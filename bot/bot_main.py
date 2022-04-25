
from telegram import (Update,ParseMode)
from telegram.ext import (
   Updater,
   CommandHandler,
   MessageHandler,
   Filters,
   CallbackContext,
   CallbackQueryHandler
)

from bot_airtable import *
from bot_telegram import *
from bot_config import *
from bot_logging import logging

#TODO migrate strings to config file are rething invalid task wording
def newTask(update: Update, context: CallbackContext) -> None:
    """handles call to create a new task with /newTask|name|desc|?addTo|?urgency|?max size
    update must have a message
    context is discarded
    """
    #verify the message comes from a direct message
    if (0>update.message.chat.id):
       invalidTask("/newTasks must be called from a direct message to the bot", update, context); 
    else:
       #Parse message string into variables
       msg = update.message.text
       args = msg.split("|")

       #verify string has required args
       if(len(args) < 2):
            invalidTask("Invalid Syntax /newTask|name|desc|?addTo|?urgency|?max size", update, context); 
       else:
         name = args[1]
         description = args[2]

         #initialize default values of optional args
         addToGroup = False
         urgency = 0
         size = 1000

         #assign optional args if pressent
         if (len(args) > 3):
           #arg3 is case insensitive
           addToGroup = args[3].lower()
           if addToGroup in ('true','t'):
               addToGroup = True
           elif addToGroup in ('false','f'):
               addToGroup = False
           else:
               invalidTask("addToGroup value must be true or t or false or f", update, context)
               return
           if (len(args) > 4):
             urgency = args[4]
             if (urgency in ['0', '1','2','3','4']):
                urgency = int(urgency)
             else:
                invalidTask("urgency must be 0-4", update, context)
                return
             if(len(args) > 5):
               size = args[5]
               if (size.isdigit()):
                 size = int(size)
               else:
                 invalidTask("max size must be an integer", update, context)
                 return
         #actualy create the task
         msg = update.message
         bot = msg.bot
         usr = getVolunteer(msg.from_user.id)
         volunteerChat = getVolunteerChat()
         #verify user exists in database
         #TODO some way to verify if user can assign tasks
         if (usr):

            #telegram updates for task
            volunteerMsgId = createVolunteerMsg(name, description, size, urgency, volunteerChat, bot)
            controlMsgId, controlChatId = createControlMsg(name, description, msg)
            channel = assignNewChannel()
            setUpNewChannel(name, description, channel['fields']['Key'], bot)

            #add the assigner to the task group chat if flag set
            if(addToGroup):
               addPersonToGroup(usr['fields']['Telegram Channel Id'], channel['fields']['Key'], bot)

            #create airtable row
            createTaskEntry(name, description, urgency, size, usr['id'], channel['id'],
                            volunteerMsgId, controlMsgId, controlChatId)
         else:
            invalidTask("You are not registered to create Tasks", update, context);


def button(update: Update, context: CallbackContext) -> None:
    """handles all button press responces
    each botton has a number saved in update.callback_query.data
    that will designate the behavor called"""

    query = update.callback_query

    #some telegram clients need querys to be answered even if blank
    query.answer()

    #choose bahavor executed
    #TODO change numbers to more descriptive strings
    data = query.data
    match data:
        case '1':
           closeTask(query)
        case '2':
           finishTask(query)
        case '3':
           cancelTask(query)
        case '4':
           acceptTask(query)

def closeTask(query: CallbackQuery) -> None:
    """chages the airtable task status to closed,
    removes the 'close' button from the controlMessage
    and removes the accsept task button from the volunteerMessage
    """
    task = updateTask('Closed', query.message.message_id)
    closeTaskMsg(task['fields']['Ask Msg Id'], getVolunteerChat(), query)

def finishTask(query: CallbackQuery) -> None:
    """chages the airtable task status to finished,
    removes buttons from the controlMessage
    removes the accsept task button from the volunteerMessage
    and removes all volunteers from the task chat
    """
    task = updateTask('Done', query.message.message_id)

    key = task['fields']['Key'][0]
    members = []
    if 'Assigned To Telegram Channel' in task['fields']:
       members.extend(task['fields']['Assigned To Telegram Channel'])
    members.append(task['fields']['Assigned By Telegram'][0])

    finishTaskMsg(task['fields']['Ask Msg Id'], getVolunteerChat(), query)
    clearChat(key, members, query.bot)
    unassignChannel(key)

def cancelTask(query: CallbackQuery) -> None:
    """chages the airtable task status to cancelled,
    removes buttons from the controlMessage
    removes the accsept task button from the volunteerMessage
    and removes all volunteers from the task chat
    """
    task = updateTask('Cancelled', query.message.message_id)

    key = task['fields']['Key'][0]
    members = []
    if 'Assigned To Telegram Channel' in task['fields']:
       members.extend(task['fields']['Assigned To Telegram Channel'])
    members.append(task['fields']['Assigned By Telegram'][0])

    cancelTaskMsg(task['fields']['Ask Msg Id'], getVolunteerChat(), query)
    clearChat(key, members, query.bot)
    unassignChannel(key)

def acceptTask(query: CallbackQuery) -> None:
    """adds the clicking user to the task in airtable,
    adds the user to the task group
    and updates volunteer and control messages to reflect this
    """
    usr, task = addPersonToTask(query.message.message_id, query.from_user.id)
    if task:
       if usr:
          acceptTaskMsg(usr['fields']["Name (all)"], usr['fields']['Telegram Channel Id'], task['fields']['Key'][0], query)
       else:
          query.message.reply_text("last applicant is not registered")
    else:
       query.message.reply_text("task is closed")

def ask(update: Update, context: CallbackContext) -> None:
    """called from within a task chat
    /ask [question or update]
    sends the [question or update] as a dm to the assigner
    to allow limited comunication between assigner and volunteers
    without them having to be in the chat
    assigner may respond to the message by replying in there dms
    """
    msg = update.message
    task = getTaskByChat(msg.chat.id)
    if task:
        msgAssigner(TELEGRAM_MSG_FWD_ASK, task['fields']['Name'], 
                    task['fields']['Key'][0], task['fields']['Assigned By Telegram'][0], msg)

def finish(update: Update, context: CallbackContext) -> None:
    """called from within a task chat
    /finish ?[message]
    sends the [message] and a not indicating the volunteer beleives the tasj is done
    as a dm to the assigner
    does not allow the assigner to respond
    """
    msg = update.message
    task = getTaskByChat(msg.chat.id)
    if task:
        msgAssigner(TELEGRAM_MSG_FWD_FNSH, task, msg)

def respond(update: Update, context: CallbackContext) -> None:
    """to handle all replys to bot messages
    at this time only forwards replys to /ask dms
    to the task chat
    """
    fwdResponce(update.message)

def register(update: Update, context: CallbackContext) -> None:
    """adds a users telegram id to their airtablel entry
    /register [name]
    name must be the same in the airtable entry
    """
    update.message.reply_text(registerUser(update.message.text, update.message.from_user.id))

def chatId(update: Update, context: CallbackContext) -> None:
    """returns the id of the chat, used for debug"""
    replyChatId(update.message.chat.id)

def helpCommand(update: Update, context: CallbackContext) -> None:
    """responds with an explanation of the bot"""
    sendHelpMsg(update.message)

def main() -> None:
    #TODO use WebHooks
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    dispatcher.add_handler(CommandHandler("newTask", newTask))
    dispatcher.add_handler(CommandHandler("help", helpCommand))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("finish", finish))
    dispatcher.add_handler(CommandHandler("ask", ask))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))
    dispatcher.add_handler(CommandHandler("chatId", chatId))
    dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
