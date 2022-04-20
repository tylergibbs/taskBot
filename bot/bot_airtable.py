from pyairtable import Table
from pyairtable.formulas import match

taskTable = 		Table(APIKEY, SYSTEM_BASE_ID, 	  TASKS)
channelTable = 		Table(APIKEY, AUTOMATION_BASE_ID, AUTOCHANNELS)
channelTableProj = 	Table(APIKEY, SYSTEM_BASE_ID, 	TASKCHANNELS)
peopleTable = 		Table(APIKEY, SYSTEM_BASE_ID, 	PEOPLE)

def registerUser(text: string) -> None:
    args = text.split(" ")
    name = " ".join(args[1:])
    record = peopleTable.first(formula = match({'Name (all)':name}))
    if record:
       fields = {"Telegram Id" : update.message.from_user.id,
                 "Telegram Channel Id":update.message.chat.id,
                 "Has Telegram": True}
       peopleTable.update(record['id'], fields)
       return "Telegram succsesfuly registered"
    else:
       return "You dont exist\nMore likely the name entered does not match our records"

def assignNewChannel() -> dict:
    newChannel = channelTable.first(formula=match({'Uses':'Tasks','In Use':False}))
    if(newChannel):
       newChannelProj = channelTableProj.first(formula=match({'Key':channel['fields']['Key']}))
       channelTable.update(channel['id'], {"In Use":True})
       return channel
    else:
       #TODO proper error handeling
       raise "all channels in use"

def unassignChannel(channelKey):
    channel = channelTable.first(formula=match({'Key':channelKey,'Uses':'Tasks','In Use':True}))
    channelTable.update(channel['id'], {"In Use":False})


def createTaskEntry(name: string, description: string, urgency: int, size: int, assigner: int, taskChannel: string,
                    volunteerMsg: int, assignerMsgId: int, assignerChatId: int) -> None:
     taskTable.create({"Name": name, "Description":description, "Assigned By": assigner,
                      "Status": "Open",
                      "Task Channel": [taskChannel],
                      "Ask Msg Id": volunteerMsg,
                      "Control Msg Id": assignerMsgId,
                      "Control Msg Channel": assignerChatId,
                      "Urgency": urgency, "Max People": size})

def updateTask(status: string, msgId: int)-> dict:
    task = taskTable.first(formula=match({"Control Msg Id":msgId}))
    newFields = {"Status":status}
    if status != "Closed":
       newFields["Assigned To"]=[]
       newFields["Task Channel"]=[]
    
    taskTable.update(task['id'], newFields)
    return task

def getVolunteerChat() -> int:
    channelTable.first({"Uses":"Volunteer"})['fields']['Key']

def addPersonToTask(query: Query): -> string, int, int:
    usr = getVolunteer(update.callback_query.from_user.id)
    task = taskTable.first(formula=match({"Ask Msg Id":query.message.message_id}))

    if task['fields']['Status'] == 'Open':
       if usr:
          assignedTo = []
          if("Assigned To" in task['fields']):
             assignedTo.extend(task['fields']["Assigned To"])

          if(not (usr["id"] in assignedTo)):
             assignedTo.append(usr["id"])

             taskTable.update(task["id"], {"Assigned To":assignedTo})

             return usr['fields']["Name (all)"]), usr['fields']['Telegram Channel Id'], task['fields']['Key'][0]
          else:
             return None, 1, 1
       else:
          return None, 1, 0
     else:
       logging.warn(LOG_TASK_CLOSED_WARN)
       return None, 0, 0

