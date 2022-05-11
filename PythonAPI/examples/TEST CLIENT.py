# THIS IS CLIENT1 test client
#aim is to publish weather information.

# import time
import time
import requests
import paho.mqtt.client as mqtt
import pydb2
import WEATHER_API_DB
#import the client1
 
broker_address="localhost" 
client = mqtt.Client("Client Carla Terminal") #create new instance
client.connect(broker_address,1883,60) #connect to broker



def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
   # client.publish("weather/TerminalClient", abcd)#publish
   # print("Published: ", +abcd)
    client.subscribe("ServerPublished/trafficupdates")

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print ("Message received from Server-> " +str(msg.payload.decode("utf-8")))
    time.sleep(3)  # Print a received msg


client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

import random

#print(abcd)

try:
    while True:
        client.loop_start()
        client.subscribe("ServerPublished/trafficupdates")
        time.sleep(5)
        #client.publish("ClientPublished",xyz)
        xyz = WEATHER_API_DB.get_weather_data()
        client.publish("ClientPublished",xyz)
        print("I am client and  published:" +"\n" +xyz)
        time.sleep(3)
except KeyboardInterrupt:
    client.disconnect()
    exit(0)

