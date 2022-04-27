import os
from telegram import InlineKeyboardButton
API_KEY = 'key2CxuYxgIZfkTyn'
SYSTEM_BASE_ID = 'apptfBjXj7dxpk5HW'
AUTOMATION_BASE_ID = 'appmOOhjEJeipDKf1'

TASKS = 'tblICYQhXDfZIl3pz'
AUTOCHANNELS = 'tblmouCE89kNazlUG'
TASKCHANNELS = 'Task Channels'
PEOPLE = 'tblgPoXrj1hqh7PI3'

TELEGRAM_TOKEN = '5185995033:AAEV7YQqaM9dEQNeN0_axhd4psc4GiCMy_s'

TELEGRAM_MSG_HELP = "This bot has the following commands\n"
TELEGRAM_MSG_HELP+= "variables are in []\n\n"
TELEGRAM_MSG_HELP+= "/register [name in airtable]\n"
TELEGRAM_MSG_HELP+= "message the bot directly(not in a group) to register your telegram to your name\n\n"
TELEGRAM_MSG_HELP+= "/newTask [task name] [recomended size] [description]\n"
TELEGRAM_MSG_HELP+= "message the bot directly(not in a group) to create a task after registering\n"
TELEGRAM_MSG_HELP+= "task name must not have spaces within it, use underscores instead\n"
TELEGRAM_MSG_HELP+= "this will create a request for volunteers in the volunteer chat and will reply with a control message "
TELEGRAM_MSG_HELP+= "that allows the creator to close the task to new volunteers, cancel the task, or declare it complete\n\n"
TELEGRAM_MSG_HELP+= "/ask [message]\n"
TELEGRAM_MSG_HELP+= "after the task channel is created volunteers may type /ask to send a msg to directly to the task assigner "
TELEGRAM_MSG_HELP+= "after which the assigner may reply to that message (not just type into the chat reply to the message) and "
TELEGRAM_MSG_HELP+= "it will be forwarded back to the chat\n\n"
TELEGRAM_MSG_HELP+= "/finish ?[message]\n"
TELEGRAM_MSG_HELP+= "when the volunteer thinks a task is done they may use /finish to notify the assigner with an optional message"

TELEGRAM_MSG_NEW_TASK_CHAT = "Old Chat\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n New Task Assigned\n*{0}*\n{1}\n\n"

TELEGRAM_MSG_NEW_VOLUNTEER = "adding new volunteer: {}"

TELEGRAM_MSG_ASSIGNER = "adding assigner: {}"

TELEGRAM_MSG_APPEND_CANCEL = "\nTask is Canceled."

TELEGRAM_MSG_APPEND_FINISH = "\nTask is Done."

TELEGRAM_MSG_APPEND_CLOSED = "\nTask is Closed."

TELEGRAM_MSG_DUPLICATE_USR_TASK = "The telegram of the last person to attempt to register with this task is not in our records"

TELEGRAM_MSG_UNKNOWN_USR_TASK = "The telegram of the last person to attempt to register with this task is not in our records"

TELEGRAM_MSG_FWD_ASK = "{0}\nmessage from task *{1}*:\n {2}"

TELEGRAM_MSG_FWD_FNSH = "*{1}* is claimed tobe finished:\n {2}"

TELEGRAM_MSG_CTRL = "Created Task *{}*\n{}"

TELEGRAM_MSG_VOL = "New Task Request *{}* \n{}\n"

TELEGRAM_MSG_SIZE = "requested members: {}\n"

TELEGRAM_MSG_INVALID_TASK_SYNTAX = "Invalid Syntax /newTask [name] [size] [task description]"

TELEGRAM_MSG_INVALID_TASK_SIZE = "[size] must be an integer"

TELEGRAM_MSG_INVALID_TASK_CHAT = "/newTasks must be called from a direct message to the bot"

TELEGRAM_MSG_INVALID_TASK_USER = "You are not registered to create Tasks"

TELEGRAM_MSG_USR_NOT_REGISTERED = "last applicant is not registered"

TELEGRAM_MSG_REGISTER_GOOD = "Telegram succsesfuly registered"

TELEGRAM_MSG_REGISTER_BAD = "You dont exist\nMore likely the name entered does not match our records"

TELEGRAM_MSG_ALL_CHANNELS = "all channels in use"

TELEGRAM_MARKUP_CLOSE = '1'

TELEGRAM_MARKUP_DONE = '2'

TELEGRAM_MARKUP_CANCEL = '3'

TELEGRAM_MARKUP_ACCSEPT = '4'

TELEGRAM_MARKUP_ADD_TO = '5'

TELEGRAM_BUTTON_CLOSE = InlineKeyboardButton("Close Task", callback_data=TELEGRAM_MARKUP_CLOSE)

TELEGRAM_BUTTON_DONE = InlineKeyboardButton("Finish Task", callback_data=TELEGRAM_MARKUP_DONE)

TELEGRAM_BUTTON_CANCEL = InlineKeyboardButton("Cancel Task", callback_data=TELEGRAM_MARKUP_CANCEL)

TELEGRAM_BUTTON_ACCSEPT = InlineKeyboardButton("Accsept Task", callback_data=TELEGRAM_MARKUP_ACCSEPT)

TELEGRAM_BUTTON_ADD_TO = InlineKeyboardButton("Add Me To Chat", callback_data=TELEGRAM_MARKUP_ADD_TO)

AIRTABLE_FIELD_PEOPLE_TELEGRAM = 'Telegram Id'

AIRTABLE_FIELD_PEOPLE_HAS_TELEGRAM = 'Has Telegram'

AIRTABLE_FIELD_PEOPLE_NAME = 'Name (all)'

AIRTABLE_FIELD_TASK_NAME = 'Name'

AIRTABLE_FIELD_TASKS_DESCRIPTION = "Description"

AIRTABLE_FIELD_TASKS_ASSIGNER = "Assigned By"

AIRTABLE_FIELD_TASKS_ASSIGNER_TELEGRAM = "Assigned By Telegram"

AIRTABLE_FIELD_TASKS_VOLUNTEERS = "Assigned To"

AIRTABLE_FIELD_TASKS_VOLUNTEER_TELEGRAMS = "Assigned To Telegram Channel"

AIRTABLE_FIELD_TASKS_STATUS = "Status"

AIRTABLE_FIELD_TASKS_CHANNEL = "Task Channel"

AIRTABLE_FIELD_TASKS_CHANNEL_ID = "Key"

AIRTABLE_FIELD_CHANNEL_ID = "Key"

AIRTABLE_FIELD_CHANNEL_USED = "In Use"

AIRTABLE_FIELD_CHANNEL_USES = "Uses"

AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE = "Ask Msg Id"

AIRTABLE_FIELD_TASKS_CONTROL_MESSAGE = "Control Msg Id"

AIRTABLE_FIELD_TASKS_CONTROL_MESSAGE_CHANNEL = "Control Msg Channel"

AIRTABLE_FIELD_TASKS_ASSIGNER_CHANNEL = "Assigner Channel"

AIRTABLE_FIELD_TASKS_SIZE = "Max People"

LOG_PATH = None#"./logfile"

LOG_TASK_CLOSED_WARN = "trying to add person to closed task"

LOG_USR_ALREADY_IN_TASK_WARN = "trying to add duplicate person to task"
