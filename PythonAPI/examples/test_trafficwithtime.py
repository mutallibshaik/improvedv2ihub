#FETCHES TRAFFIC INFO FROM API AND INSERTS TO DATABASE
from unittest import result
import requests
import json
import time
import pydb2
from datetime import datetime
LATITUDE = "52.50811"
LONGITUDE = "13.47853"
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
            pydb2.insert_traffic_updates(criticality,desc,entryTime)   
            count += 1
    print("---------------")
    print("Latest Informated Updated at : ", datetime.now())
get_traffic_data()
