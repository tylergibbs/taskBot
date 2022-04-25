from pyairtable import Table
from pyairtable.formulas import match
from bot_config import *
import string

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
    record = peopleTable.first(formula = match({'Name (all)':name}))

    #if a volunteer is found add the telegram id to them
    if record:
       fields = {"Telegram Id" : usrId,
                 "Telegram Channel Id": usrId,
                 "Has Telegram": True}
       peopleTable.update(record['id'], fields)
       #TODO move strings to config file
       return "Telegram succsesfuly registered"
    else:
       return "You dont exist\nMore likely the name entered does not match our records"

def assignNewChannel() -> dict:
    """gets the airtable entry of the next open channel
    and marks it as in use
    """
    #get open channel
    channel = channelTable.first(formula=match({'Uses':'Tasks','In Use':False}))
    if(channel):
       #mark channel as in use
       newChannelProj = channelTableProj.first(formula=match({'Key':channel['fields']['Key']}))
       channelTable.update(channel['id'], {"In Use":True})
       return newChannelProj
    else:
       #TODO proper error handeling
       raise "all channels in use"

def unassignChannel(channelKey: int) -> None:
    """mark channel as free
    channelKey: int - the id of the channel to mark as free
    """
    channel = channelTable.first(formula=match({'Key':channelKey,'Uses':'Tasks','In Use':True}))
    channelTable.update(channel['id'], {"In Use":False})


def createTaskEntry(name: string, description: string, urgency: int, size: int, assigner: int, taskChannel: string,
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

    taskTable.create({"Name": name, "Description":description, "Assigned By": [assigner],
                      "Status": "Open",
                      "Task Channel": [taskChannel],
                      "Ask Msg Id": volunteerMsg,
                      "Control Msg Id": assignerMsgId,
                      "Control Msg Channel": assignerChatId,
                      "Urgency": urgency, "Max People": size})

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
    newFields = {"Status":status}
    #if task is over remove all volunteers and unassin the channel
    if status != "Closed":
       newFields["Assigned To"]=[]
       newFields["Task Channel"]=[]
    
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
    task = getTaskFromVolMsg(msgId)

    #verify task is open
    if task['fields']['Status'] == 'Open':
       #verify user is registerred
       if usr:
          assignedTo = []
          
          #if task has any already assigned to it keep them
          if("Assigned To" in task['fields']):
             assignedTo.extend(task['fields']["Assigned To"])

          #if user is already assigned to task do nothing
          if(not (usr["id"] in assignedTo)):
             assignedTo.append(usr["id"])

             taskTable.update(task["id"], {"Assigned To":assignedTo})

             return usr, task
          else:
             return None, task
       else:
          return None, task
    else:
       logging.warn(LOG_TASK_CLOSED_WARN)
       return None, None

def getVolunteer(telegram_id: int) -> dict:
    return peopleTable.first(formula=match({"Telegram Id":telegram_id}))

def getTaskFromControl(msgId: int) -> dict:
    return taskTable.first(formula=match({"Control Msg Id":msgId}))

def getTaskFromVolMsg(msgId: int) -> dict:
    return taskTable.first(formula=match({"Ask Msg Id":msgId}))

def getTaskByChat(chatId: int) -> dict:
    return taskTable.first(formula=match({"Key":chatId}))

def getVolunteerChat() -> int:
    return channelTable.first(formula=match({"Uses":"Volunteer"}))['fields']['Key']


