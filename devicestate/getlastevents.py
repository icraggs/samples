
from __future__ import print_function
import requests, base64, time
  
def getlastevents(host, devicetypename, deviceId):
  url = "http://%s/api/v0002/device/types/%s/devices/%s/events" % (host, devicetypename, deviceId)
  result = requests.get(url, auth=(key, token))
  assert result.status_code == 200, result
  events = result.json()
  for event in events:
    event["payload"] = base64.decodestring(event["payload"])
  print(events)

if __name__ == "__main__":    
  from properties import orgid, key, token, devicetype, deviceid
  host = "%s.internetofthings.ibmcloud.com" % (orgid, )
  
  while True:
    getlastevents(host, devicetype, deviceid)
    time.sleep(1)
