
from __future__ import print_function
import requests, time

def getappinterfaces(host, devicetypename, deviceid):
  url = "http://%s/api/v0002/device/types/%s/applicationinterfaces" % (host, devicetypename)
  result = requests.get(url, auth=(key, token))
  assert result.status_code == 200, result
  try:
    rc = [appintf["id"] for appintf in result.json()]
  except:
    rc = None
  return rc

def getstate(host, devicetypename, deviceId, appinterfaceid):
  url = "http://%s/api/v0002/device/types/%s/devices/%s/state/%s" % (host, devicetypename, deviceId, appinterfaceid)
  result = requests.get(url, auth=(key, token))
  print(result.json())
  assert result.status_code == 200, result
  #print("getstate elapsed", result.elapsed)
  
if __name__ == "__main__":    
  from properties import orgid, key, token, devicetype, deviceid
  host = "%s.internetofthings.ibmcloud.com" % (orgid, )
    
  appinterfaceids = getappinterfaces(host, devicetype, deviceid)
  
  while True:
    for appinterfaceid in appinterfaceids:
      getstate(host, devicetype, deviceid, appinterfaceid)
    time.sleep(1)
