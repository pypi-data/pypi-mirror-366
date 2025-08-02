# Es un bridge dummmy
# para correr sin los dispositivos
#


import serial
import os
import errno
import threading
import json
from .logger import Logger
import traceback

# Con esto leemos data desde el named pipe /tmp/sndummy
# Para pruebas
#

log=Logger("smallneuron.SnInput")
FIFO = "/tmp/sndummy"

#
# SnInput
#
class SnInput:
    def __init__(self, eventManager):
        self.eventManager = eventManager

    # Add tothe fifo an event
    def fifoEvent(self, event, params):
        line=event
        if type(params) == dict:
            line=line+" "+json.dumps(params)
        self.fifoLine(line)
 
    def fifoLine(self, line):
        with open(FIFO, "w") as fifo:
            fifo.write(line)
            fifo.close()

    # Corre en un thread separado
    def eventWait(self):
        log.info(f"eventWait tid {threading.get_native_id()}")
        try:
            log.debug("reader start")
            # Limpiamos la cola
            try:
                log.info("fifo remove")
                os.remove(FIFO)
            except FileNotFoundError:
                pass
            log.info("fifo create")
            os.umask(0)  # esto para que quede como default 066
            os.mkfifo(FIFO, 0o666)
            log.info("fifo create done")

            #log.debug("SnInput read pid:", threading.get_native_id())
            while True:
                #log.debug("open")
                with open(FIFO) as fifo:
                    #log.debug("open")
                    data = fifo.read()
                    log.debug("read:", data)
                    if len(data) != 0:
                        # Procesamos lo leido y generamos el evento
                        #
                        data = data.strip()
                        p = data.find(" ")
                        if p == -1:
                            #log.info("SnInput event:", data)
                            self.eventManager.putEvent(data)
                        else:
                            #log.debug("SnInput event:",data[:p])
                            #log.debug("SnInput args:",data[p:])
                            try:
                                args = json.loads(data[p:])
                                self.eventManager.putEvent(data[:p], args)
                            except Exception as e:
                                log.warn("Invalid json:", data[p:], " skipped")
                    fifo.close()
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            self.eventManager.putEvent("panic", str(e))
            exit(1)

    def start(self):
        log.info("started")
        threading.Thread(target=lambda: SnInput.eventWait(self)).start()


if __name__ == "__main__":
    print("Using fifo:", FIFO)
    print("write one event per line plus arguments")
    print('open_event { "slot":"I2_1"}')
    while True:
        line = input(">")
        print("readen:", line)
        with open(FIFO, "w") as fifo:
            fifo.write(line)
            print("written:", line)
            fifo.close()

