# THIS IS CLIENT1 test client
#aim is to publish weather information.

# import time
import time
import requests
import paho.mqtt.client as mqtt
import pydb2
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

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print ("Message received from Server-> " +str(msg.payload.decode("utf-8")))  # Print a received msg


client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

import random

#print(abcd)

try:
    while True:
        client.loop_start()
        client.subscribe("ServerPublished/db")  # Subscribe to the topic “digitest/test1”, receive any messages published on it
        time.sleep(3)
        my_list = ["A","B","C"]
        #xyz = random.choice(my_list)
        #client.publish("ClientPublished",xyz)
        xyz = pydb2.mqtt_getweatherupdates()
        client.publish("ClientPublished/db",xyz)

        print("I am client and  published:" +"\n" +xyz)
        time.sleep(1)
except KeyboardInterrupt:
    client.disconnect()
    exit(0)

