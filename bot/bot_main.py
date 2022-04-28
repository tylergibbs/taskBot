
from telegram import (Update,ParseMode)
from telegram.ext import (
   Updater,
   CommandHandler,
   MessageHandler,
   Filters,
   CallbackContext,
   CallbackQueryHandler,
   Dispatcher
)

from bot_airtable import *
from bot_telegram import *
from bot_config import *
import bot_config
from bot_logging import logging

#TODO migrate strings to config file are rething invalid task wording
def newTask(update: Update, context: CallbackContext) -> None:
    """handles call to create a new task with /newTask [name] [size] [task description]
    update must have a message
    context is discarded
    """
    message = update.message
    #verify the message comes from a direct message
    if (0>update.message.chat.id):
       invalidTask(TELEGRAM_MSG_INVALID_TASK_CHAT, message); 
    else:
       #Parse message string into variables
       msg = message.text
       args = msg.split(" ")

       if len(args) < 4:
          invalidTask(TELEGRAM_MSG_INVALID_TASK_SYNTAX, message)
          return

       name = args[1]

       size = args[2]
       if(size.isdigit()):
          size = int(size)
       else:
          invalidTask(TELEGRAM_MSG_INVALID_TASK_SIZE, message)
          return

       description = " ".join(args[3:])
       
       msg = update.message
       bot = msg.bot
       usr = getVolunteer(msg.from_user.id)
       volunteerChat = getVolunteerChat()
       #verify user exists in database

       #TODO some way to verify if user can assign tasks
       if (usr):
            #telegram updates for task
            volunteerMsgId = createVolunteerMsg(name, description, size, volunteerChat, bot)
            controlMsgId, controlChatId = createControlMsg(name, description, msg)
            channel = assignNewChannel()
            setUpNewChannel(name, description, channel['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID], bot)

            #create airtable row
            createTaskEntry(name, description, size, usr['id'], channel['id'],
                            volunteerMsgId, controlMsgId, controlChatId)
       else:
            invalidTask(TELEGRAM_MSG_INVALID_TASK_USER, message);


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
        case bot_config.TELEGRAM_MARKUP_CLOSE:
           closeTask(query)
        case bot_config.TELEGRAM_MARKUP_DONE:
           finishTask(query)
        case bot_config.TELEGRAM_MARKUP_CANCEL:
           cancelTask(query)
        case bot_config.TELEGRAM_MARKUP_ACCSEPT:
           acceptTask(query)
        case bot_config.TELEGRAM_MARKUP_ADD_TO:
           addToChannel(query)

def closeTask(query: CallbackQuery) -> None:
    """chages the airtable task status to closed,
    removes the 'close' button from the controlMessage
    and removes the accsept task button from the volunteerMessage
    """
    task = updateTask('Closed', query.message.message_id)
    closeTaskMsg(task['fields'][AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE],
                 getVolunteerChat(), query)

def finishTask(query: CallbackQuery) -> None:
    """chages the airtable task status to finished,
    removes buttons from the controlMessage
    removes the accsept task button from the volunteerMessage
    and removes all volunteers from the task chat
    """
    task = updateTask('Done', query.message.message_id)

    key = task['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID][0]
    members = []
    if 'Assigned To Telegram Channel' in task['fields']:
       members.extend(task['fields'][AIRTABLE_FIELD_TASKS_VOLUNTEER_TELEGRAMS])
    members.append(task['fields'][AIRTABLE_FIELD_TASKS_ASSIGNER_TELEGRAM][0])

    finishTaskMsg(task['fields'][AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE], getVolunteerChat(), query)
    clearChat(key, members, query.bot)
    unassignChannel(key)

def cancelTask(query: CallbackQuery) -> None:
    """chages the airtable task status to cancelled,
    removes buttons from the controlMessage
    removes the accsept task button from the volunteerMessage
    and removes all volunteers from the task chat
    """
    task = updateTask('Cancelled', query.message.message_id)

    key = task['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID][0]
    members = []
    if AIRTABLE_FIELD_TASKS_VOLUNTEER_TELEGRAMS in task['fields']:
       members.extend(task['fields']['Assigned To Telegram Channel'])
    members.append(task['fields'][AIRTABLE_FIELD_TASKS_ASSIGNER_TELEGRAM][0])

    cancelTaskMsg(task['fields'][AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE], getVolunteerChat(), query)
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
          print(usr['fields'])
          print(usr['fields'])
          print(usr['fields'])
          print(usr['fields'])
          acceptTaskMsg(usr['fields'][AIRTABLE_FIELD_PEOPLE_NAME], 
                       usr['fields'][AIRTABLE_FIELD_PEOPLE_TELEGRAM], 
                       task['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID][0], query)
       else:
          query.message.reply_text(TELEGRAM_MSG_USR_NOT_REGISTERED)
    else:
       query.message.reply_text(TELEGRAM_MSG_TASK_CLOSED)

def addToChannel(query: CallbackQuery) -> None:
    """adds the user to to the group associated with the controll message
    query: CallbackQuery - a click on a controll message
    """

    #TODO remove/track button when button is clicked
    volunteer = getVolunteer(query.from_user.id)
    task = getTaskFromControl(query.message.message_id)
    addAssignerToGroup(volunteer['fields'][AIRTABLE_FIELD_PEOPLE_NAME],
             volunteer['fields'][AIRTABLE_FIELD_PEOPLE_TELEGRAM],
             task['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID][0], query.bot)

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
        msgAssigner(TELEGRAM_MSG_FWD_ASK, task['fields'][AIRTABLE_FIELD_TASK_NAME], 
                    task['fields'][AIRTABLE_FIELD_TASKS_CHANNEL_ID][0], 
                    task['fields']['Assigned By Telegram'][0], msg)

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

def setup():
    bot = Bot(TELEGRAM_TOKEN)

    dispatcher = Dispatcher(bot, None, workers=0)
    dispatcher.add_handler(CommandHandler("newTask", newTask))
    dispatcher.add_handler(CommandHandler("help", helpCommand))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("finish", finish))
    dispatcher.add_handler(CommandHandler("ask", ask))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))
    dispatcher.add_handler(CommandHandler("chatId", chatId))
    dispatcher.add_handler(CallbackQueryHandler(button))
    
    return dispatcher

dispatcher = setup()

def webhook(update):
    dispatcher.process_update(update)



if __name__ == '__main__':
    main()
