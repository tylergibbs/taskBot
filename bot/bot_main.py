from bot.bot_logging import logging
from telegram import ()
from telegram.ext import ()

def newTask(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    if (0>update.message.chat.id):
       invalidTask("/newTasks must be called from a direct message to the bot", update, context); 
    else:
       msg = update.message.text
       args = msg.split("|")

       if(len(args) < 2):
            invalidTask("Invalid Syntax /newTask|name|desc|?addTo|?urgency|?max size", update, context); 
       else:
         name = args[1]
         desc = args[2]
         addToGroup = False
         urgency = 0
         size = 1000
         if (len(args) > 3):
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

         msg = update.message
         bot = msg.bot
         usr = getVolunteer(msg.from_user.id)
         if (usr):
            volunteerMsgId = createVolunteerMsg(name, description, msg)
            controlMsgId, controlChatId = createControlMsg(name, description, msg)
            channel = assignNewChannel()
            setUpNewChannel(name, description, channel['fields']['Key'], bot)
            if(addToGroup):
               addPersonToGroup(usr['fields']['Telegram Channel Id'], channel['fields']['Key'], bot)
            createTaskEntry(name, description, urgency, size, usr['id'], channel['fields']['Record'],
                            volunteerMsgId, controlMsgId, controlChatId)
         else:
            invalidTask("You are not registered to create Tasks", update, context);

def help(update: Update, context: CallbackContext) -> None:
    sendHelpMsg(update.message)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    data = query.data
    match data:
        case '1':
           closeTask(query)
        case '2':
           finishTask(query)
        case '3':
           cancellTask(query)
        case '4':
           acceptTask(query)

def closeTask(query: Update) -> None:
    task = updateTask('Close', query.message.message_id)
    closeTaskMsg(task['fields']['Ask Msg Id'], query)

def finishTask(query: Update) -> None:
    task = updateTask('Done', query.message.message_id)
    finishTaskMsg(task['fields']['Ask Msg Id'], query)
    clearChat(update, task)

def cancelTask(query: Update) -> None:
    task = updateTask('Cancelled', query.message.message_id)
    cancelTaskMsg(task['fields']['Ask Msg Id'], query)
    clearChat(update, task)

def acceptTask(query: Update) -> None:
    usr, task = addPersonToTask(query.from_user.id)
    acceptTaskMsg(usr['fields']["Name (all)"], usr['fields']['Telegram Channel Id'], task['fields']['Key'][0], query)

def register(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(registerUser(update.message.text))

def ask(update: Update, context: CallbackContext) -> None:
    msg = update.message
    task = getTaskByChat(msg.chat.id)
    if task:
        msgAssigner(TELEGRAM_MSG_FWD_ASK, task, msg)

def finish(update: Update, context: CallbackContext) -> None:
    msg = update.message
    task = getTaskByChat(msg.chat.id)
    if task:
        msgAssigner(TELEGRAM_MSG_FWD_FNSH, task, msg)

def respond(update: Update, context: CallbackContext) -> None:
    fwdResponce(update.message.reply_to_message)

def chatId(update: Update, context: CallbackContext) -> None:
    replyChatId(update.message.chat.id)

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
    dispatcher.add_handler(CommandHandler("register", registerUser))
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
