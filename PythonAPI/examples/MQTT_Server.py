import time
import pydb2
import paho.mqtt.client as mqtt
#import the client1
 
broker_address="localhost" #use external broker
client = mqtt.Client("Abdul_MQTT_Server") #create new instance
client.connect(broker_address,1883,60) #connect to broker


def start_mqtt_server():
    while True:
        abcd = pydb2.mqtt_gettrafficupdates()
        #xyz = "text2"
        client.publish("trafficupdates", abcd)#publish
        print("Publishing below data " +"\n" +abcd)
        time.sleep(3)
        #client.publish("ABDULSHAIKTOPIC2", xyz)#publish
        #print("Published",xyz)

        time.sleep(3)
start_mqtt_server()