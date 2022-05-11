# TEST SERVER
# WORKS OK
# GETS REAL-TIME TRAFFIC INFO FROM API AND STORES TO DB THEN PUBLISHES FROM DB TO MQTT BROKER
# SUBSCRIBES TO THE MQTT BROKER TO GET WEATHER INFORMATION AND THEN SAVES THE WEATHER INFORMATION TO DB 

#sends traffic info
from random import random, uniform
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
import TRAFFIC_API_DB
import TEST_ATMOSPHERE_DATA
#import the client1

broker_address="localhost" #use external broker
client = mqtt.Client("Abdul_MQTT_Server") #create new instance
client.connect(broker_address,1883,60) #connect to broker

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    
   
def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    a = str(msg.payload.decode("utf-8"))
    query = f'insert into weatherupdates (message) values ("{a}");'
    pydb2.runsqlquery(query)
    print ("Message received from Client-> " +str(msg.payload.decode("utf-8")))  # Print a received msg
    print("a is" +a)
    #pydb2.runsqlquery(f"insert into weatherupdates value({str(msg.payload.decode("utf-8")}))

client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

#TRAFFIC_API_DB.get_traffic_data()   # INSERTS LATEST TRAFFIC INFO INTO DB
#TEST_ATMOSPHERE_DATA.get_atmdata()  # INSERTS LATEST ATM DATA INTO DB (PERFORMS 2-Level-FISANALYSIS) 
try:
    while True:
            client.loop_start()
            client.subscribe("ClientPublished")
            #rnum = uniform(1.0,100.0)
            #client.publish("trafficupdates", rnum)
            
            #TRAFFIC_API_DB.get_traffic_data()   # INSERTS LATEST TRAFFIC INFO INTO DB
            #TEST_ATMOSPHERE_DATA.get_atmdata()  # INSERTS LATEST ATM DATA INTO DB (PERFORMS 2-Level-FISANALYSIS) 
            tr_updates = pydb2.mqtt_gettrafficupdates()
            nc1 = pydb2.get_atmupdates_noncrical()
            c1 = pydb2.get_atmupdates_critical()
            
            client.publish("ServerPublished/trafficupdates",tr_updates)      #PUBLISHING TRAFFIC UPDATES
            print("I am Server, I published :" +"\n" +tr_updates)

            client.publish("ServerPublished/criticalupdates", c1)            #PUBLISHING CRITICAL UPDATES                                             
            print("I am Server, I published Critical Updates :" +"\n" +c1)
            
            
            client.publish("ServerPublished/noncriticalupdates", nc1)   #PUBLISHING NONCRITICAL ATM UPDATES
            print("I am Server, I published Non Critical Updates :" +"\n" +nc1)
            

            time.sleep(2)
except KeyboardInterrupt:
    client.disconnect()
    exit(0)