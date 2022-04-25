import os

API_KEY = 'key2CxuYxgIZfkTyn'
SYSTEM_BASE_ID = 'apptfBjXj7dxpk5HW'
AUTOMATION_BASE_ID = 'appmOOhjEJeipDKf1'

TASKS = 'tblICYQhXDfZIl3pz'
AUTOCHANNELS = 'tblmouCE89kNazlUG'
TASKCHANNELS = 'Task Channels'
PEOPLE = 'tblgPoXrj1hqh7PI3'

TELEGRAM_TOKEN = '5185995033:AAEV7YQqaM9dEQNeN0_axhd4psc4GiCMy_s'

TELEGRAM_MSG_NEW_TASK_CHAT = "Old Chat\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n New Task Assigned\n*{0}*\n{1}\n\n"

TELEGRAM_MSG_NEW_VOLUNTEER = "adding new volunteer: {}"

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

TELEGRAM_MSG_URG = '\U0001F6A9'

LOG_PATH = None#"./logfile"

LOG_TASK_CLOSED_WARN = "trying to add person to closed task"

LOG_USR_ALREADY_IN_TASK_WARN = "trying to add duplicate person to task"
