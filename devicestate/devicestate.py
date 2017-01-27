

from __future__ import print_function
import logging, json, requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def createSchema(host, schemaName, schemaFileName, schemaContents, description=None):
  url = "https://%s/api/v0002/schemas" % (host, )
  
  fields={
    'schemaFile': (schemaFileName, schemaContents, 'application/json'),
    'schemaType': 'json-schema', 
    'name': schemaName,
  }
  if description:
    fields["description"] = description
  
  multipart_data = MultipartEncoder(fields=fields)
  result = requests.post(url, auth=(key, token), data=multipart_data,
                headers={'Content-Type': multipart_data.content_type})
  rc = result.json()["id"] if result.status_code == 201 else None
  return result, rc # return the id of the created schema resource
  
def getSchema(host, schemaId):
  url = "https://%s/api/v0002/schemas/%s" % (host, schemaId)
  result = requests.get(url, auth=(key, token))
  rc = result.json() if result.status_code == 200 else None
  return result, rc
  
def createEventType(host, name, schemaId, description=None):
  url = "https://%s/api/v0002/event/types" % (host, )
  body = {"name" : name, "schemaId" : schemaId}
  if description:
    body["description"] = description
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json()["id"] if result.status_code == 201 else None
  return result, rc
  
def createPhysicalInterface(host, name, description=None):
  url = "https://%s/api/v0002/physicalinterfaces" % (host, )
  body = {"name" : name, "description" : description}
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json()["id"] if result.status_code == 201 else None
  return result, rc

def mapEventTypeToPhysicalInterface(host, physicalInterfaceId, eventId, eventTypeId):
  url = "https://%s/api/v0002/physicalinterfaces/%s/events" % (host, physicalInterfaceId)
  body = {"eventId" : eventId, "eventTypeId" : eventTypeId}
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json() if result.status_code == 201 else None
  return result, rc
  
def updateDeviceTypeWithPhysicalInterface(host, devicetypename, physicalInterfaceId=None):
  url = "https://%s/api/v0002/device/types/%s" % (host, devicetypename)
  body = {"physicalInterfaceId" : physicalInterfaceId} if physicalInterfaceId else {}
  result = requests.put(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json() if result.status_code == 200 else None
  return result, rc
  
def createApplicationInterface(host, name, schemaId, description=None):
  url = "https://%s/api/v0002/applicationinterfaces" %(host, )
  body = {"name" : name, "schemaId" : schemaId}
  if description:
    body["description"] = description
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json()["id"] if result.status_code == 201 else None 
  return result, rc
  
def addApplicationInterfaceToDeviceType(host, devicetypename, name, appInterfaceId, schemaId, description=None):
  url = "https://%s/api/v0002/device/types/%s/applicationinterfaces" % (host, devicetypename)
  body = {"name" : name, "id" : appInterfaceId, "schemaId" : schemaId}
  if description:
    body["description"] = description
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json() if result.status_code == 201 else None
  return result, rc
  
def addMappingsToDeviceType(host, devicetypename, mappings):
  url = "https://%s/api/v0002/device/types/%s/mappings" % (host, devicetypename)
  result = requests.post(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(mappings))
  rc = result.json() if result.status_code == 201 else None
  return result, rc 
  
def validateDeviceType(host, devicetypename):
  url = "https://%s/api/v0002/device/types/%s" % (host, devicetypename)
  body = {"operation" : "validate"}
  result = requests.patch(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json() if result.status_code == 200 else None
  return result, rc
  
def deployDeviceType(host, devicetypename):
  url = "https://%s/api/v0002/device/types/%s" % (host, devicetypename)
  body = {"operation" : "deploy"}
  result = requests.patch(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  rc = result.json() if result.status_code == 200 else None
  return result, rc

def define(devicetypename):
  ids = {}
    
  logger.info("# ---- add an event schema -------")
  schemaFile = json.dumps({ "type" : "object", "properties" : { "d" :
    { "type" : "object", "properties" : {
        "myName": {"type": "string"},
        "accelX": {"type": "number"},
        "accelY": {"type": "number"},
        "accelZ": {"type": "number"},
        "temp": {"type": "number"},
        "potentiometer1": {"type": "number"},
        "potentiometer2": {"type": "number"},
        "joystick" : {"type": "string"},
    } } } })
  result, ids["k64f event schema"] = createSchema(host, "k64F event schema", 'K64Event.json', schemaFile)
  assert result.status_code == 201, str(result) + " " + str(result.text)
    
  logger.info("# ---- get the schema back -------")
  result, rc = getSchema(host, ids["k64f event schema"])
  assert result.status_code == 200, result

  logger.info("# ---- add an event type -------")    
  result, ids["k64feventtype"] = createEventType(host, "K64F event", ids["k64f event schema"], "K64F event")
  assert result.status_code == 201, result
    
  logger.info("# ---- add a physical interface -------")  
  result, ids["physicalinterface"] = createPhysicalInterface(host, "K64F", "The physical interface for K64F example")
  assert result.status_code == 201, result
    
  logger.info("# ---- add the event type to the physical interface -------")
  result, rc = mapEventTypeToPhysicalInterface(host, ids["physicalinterface"], "status", ids["k64feventtype"])
  assert result.status_code == 201, str(result) + " " + str(result.text)
    
  logger.info("# ---- add the physical interface to the device type")
  result, rc = updateDeviceTypeWithPhysicalInterface(host, devicetypename, ids["physicalinterface"])
  assert result.status_code == 200, str(result) + " " + str(result.text)
    
  logger.info("# ---- add an application interface schema -------")    
  schemaFile = json.dumps(
      { "type" : "object",
        "properties" : {
          "eventCount" :{"type": "number", "default":0},
          "accel": {"type": "object",
            "properties" : {
              "x": {"type": "number", "default": 0},
              "y": {"type": "number", "default": 0},
              "z": {"type": "number", "default": 0},
            },
          },
          "temp": {"type": "object",
            "properties" : {
              "C": {"type": "number", "default": 0},
              "F": {"type": "number", "default": 0},
              "isLow": {"type": "boolean", "default": False},
              "isHigh": {"type": "boolean", "default": False},
              "lowest" : {"type": "number", "default": 100},
              "highest" : {"type": "number", "default": 0},
            },
            "required" : ["C", "F", "isLow", "isHigh", "lowest", "highest"],
          },
          "potentiometers": {"type": "object",
             "properties" : {
                "1": {"type": "number", "default": 0},
                "2": {"type": "number", "default": 0},
            },
          },
          "joystick": {"type": "string", "default": "NONE" },
        },
        "required" : ["eventCount", "accel", "potentiometers", "joystick", "temp"],
      }
    )
  result, ids["k64f app interface schema"] = createSchema(host, "k64fappinterface", 'k64fappinterface.json', schemaFile)
  assert result.status_code == 201, str(result) + " " + str(result.text)
  print("App interface schema id", ids["k64f app interface schema"])
    
  logger.info("# ---- add an application interface -------")
  result, ids["k64f app interface"] = \
       createApplicationInterface(host, "K64F application interface", ids["k64f app interface schema"], "K64F application interface")
  assert result.status_code == 201, str(result) + " " + str(result.text)
    
  logger.info("# ---- associate application interface with the device type -------")  
  result, rc = addApplicationInterfaceToDeviceType(host, devicetypename, "k64f application interface", 
                 ids["k64f app interface"], ids["k64f app interface schema"])
  assert result.status_code == 201, str(result) + " " + str(result.text)
    
  logger.info("# ---- add mappings to the device type -------")
  mappings = {"applicationInterfaceId" : ids["k64f app interface"], 
            "propertyMappings" : {
              # eventid -> { property -> eventid property expression }
              "status" :  { 
                "eventCount" : "$state.eventCount+1",
                "accel.x" : "$event.d.accelX",
                "accel.y" : "$event.d.accelY",
                "accel.x" : "$event.d.accelZ",
                "temp.C" : "$event.d.temp",  
                "temp.F" : "$event.d.temp * 1.8 + 32",
                "temp.isLow" : "$event.d.temp < $state.temp.lowest",
                "temp.isHigh" : "$event.d.temp > $state.temp.highest",
                "temp.lowest" : "($event.d.temp < $state.temp.lowest) ? $event.d.temp : $state.temp.lowest",
                "temp.highest" : "($event.d.temp > $state.temp.highest) ? $event.d.temp : $state.temp.highest",
                "potentiometers.1" : "$event.d.potentiometer1",
                "potentiometers.2" : "$event.d.potentiometer2",
                "joystick" : '($event.d.joystick == "LEFT") ? "RIGHT" : (($event.d.joystick == "RIGHT") ? "LEFT" : $event.d.joystick)'
               },
            }
        }
        
  result, rc = addMappingsToDeviceType(host, devicetypename, mappings)
  assert result.status_code == 201, result
    
  logger.info("# ---- validate definitions -------") 
  result, rc = validateDeviceType(host, devicetypename)
  assert result.status_code == 200, str(result) + " " + str(result.text)
  print(str(result) + " " + str(result.text))
    
  logger.info("# ---- deploy definitions -------") 
  result, rc = deployDeviceType(host, devicetypename)
  assert result.status_code == 202, str(result) + " " + str(result.text)
  print(str(result) + " " + str(result.text))

if __name__ == "__main__":    

  from properties import orgid, key, token, devicetype, deviceid
  host = "%s.internetofthings.ibmcloud.com" % (orgid, )
  
  define(devicetype)

