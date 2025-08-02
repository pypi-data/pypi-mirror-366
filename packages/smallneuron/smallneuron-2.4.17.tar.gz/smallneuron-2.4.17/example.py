from time import sleep
import threading
import queue
from sys import stdin
from smallneuron_pelainux import Node, TimerNode, EventManager
from snmqtt import SnMqtt
#from sngpio import SnGpio, GPIO
from sntkinter import SnTkinter
from snserial import SnSerial, serial

##########################
# system core and bridges definitions
#
em=     EventManager()
mqtt=   SnMqtt(eventManager=em,clientId="sngate2",context="sngate2") # mqtt bridge
#gpio=  SnGpio(eventManager=em)                                    # gpio bridge
tkinter=SnTkinter()
port   = SnSerial(em, "/dev/ttyACM0", 9600, serial.EIGHTBITS, serial.PARITY_NONE, serial.STOPBITS_ONE)


#############################
# Ejemplo de nodo customizado
# cuando llega a este nodo 
# publica en mqtt y dibuja en tkinker
class PubNode(Node) :
    def __init__(self, state):
        super().__init__(state)
        
    def enter(self, event, dict_eventargs, stateFrom):
        print("PubNode: Enter:", self.state, "event trigger:", event, "from", stateFrom )
        mqtt.publish("EsteRecontraTopico/"+self.state)
        tkinter.setText("trigger")


            
if __name__ == '__main__': 
    #########################
    # Armamos la red de nodos
    #
    print("creating Nodes")
    n_close    =PubNode("close")
    n_goingback=TimerNode("goingback","backTimer",3)
    n_unlocking=TimerNode("unlocking","unlockTimer",6)
    n_opening  =TimerNode("opening","openTimer",20)
    n_open     =PubNode("open")    
    n_closing  =TimerNode("closing","closeTimer",30)
    n_midopen  =Node("midopen")    
    n_midclose =Node("midclose")    

    n_cmd  =Node("cmd")     # Nodo command que se ejecuta cuando llega el evento indicado,
                            # pero sin modificar el estado de la red

    #
    print("Adding events (edges)")
    #
    em.linkEdge("toggle",n_close, n_goingback )
    em.linkEdge("backTimer",n_goingback,n_unlocking )
    em.linkEdge("toggle",n_goingback,n_midopen )
    em.linkEdge("unlockTimer",n_unlocking, n_opening )    
    em.linkEdge("toggle",n_unlocking, n_midopen )    
    em.linkEdge("openTimer",n_opening, n_open )        
    em.linkEdge("toggle",n_opening, n_midopen )        
    em.linkEdge("toggle",n_midopen,n_closing  )        
    
    em.linkEdge("toggle",n_open, n_closing )
    em.linkEdge("closeTimer",n_closing, n_close )        
    em.linkEdge("toggle",n_closing, n_midclose )        
    em.linkEdge("toggle",n_midclose,n_goingback  )        
    
    em.linkCmd("doit",n_cmd  )   # Incorporamos el commando asociado a un evento
        
    #################################
    # Core SmartNeuron
    print("Start at state 'close'")
    em.start("close")
   
    ############################
    # Bridge MQTT
    # Conectamos eventos de mqtt para que se inyecten
    #
    print("mqtt event 'toggle'")
    mqtt.addEvent("toggle")
    
    print("mqtt connecting to server")
    mqtt.start("172.16.1.2")
      
    ###########################
    # Bridge GPio
    # Definicmos los cambios en pines que generen eventos
    #
    #gpio.addEvent("toggle","PG06", GPIO.RISING)
    
    ###########################
    # Bridge Serial
    # Definicmos los textos que pueden venir con regex
    #
    port.addEvent("toggle")
    port.start()
 
 
    #########################
    # Tkinter bloquea aqui, debe ser el ultimo
    tkinter.loop()
    
    ###########################
    # Bridge CMD
    # Para pruebas agregamos eventos
    # desde la linea de comandos, todo el resto corre en 
    # en threads separados
    # for event in stdin:
    #     e=event[0:-1]
    #     print("New event enter:", e)
    #     em.newEvent(e)
