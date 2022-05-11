# RUNS OK
# CALL get_traffic_data() method to clear the replace trafficupdates with latest updates from API
from typing import Counter
from unittest import result
import requests
import json
import time
import pydb2
from datetime import datetime
import time
import pydb2
import paho.mqtt.client as mqtt


#LATITUDE = "52.50811"
#LONGITUDE = "13.47853" EMP.ST.B
LATITUDE = "40.722227"    #works
LONGITUDE = "-74.0046243" #works

# LATITUDE = "43.064797"    
# LONGITUDE = "-93.278516"

RADIUS = "10000"
API_KEY = "6dTA7TI5HTVzyDxtVXjAeQu-hnUd8tUU-JWYMEMU6Tg"
TRAFFIC_API_ENDPOINT = f'https://data.traffic.hereapi.com/v7/incidents?in=circle:{LATITUDE},{LONGITUDE};r={RADIUS}&locationReferencing=olr&apiKey={API_KEY}&lang=en-US'


response = requests.get(url=TRAFFIC_API_ENDPOINT)
# content = json.loads(response.content)
# #print(content["results"][0])
# print(content["results"][0])

jsonResponse = response.json()

# incident0 = jsonResponse["results"][0]
# ime0 = jsonResponse["results"][0]['incidentDetails']['entryTime']
# print(ime0)


# desc = incident0['incidentDetails']['description']['value']
# print(desc)

#FETCHES TRAFFIC INFO FROM API AND INSERTS TO DATABASE
def get_traffic_data():
    pydb2.runsqlquery("truncate trafficupdates")
    count = 0
    while count <1:
        for (x) in jsonResponse:
            #print("Incidents in jsonResponse: ",len(jsonResponse.keys()))
            for y in jsonResponse["results"][count]:
                criticality = jsonResponse["results"][count]['incidentDetails']['criticality']
                desc = jsonResponse["results"][count]['incidentDetails']['description']['value']
                time = jsonResponse["results"][count]['incidentDetails']['entryTime']
                cdate = time[:-10]
                ctime = time[12:-1]
                entryTime = cdate+" "+ctime
                #print(desc)
                pydb2.insert_traffic_updates(criticality,desc,entryTime)   
            
        count += 1
    #print("---------------")
    #print("Latest Informated Updated at : ", datetime.now())
print("TRAFFIC_API_DB: INSERTED LATEST TRAFFIC DATA INTO DB")

