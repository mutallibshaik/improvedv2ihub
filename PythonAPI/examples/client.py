import paho.mqtt.client as mqtt #import the client1
import time
############

def on_log(client, userdata, level, buf):
    print("log: ",buf)



def on_connect(client, userdata, flags, rc):  # The callback for when the client connects to the broker
    print("Connected with result code {0}".format(str(rc)))  # Print result of connection attempt
    client.subscribe("ABDULSHAIKTOPIC1")  # Subscribe to the topic “digitest/test1”, receive any messages published on it
    client.subscribe("ABDULSHAIKTOPIC2")  # Subscribe to the topic “digitest/test1”, receive any messages published on it

def on_message(client, userdata, msg):  # The callback for when a PUBLISH message is received from the server.
    print("Message received-> " + msg.topic + " " + str(msg.payload))  # Print a received msg


client = mqtt.Client("myclient1721")  # Create instance of client with client ID “digi_mqtt_test”
client.on_connect = on_connect  # Define callback function for successful connection
client.on_message = on_message  # Define callback function for receipt of a message

broker_address="localhost" #use external broker
client.connect(broker_address)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    exit(0)