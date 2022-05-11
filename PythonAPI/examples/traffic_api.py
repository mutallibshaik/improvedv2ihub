from unittest import result
import requests
import json
import time
import pydb2
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



# desc = incident0['incidentDetails']['description']['value']
# print(desc)


def get_traffic_data():
    count = 0
    while count <1:
        for (x) in jsonResponse:
            print("Incidents in jsonResponse: ",len(jsonResponse.keys()))
            for y in jsonResponse["results"][count]:
                criticality = jsonResponse["results"][count]['incidentDetails']['criticality']
                desc = jsonResponse["results"][count]['incidentDetails']['description']['value']
                pydb2.insert_traffic_updates(criticality,desc)
                          
            count += 1
    
get_traffic_data()

# while True:
#     get_traffic_data()
#     time.sleep(5)