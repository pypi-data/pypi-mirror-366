
#
#    pip install paho-mqtt
#
import paho.mqtt.client as mqtt
import threading
from .logger import Logger
log= Logger("smallneuron.SnMqtt")

def on_connect(client, snmqtt, flags, rc):  
    # The callback for when the client connects to the broker 
    log.debug("connected with result code {0}".format(str(rc)))  
    #  result of connection attempt client.subscribe("digitest/test1")  
    # Subscribe to the topic digitest/test1, receive any messages published on it

    for topic in snmqtt.sub_list:
        client.subscribe(snmqtt.prefix+topic)

def on_message(client, snmqtt, msg):  
    # The callback for when a PUBLISH message is received from the server.
    log.debug("Message received-> "+ msg.topic + " " + str(msg.payload))  # Print a received msg
    
    # Vemos si concuerda con el prefijo y lo sacamos
    if  msg.topic[0:len(snmqtt.prefix)] == snmqtt.prefix :
        snmqtt.eventManager.putEvent(msg.topic[len(snmqtt.prefix):],{ "payload": str(msg.payload)})

    
def on_publish(client,snmqtt,result):             #create function for callback
    log.debug("published ", result)

def on_subscribe(client,snmqtt,result, qos):             #create function for callback
    log.debug("subscribed ", result)

class SnMqtt(mqtt.Client):
    def __init__(self, eventManager, clientId, context=None):
        super().__init__(client_id=clientId, userdata=self)
        
        if context != None and context != "":
            self.prefix=context+"/"
        else:
            self.prefix=""
        self.context=context;
        self.sub_list=[];
        self.eventManager=eventManager
        self.on_connect = on_connect  # Define callback function for successful connection
        self.on_message = on_message  # Define callback function for receipt of a message
        self.on_publish = on_publish  # client.connect("m2m.eclipse.org", 1883, 60)  # Connect to (broker, port, keepalive-time)
        self.on_subscribe = on_subscribe
    def addEvent(self, topic):
        log.debug ("register mqtt subscribed topic event:", topic)
        self.sub_list.append(topic);
 
    def start(self, broker):
        try :
            self.connect(broker)
            log.debug("SnMqtt start")
            threading.Thread(target=self.loop_forever).start()
        except Exception as e:
            log.error("mqtt not started", e)

 
