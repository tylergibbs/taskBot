
from telegram import (
   Message,
   Bot,
   CallbackQuery,
   InlineKeyboardButton, 
   InlineKeyboardMarkup,
   ParseMode
)
from telegram.error import BadRequest
#from telegram.ext import ()
from bot_config import *
from bot_logging import *
import string

def createControlMsg(name: string, description: string, msg: Message) -> tuple[int, int]:
    """creates the control message to respond to a task creation request with

    name: string - name of task 
    description: string - description of task 
    msg: Message - message to be replied to

    returns the telegram ids of the control message and the chat
    """

    #buttons
    keyboard = [[   
            InlineKeyboardButton("Close Task", callback_data='1'),
            InlineKeyboardButton("Finish Task", callback_data='2'),
            InlineKeyboardButton("Cancel Task", callback_data='3'),
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    #send control message
    sentMsg = msg.reply_text(TELEGRAM_MSG_CTRL.format(name, description), 
                             reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
    return sentMsg.message_id, sentMsg.chat.id


def createVolunteerMsg(name: string, description: string, size: int, urgency: int, volunteerChat: int, bot: Bot) -> int:
    """creates a message requresing volunteers for a task
    name: string - name of task
    description: string - description of task
    size: int - recomended number of volunteers
    urgency: int - number of red flags added to message indicating urgency
    volunteerChat: int - id of chat to send message
    bot: Bot - telegram bot to send message
    
    returns the id of the volunteer message
    """

    #accsept button
    keyboard = [[  
            InlineKeyboardButton("Accsept Task", callback_data='4'),
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    #construct message
    msg = TELEGRAM_MSG_VOL.format(name,description)
    if size < 1000:
       msg+= TELEGRAM_MSG_SIZE.format(size)
    for i in range(urgency):
        msg += TELEGRAM_MSG_URG

    #send volunteer message
    sentMsg = bot.sendMessage(chat_id=volunteerChat, text=msg,
            reply_markup=reply_markup,  parse_mode=ParseMode.MARKDOWN)
   
    return sentMsg.message_id

def setUpNewChannel(name: string, description: string, channelId: int, bot: Bot) -> None:
    """sends a message sperating the messages about the previous task assigned to this chat from new messages
    also states name and description of new task assigned to chat
    name: string - name of new task
    description: string - description of new task
    channelId: int - id of channel to setup
    bot: Bot - bot that will send the message
    """ 
    bot.sendMessage(channelId, TELEGRAM_MSG_NEW_TASK_CHAT.format(name, description), parse_mode=ParseMode.MARKDOWN)


def addPersonToGroup(name: str, telegramId: int, channel: int, bot: Bot) -> None:
    """issues an invite to the volunteer to the channel
    person: string - name of person to invite
    channel: int - chat id to send invite to
    bot: Bot - bot to send invite 
    """
    #inform group of new member
    msg = bot.sendMessage(channel, TELEGRAM_MSG_NEW_VOLUNTEER.format(name))
    #send invite
    bot.sendMessage(telegramId, msg.chat.create_invite_link().invite_link)

def invalidTask(msg: Message) -> None:
    """reply to an invalid task request with error message
    msg: Message -  incorect task request to be replied to
    """
    message.reply_text("Error creating task\n" + msg)
    logging.info("Error creating task\n" + msg)

def sendHelpMsg(msg: Message) -> None:
    """sends a message describing bot behavior"""
    msg.reply_text(TELEGRAM_MSG_HELP)

def clearChat(key: int, members: list, bot: Bot) -> None:
    """kicks all members from a chat
    key: int - 
    members : list -
    bot: Bot -
    """
    chat = bot.sendMessage(key, "Closing Channel").chat
    for member in members:
       try:
          chat.kick_member(member)
       except BadRequest as err:
          print(err)
       logging.info("chat cleared")
    else:
       logging.info("chat already cleared")

def replyChatId(message: Message) -> None:
    """sends a message of the chat telegram id
    message: Message - the message to reply to
    """
    message.reply_text("This Chat id is: " + str(message.chat.id))

def finishTaskMsg(volunteerMsgId: int, volunteerChatId: int, query: CallbackQuery) -> None:
    """edits the control and volunteer messages to reflect that the task is finished
    volunteerMsgId: int - the message id of the volunteer message 
    query: CallbackQuery - query from control message clicking finish task
    """
    #edits control message and removes all buttons
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_FINISH)

    #removes accsept button from volunteer message
    try:
       query.bot.edit_message_reply_markup(volunteerChatId, volunteerMsgId)
    except:
       #if does not change will through error
       pass

def cancelTaskMsg(volunteerMsgId: int, volunteerChatId: int, query: CallbackQuery) -> None:
    """edits the control and volunteer messages to reflect that the task is cancelled
    volunteerMsgId: int - the message id of the volunteer message 
    query: CallbackQuery - query from control message clicking cancel task
    """
    #edits control message and removes all buttons
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_CANCEL)

    #removes accsept button from volunteer message
    query.bot.edit_message_reply_markup(volunteerChatId, volunteerMsgId)

def closeTaskMsg(volunteerMsgId: int, volunteerChatId: int, query: CallbackQuery) -> None:
    """edits the control and volunteer messages to reflect that the task is closed
    volunteerMsgId: int - the message id of the volunteer message 
    query: CallbackQuery - query from control message clicking close task
    """
    #edits control message and removes close button
    keyboard = [[
            InlineKeyboardButton("Finish Task", callback_data='2'),
            InlineKeyboardButton("Cancel Task", callback_data='3'),
        ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text=query.message.text + TELEGRAM_MSG_APPEND_CLOSED, reply_markup = reply_markup)
    
    #removes accsept button from volunteer message
    query.bot.edit_message_reply_markup(volunteerChatId, volunteerMsgId)

def acceptTaskMsg(name: string, usrTelegram: int, channel: int, query: CallbackQuery) -> None:
    """updates volunteer message to reflect that a user has been added to the task
    or updates why that cant be done
    added the volunteer the the task chat
    
    name: string - name of user added to task
    usrTelegram: int - telegram of user added to task
    channel: int - chat id to add user to
    query: CallbackQuery - query from volunteer message
    """
    if name:
       msg = query.message.text + "\n" + name + " has accepted"
       query.edit_message_text(text=msg, reply_markup= query.message.reply_markup)
       addPersonToGroup(name, usrTelegram, channel, query.bot)
    else:
       if usrTelegram:
          if channel:
             query.message.reply_text(TELEGRAM_MSG_DUPLICATE_USR_TASK)
             logging.warn(TELEGRAM_MSG_DUPLICATE_USR_TASK)    
          else: 
             query.message.reply_text(TELEGRAM_MSG_UNKNOWN_USR_TASK)
             logging.warn(TELEGRAM_MSG_UNKNOWN_USR_TASK)    


def msgAssigner(fmtStr: string, name: string, chatId, telegramId: int, msg: Message) -> None:
    """forward a messed to the task assigner
    fmtStr string, task dict, msg: Message
    TODO update to new structure
    """
    #TODO hide number from user
    msg.bot.sendMessage(telegramId, fmtStr.format(chatId, name, msg.text[4:]), parse_mode=ParseMode.MARKDOWN)


def fwdResponce(msg: Message) -> None:
    """forwards reply to associated chat
    reply: Message - message to send to task chat
    """
    reply = msg.reply_to_message 
    if reply:
       msgs = reply.text.split('\n')
       #ensures is an ask message
       if len(msgs) > 0:
          #associated chat number is first number in message
          #eg text = "-128323728\nthe rest of the message"
          id = msgs[0]
          if id[1:].isdigit():
             #TODO make this reply to the group msg /ask
             reply.bot.sendMessage(id, "Reply: " + msg.text)



