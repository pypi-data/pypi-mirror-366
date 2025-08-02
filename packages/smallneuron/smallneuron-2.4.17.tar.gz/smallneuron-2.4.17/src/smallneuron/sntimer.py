#
# Este modulo es un simple timer, que coloc un evento con paramtros despues de 
# del tiempo indicado
#
import re
import threading
import os.path
import traceback
from .logger import Logger, logger_with_method
from time import sleep
from .smallneuron import  EventManager

log=Logger("smallneuron.SnTimer")

    
class SnTimer():
    def __init__(self, eventManager:EventManager):
        self.eventManager = eventManager
        log.info("start")

    def callback(self, time=1.0):
        sleep(time)
        return { "time":time } 

    # Los eventos agregado con timer son por defecto 
    # solo validos para el siguiente estado
    @logger_with_method(log)
    def watchEvent(self, event, event_params={}, time:float=1.0, valid:int=1):
        until=self.eventManager.count+valid
        log.debug(f"event:{event}, params:{event_params} time:{time}s valid:{valid} until:{until}")
        return self.eventManager.watchEvent(event=event,
                                            event_params=event_params, 
                                            callback_obj=self, 
                                            callback_function_args={"time":time},
                                            mode="noloop", 
                                            valid_until=until)


