#FETCHES TRAFFIC INFO FROM API AND INSERTS TO DATABASE
# FINAL TRAFFIC AND MQTT SERVER

# TIS IS  TEST SERVER!!!!!!!!!!!!!!!!!
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
#import the client1

broker_address="localhost" #use external broker
client = mqtt.Client("Abdul_MQTT_Server") #create new instance
client.connect(broker_address,1883,60) #connect to broker

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("trafficupdates")  # Subscribe to the topic “digitest/test1”, receive any messages published on it
    #client.subscribe("ABDULSHAIKTOPIC2")  # Subscribe to the topic “digitest/test1”, receive any messages published on it

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    #a = str(msg.payload)
    print ("Message received-> " +str(msg.payload.decode("utf-8")))  # Print a received msg

#LATITUDE = "52.50811"
#LONGITUDE = "13.47853" below is EMP STATE BUILDING NEW YORK
LATITUDE = "40.722227"
LONGITUDE = "-74.0046243"
RADIUS = "10000"
API_KEY = "6dTA7TI5HTVzyDxtVXjAeQu-hnUd8tUU-JWYMEMU6Tg"
TRAFFIC_API_ENDPOINT = f'https://data.traffic.hereapi.com/v7/incidents?in=circle:{LATITUDE},{LONGITUDE};r={RADIUS}&locationReferencing=olr&apiKey={API_KEY}&lang=en-US'

response = requests.get(url=TRAFFIC_API_ENDPOINT)


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
#get_traffic_data()



#FETCHES FROM DATABSE AND PUBLISHES TRAFFIC INFO
def start_mqtt_server():
        abcd = pydb2.mqtt_gettrafficupdates()
        #xyz = "text2"
        client.publish("trafficupdates", abcd)#publish
        print("Publishing below data " +"\n" +abcd)
        time.sleep(10)
        #client.publish("ABDULSHAIKTOPIC2", xyz)#publish
        #print("Published",xyz)
        #time.sleep()
        client.subscribe("weather/TerminalClient")


#start_mqtt_server()

def main():
    count = 0
    while True:
        count = count+1
        print("COUNTER IS", count)
        get_traffic_data()
        start_mqtt_server()


main()