from pyairtable import Table
from pyairtable.formulas import match
from bot_config import *
import string
from bot_logging import *

taskTable = 		Table(API_KEY, SYSTEM_BASE_ID, 	  TASKS)
channelTable = 		Table(API_KEY, AUTOMATION_BASE_ID, AUTOCHANNELS)
channelTableProj = 	Table(API_KEY, SYSTEM_BASE_ID, 	TASKCHANNELS)
peopleTable = 		Table(API_KEY, SYSTEM_BASE_ID, 	PEOPLE)


def registerUser(text: string, usrId: int) -> string:
    """adds the telegram id from message to the airtable
    entry of the person named in the message
    returns the string to message back indicating succsess or failure
    """
    #parses out the name
    name = " ".join(text.split(" ")[1:])
    
    #get the entry of the volunteer with the name ubove
    #TODO throw error if multibe people with name?
    record = peopleTable.first(formula = match({AIRTABLE_FIELD_PEOPLE_NAME:name}))

    #if a volunteer is found add the telegram id to them
    if record:
       fields = {AIRTABLE_FIELD_PEOPLE_TELEGRAM : usrId,
                 AIRTABLE_FIELD_PEOPLE_HAS_TELEGRAM : True}
       peopleTable.update(record['id'], fields)
       #TODO move strings to config file
       return TELEGRAM_MSG_REGISTER_GOOD
    else:
       return TELEGRAM_MSG_REGISTER_BAD

def assignNewChannel() -> dict:
    """gets the airtable entry of the next open channel
    and marks it as in use
    """
    #get open channel
    channel = channelTable.first(formula=match({'Uses':'Tasks','In Use':False}))
    if(channel):
       #mark channel as in use
       newChannelProj = channelTableProj.first(formula=match({
                        AIRTABLE_FIELD_TASKS_CHANNEL_ID:channel['fields'][AIRTABLE_FIELD_CHANNEL_ID]}))
       channelTable.update(channel['id'], {AIRTABLE_FIELD_CHANNEL_USED:True})
       return newChannelProj
    else:
       #TODO proper error handeling
       raise TELEGRAM_MSG_ALL_CHANNELS

def unassignChannel(channelKey: int) -> None:
    """mark channel as free
    channelKey: int - the id of the channel to mark as free
    """
    channel = channelTable.first(formula=match({'Key':channelKey,'Uses':'Tasks','In Use':True}))
    channelTable.update(channel['id'], {AIRTABLE_FIELD_CHANNEL_USED:False})


def createTaskEntry(name: string, description: string, size: int, assigner: int, taskChannel: string,
                    volunteerMsg: int, assignerMsgId: int, assignerChatId: int) -> None:
    """creates a new task entry in airtable from the avalible information
    name: string - name of task
    description: string - description of task
    urgency: int - 0-4 visual indication of urgency
    size: int - recomended number of volunteers, only used for display
    assigner: int - telegram id of the assigner
    taskChannel: string - telegram id of the task chat assigned to the volunteers
    volunteerMsg: int - id of the message requresting volunteers
    assignerMsgId: int - id of the control message
    assignerChatId: int - id of the chat the control message is in
    """

    taskTable.create({AIRTABLE_FIELD_TASK_NAME: name, 
                      AIRTABLE_FIELD_TASKS_DESCRIPTION:description, 
                      AIRTABLE_FIELD_TASKS_ASSIGNER: [assigner],
                      AIRTABLE_FIELD_TASKS_STATUS: "Open",
                      AIRTABLE_FIELD_TASKS_CHANNEL: [taskChannel],
                      AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE: volunteerMsg,
                      AIRTABLE_FIELD_TASKS_CONTROL_MESSAGE: assignerMsgId,
                      AIRTABLE_FIELD_TASKS_CONTROL_MESSAGE_CHANNEL: assignerChatId,
                      AIRTABLE_FIELD_TASKS_SIZE: size})

def updateTask(status: string, msgId: int)-> dict:
    """updates the status of a task to the given status, if
    the new status is Done or Finished also removes assigned volunteers
    from the task
    status: string - new status of task must be "Done" "Finished" or "Closed"
    msgId: int - telegram id of the control message
    
    returns the old task while unintuitive this works better in the workflow 
    """
    #get the task conected to the control message
    task = getTaskFromControl(msgId)
    
    #build dictionary with fields to update
    newFields = {AIRTABLE_FIELD_TASKS_STATUS:status}
    #if task is over remove all volunteers and unassin the channel
    if status != "Closed":
       newFields[AIRTABLE_FIELD_TASKS_VOLUNTEERS]=[]
       newFields[AIRTABLE_FIELD_TASKS_CHANNEL]=[]
    
    #update the airtable entry with newFields
    taskTable.update(task['id'], newFields)

    #returns the old taask
    return task

def addPersonToTask(msgId:int, telegramId:int) ->  tuple[dict, dict]:
    """adds the volunteer that clicked the button in query to the task conected
    with the volunteer message that sent query

    msgId: int - volunteer message id assciated with task to update
    
    returns the airtable task entry and the airtable user entry
    """

    #gets the associated user who clicked query
    usr = getVolunteer(telegramId)

    #gets the task associated with the volunteer message that generated query
    print(str(msgId))
    print(str(msgId))
    print(str(msgId))
    print(str(msgId))
    print(str(msgId))
    task = getTaskFromVolMsg(msgId)

    #verify task is open
    print(str(task))
    print(str(task))
    print(str(task))
    print(str(task))
    print(str(task))
    if task['fields'][AIRTABLE_FIELD_TASKS_STATUS] == 'Open':
       #verify user is registerred
       if usr:
          assignedTo = []
          
          #if task has any already assigned to it keep them
          if("Assigned To" in task['fields']):
             assignedTo.extend(task['fields'][AIRTABLE_FIELD_TASKS_VOLUNTEERS])

          #if user is already assigned to task do nothing
          if(not (usr["id"] in assignedTo)):
             assignedTo.append(usr["id"])

             taskTable.update(task["id"], {"Assigned To":assignedTo})

             return usr, task
          else:
             return usr, task
       else:
          return None, Task
    else:
       logging.warn(LOG_TASK_CLOSED_WARN)
       return None, None

def getVolunteer(telegram_id: int) -> dict:
    return peopleTable.first(formula=match({AIRTABLE_FIELD_PEOPLE_TELEGRAM:telegram_id}))

def getTaskFromControl(msgId: int) -> dict:
    return taskTable.first(formula=match({AIRTABLE_FIELD_TASKS_CONTROL_MESSAGE:msgId}))

def getTaskFromVolMsg(msgId: int) -> dict:
    return taskTable.first(formula=match({AIRTABLE_FIELD_TASKS_VOLUNTEER_MESSAGE:msgId}))

def getTaskByChat(chatId: int) -> dict:
    return taskTable.first(formula=match({AIRTABLE_FIELD_TASKS_CHANNEL_ID:chatId}))

def getVolunteerChat() -> int:
    return channelTable.first(formula=match({AIRTABLE_FIELD_CHANNEL_USES:"Volunteer"}))['fields'][AIRTABLE_FIELD_CHANNEL_ID]


