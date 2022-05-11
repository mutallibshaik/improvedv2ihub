# TEST SERVER FOR CARLA
from random import uniform
import time
import paho.mqtt.client as mqtt

#import the client1

broker_address="localhost" #use external broker
client = mqtt.Client("ABDUL_CARLA_SERVER") #create new instance
client.connect(broker_address,1883,60) #connect to broker

def on_log(client, userdata, level, buf):
    print("log: ",buf)

def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    
   
def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    a = str(msg.payload.decode("utf-8"))
    print ("Message received from Client-> " +str(msg.payload.decode("utf-8")))  # Print a received msg
    

client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

try:
    while True:
            client.loop_start()
            critical = "critical"
            rnum = uniform(1.0,100.0)
            client.publish("trafficupdates", rnum)
            client.publish("critical", critical)
            print("I am Server, I published :" +"\n" +str(rnum))
            print("I am criticalServer, I published :" +critical)
            time.sleep(3)
except KeyboardInterrupt:
    client.disconnect()
    exit(0)            
            



