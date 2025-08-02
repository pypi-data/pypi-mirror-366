
# Es un bridge dummmy 
# para correr sin los dispositivos
#


import serial
import os
import errno
import threading
from .logger import Logger
log= Logger("smallneuron.SnGpio")

class SnGpio:
    def __init__(self, eventManager):        
        self.eventManager=eventManager
        
    def addEvent(self, event, gpio, edge, pullup=True, debounce=0.5):
        pass          

class SnSerial():
    def __init__(self, eventManager, port, baudrate, bytesize, parity, stopbits, endofline : bytes = b'\r' ):        
       self.eventManager=eventManager
        
    def addEvent(self, event, pattern=".*"):
        pass


    def start(self):
        log.debug("SnDummy started")
    
class Locker:
    def __init__(self, port, model, mode_dev=False):
        self.port = port        
        self.model = model
 


    def unlock(self, posName):
        log.debug("Dummy locker unlock ", posName, self.model, self.port)
        return 0

    def status(self, posName):
        log.debug("Dummy locker status ", posName, self.model, self.port, )
        return 0

