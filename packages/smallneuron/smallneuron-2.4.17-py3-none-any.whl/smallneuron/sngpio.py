
# To install GPIO module do:
#
# $ sudo pip install --upgrade OPi.GPIO
#



import OPi.GPIO as GPIO
import threading
from time import sleep, time
from ctypes import *
from .logger import Logger

log= Logger("smallneuron.SnGpio")

so_file = "/usr/local/lib/gpio_h3.so"
gpio_h3 = CDLL(so_file)

def eventWait(sngpio, event, gpio, trigger, debounce):
    log.info(f"sngpio eventWait tid {threading.get_native_id()}")
    nextTime=0
    while True:
        GPIO.wait_for_edge(gpio,trigger) # block until happen
        if time() >= nextTime:
            log.debug("gpio event:", event, " gpio:", gpio, " edge:", trigger)
            sngpio.eventManager.putEvent(event,{"gpio":gpio})
            nextTime=time()+debounce

   
class SnGpio:
    def __init__(self, eventManager):        
        self.eventManager=eventManager
        GPIO.setmode(GPIO.SUNXI)
        
    def addEvent(self, event, gpio, edge, pullup=True, debounce=0.5):
        GPIO.setup(gpio,GPIO.IN)

        
        if pullup:
            # Configuramos el pullup llamando directo, usando mi libreria
            # el OPI.GPIO no tiene implementado el pullup
            gpio_num=gpio_h3.gpio_name2num(bytes(gpio,"utf-8"))
            if gpio_num < 0:
                log.error("SnGpio invalid pin",gpio)
                return
            gpio_h3.gpio_confInputPull(gpio_num)

        log.debug("register gpio event:", event, " gpio:", gpio,"(", gpio_num,") edge:", edge)
        threading.Thread(target=lambda : eventWait(self, event, gpio, edge, debounce) ).start()

