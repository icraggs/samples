

from __future__ import print_function
import requests, json, time

requests.packages.urllib3.disable_warnings()

if __name__ == "__main__":    
  from properties import orgid, key, token, devicetype as devicetypename, deviceid
  host = "%s.internetofthings.ibmcloud.com" % (orgid, )
  
  # get mappings
  url = "https://%s/api/v0002/device/types/%s/mappings" % (host, devicetypename)
  resp = requests.get(url, auth=(key, token), verify=True)
  assert resp.status_code == 200, resp
  print(resp.json())
  
  # delete the mappings
  count = 0; ids = []
  for id in [x["applicationInterfaceId"] for x in resp.json()]:
    url = "https://%s/api/v0002/device/types/%s/mappings/%s" % (host, devicetypename, id)
    result = requests.delete(url, auth=(key, token), verify=True)
    assert result.status_code == 204, str(result) + " " + str(result.text)
    count += 1; ids.append(id)
  print("Mappings deleted:", count, ids)
  
  # list application interfaces for the device type
  url = "https://%s/api/v0002/device/types/%s/applicationinterfaces" % (host, devicetypename)
  resp = requests.get(url, auth=(key, token), verify=False)
  assert resp.status_code == 200, resp
  #print(resp.json())
  
  # disassociate the application interfaces
  count = 0
  for id in [x["id"] for x in resp.json()]:
    url = "https://%s/api/v0002/device/types/%s/applicationinterfaces/%s" % (host, devicetypename, id)
    result = requests.delete(url, auth=(key, token), verify=True)
    assert result.status_code == 204, str(result) + " " + str(result.text)
    count += 1
  print("Application interfaces disassociated:", count)
 
  # list application interfaces
  url = "https://%s/api/v0002/applicationinterfaces" % (host, )
  resp = requests.get(url, auth=(key, token), verify=False)
  assert resp.status_code == 200, resp
    
  # delete application interfaces  
  count = 0
  for id in [x["id"] for x in resp.json()["results"]]:
    url = "https://%s/api/v0002/applicationinterfaces/%s" % (host, id)
    result = requests.delete(url, auth=(key, token), verify=True)
    if result.status_code == 409:
      # if the delete failed, remove the 
      url = "https://%s/api/v0002/device/types/%s/applicationinterfaces/%s" % (host, devicetypename, id)
      result = requests.delete(url, auth=(key, token), verify=True)
      assert result.status_code == 204, str(result) + " " + str(result.text)
        
      url = "https://%s/api/v0002/applicationinterfaces/%s" % (host, id)
      result = requests.delete(url, auth=(key, token), verify=True)
    assert result.status_code == 204, str(result) + " " + str(result.text)
    count += 1
  print("Application interfaces deleted:", count)
  
  # remove the physical interface from the device type
  url = "https://%s/api/v0002/device/types/%s" % (host, devicetypename)
  body = {}
  result = requests.put(url, auth=(key, token), headers={"Content-Type":"application/json"}, data=json.dumps(body))
  assert result.status_code == 200, result
  
  # list and delete physical interfaces
  url = "https://%s/api/v0002/physicalinterfaces" % (host, )
  resp = requests.get(url, auth=(key, token), verify=False)
  assert resp.status_code == 200, resp
  #print("Schemas found", resp, [x["id"] for x in resp.json()["results"]])
  
  count = 0
  for id in [x["id"] for x in resp.json()["results"]]:
    # list and remove any event types from the physical interface
    url = "https://%s/api/v0002/physicalinterfaces/%s/events" % (host, id)    
    
    url = "https://%s/api/v0002/physicalinterfaces/%s" % (host, id)
    resp = requests.delete(url, auth=(key, token), verify=True)
    assert resp.status_code == 204, resp
    count += 1
  print("Physical interfaces deleted:", count)
  
  # list and delete event types
  url = "https://%s/api/v0002/event/types" % (host, )
  resp = requests.get(url, auth=(key, token), verify=True)
  assert resp.status_code == 200, resp
  #print("Schemas found", resp, [x["id"] for x in resp.json()["results"]])
  
  count = 0
  for id in [x["id"] for x in resp.json()["results"]]:
    url = "https://%s/api/v0002/event/types/%s" % (host, id)
    resp = requests.delete(url, auth=(key, token), verify=True)
    assert resp.status_code == 204, resp
    count += 1
  print("Event types deleted:", count)

  # list and delete schemas
  url = "https://%s/api/v0002/schemas" % (host, )
  resp = requests.get(url, auth=(key, token), verify=True)
  assert resp.status_code == 200, resp
  #print("Schemas found", resp, [x["id"] for x in resp.json()["results"]])
  
  count = 0
  for id in [x["id"] for x in resp.json()["results"]]:
    url = "https://%s/api/v0002/schemas/%s" % (host, id)
    resp = requests.delete(url, auth=(key, token), verify=True)
    assert resp.status_code == 204, resp
    count += 1
  print("Schemas deleted:", count)
    
