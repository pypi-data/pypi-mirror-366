#
# Este modulo escucha en una puerta serial, se definen eventos
# en base a patrones (regEx) del contenido leido, se testean
# secuencialemnte en el orden que dueron agregados
#
# pip install pyserial
#
import serial
import time
import re
import threading
import os.path
import traceback
from .logger import Logger

log=Logger("smallneuron.SnSerial")

class SnSerial(serial.Serial):
    def __init__(self, eventManager, port, baudrate, bytesize, parity, stopbits, endofline: bytes = b"\r"):
        super().__init__(baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits)
        self.originalPort=port
        self.eventManager = eventManager
        self.eol = endofline
        self.events = []
        self.fails=0
        log.info("start")

    def callback(self):
        try:
            if not self.isOpen():
                port=self.originalPort
                if not os.path.exists(port):
                    port=port[:-1]+"1"
                    log.debug("serial port not exist, trying ",port)
                self.port=port
                self.open()

            self.fails=0
            line = b""
            c = b""
            while c != self.eol:
                c = self.read()
                line += c
            log.debug("Leido: "+ str(line[:-1].decode("utf-8")) )
            print("Leido: "+ str(line[:-1].decode("utf-8")) )
            return line[:-1].decode("utf-8")
        
        except Exception as e:
            self.fails=self.fails+1
            if self.fails > 10:
                raise("Falla multiples veces lectura serial "+str(self.fails))
            log.warn("Reintentamos lectura "+str(e) )
            time.sleep(1)
            self.close()

    def watchEvent(self, event, event_params={}, data_pattern=None, mode="loop", period=1):
        return self.eventManager.watchEvent(event, event_params=event_params, data_pattern=data_pattern, 
                    callback_obj=self, callback_function_args={},
                    mode=mode,period=period)
