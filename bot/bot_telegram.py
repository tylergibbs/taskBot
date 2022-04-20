
from telegram import ()
from telegram.ext import ()


def createControlMsg(name: string, description: string, msg: Message): -> int, int:
    keyboard = [[   
            InlineKeyboardButton("Close Task", callback_data='1'),
            InlineKeyboardButton("Finish Task", callback_data='2'),
            InlineKeyboardButton("Cancel Task", callback_data='3'),
        ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    sentMsg = update.message.reply_text(TELEGRAM_MSG_CTRL.format(name, description), 
                             reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return sentMsg.message_id, sentMsg.chat.id


def createVolunteerMsg(name: string, description: string, size: int, urgency: int, volunteerChat: int, bot: Bot):
    keyboard = [[  
            InlineKeyboardButton("Accsept Task", callback_data='4'),
        ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = TELEGRAM_MSG_VOL.format(name,description)
    if size < 1000:
       msg+= TELEGRAM_MSG_SIZE.format(size)

    for i in range(urgency):
        msg += TELEGRAM_MSG_URG

    sentMsg = context.bot.sendMessage(chat_id=volunteerChat, text=msg,
            reply_markup=reply_markup,  parse_mode=ParseMode.MARKDOWN)
   
    return sentMsg.message_id

def setUpNewChannel(name: string, description: string, channelId: int, bot: Bot)
    bot.sendMessage(channelId, TELEGRAM_MSG_NEW_TASK_CHAT.format(name, description), parse_mode=ParseMode.MARKDOWN)


#def assignOpenChat(name: string, desciption: string, channel: int, bot: Bot) -> Chat:
 #      return bot.sendMessage(channel, TELEGRAM_MSG_NEW_TASK_CHAT.format(name, desciption),
  #                     parse_mode=ParseMode.MARKDOWN)

def addPersonToGroup(person: dict, channel: int, bot: Bot):
    msg = bot.sendMessage(channel, TELEGRAM_MSG_NEW_VOLUNTEER.format(person['fields']['Name']))
    bot.sendMessage(person, msg.chat.create_invite_link().invite_link)

def invalidTask(msg, update):
    update.message.reply_text("Error creating task\n" + msg)
    logging.info("Error creating task\n" + msg)

def sendHelpMsg(msg: Message) -> None:
    msg.reply_text(TELEGRAM_MSG_HELP)

def clearChat(update, task):
    if('Key' in task['fields']):
       key = task['fields']['Key']
       chat = update.callback_query.bot.sendMessage(key[0], "Closing Channel").chat
       try:
          chat.kick_member(task['fields']['Assigned By Telegram'][0])
       except telegram.error.BadRequest as err:
          logging.info(err)
       if 'Assigned To' in task['fields']:
          for member in task['fields']['Assigned To Telegram Channel']:
             try:
                chat.kick_member(member)
             except telegram.error.BadRequest as err:
                print(err)
       unassignChannel(key)
       logging.info("chat cleared")
    else:
       logging.info("chat already cleared")

def replyChatId(chatId: int) -> None:
    update.message.reply_text("This Chat id is: " + str(chatId))

def finishTaskMsg(volunteerMsgId: int, query: Query): -> None:
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_FINISH)
    query.bot.edit_message_reply_markup(getVolunteerChatId(), volunteerMsgId)

def cancelTaskMsg(volunteerMsgId: int, query: Query): -> None:
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_CANCEL)
    query.bot.edit_message_reply_markup(getVolunteerChatId(), volunteerMsgId)

def closeTaskMsg(volunteerMsgId: int, query: Query): -> None:
    keyboard = [[
            InlineKeyboardButton("Finish Task", callback_data='2'),
            InlineKeyboardButton("Cancel Task", callback_data='3'),
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_CLOSED, reply_markup = reply_markup)
    query.bot.edit_message_reply_markup(getVolunteerChatId(), volunteerMsgId)

def acceptTaskMsg(name,usrTelegram, channel, query):
    if name:
       msg = update.callback_query.message.text + "\n" + str(usr['fields']["Name (all)"]) + " has accepted"
       query.edit_message_text(text=msg, reply_markup=update.callback_query.message.reply_markup)
       addPersonToGroup(usrTelegram, channel, query.bot)
     else:
       if usrTelegram:
          if channel:
             query.message.reply_text(TELEGRAM_MSG_DUPLICATE_USR_TASK)
             logging.warn(TELEGRAM_MSG_DUPLICATE_USR_TASK)    
          else: 
             query.message.reply_text(TELEGRAM_MSG_UNKNOWN_USR_TASK)
             logging.warn(TELEGRAM_MSG_UNKNOWN_USR_TASK)    


def msgAssigner(fmtStr, task, msg):
    #TODO hide number from user
    update.message.bot.sendMessage(task['fields']['Assigned By Telegram'][0], 
           fmtStr.format(msg.chat.id,task['fields']['Name'],update.message.text[4:]),
           parse_mode=ParseMode.MARKDOWN)

def fwdResponce(reply: Message): -> None:
    if reply:
       msgs = reply.text.split('\n')
       if len(msgs) > 0:
          id = msgs[0]
          if id[1:].isdigit():
             #TODO make this reply to the group msg /ask
             reply.bot.sendMessage(id, "Reply: " + update.message.text)



