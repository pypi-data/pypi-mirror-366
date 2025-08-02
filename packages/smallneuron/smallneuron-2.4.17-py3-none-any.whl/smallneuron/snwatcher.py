from time import sleep, time
import threading
import re
import json
from .logger import Logger
import traceback
from datetime import datetime

log= Logger("smallneuron.snwatcher")

class SnWatcher():
    '''
    Cada instancia de esta clase monitorea la funcion callback() del bridge, con bridge_args como parametros,
    Si la respuesta contiene el bridge_pattern se dispara el evento con event_params que se le agrega "value": respuesta

    Consideraciones importantes de la funcion callback:
        1. Debe recibir como parametros los mismo elementos del dict bridge_args de enter()
        2. Debe retornar un diccionario con almenos el elemento data, todo el diccionario retornado
           seran parte del argumento del evento junto a los event_params
        3. Si se repiten los elementos retornados por callback() con los events_params mandan los de callback()
    '''
    def __init__(self, eventManager, event, event_params={}, event_pattern=ModuleNotFoundError, valid_until=0):
        self.em=eventManager
        self.event=event
        self.event_params=event_params
        self.event_pattern=event_pattern
        self.event_valid_until=valid_until
        self.stoploop=False
        self.thread=None
        #log.debug("created")
       
    def start(self, callback_obj, callback_function_args={}, mode="loop",period=1):
        '''
        modos validos:
            loop: (default) Se leera permanentenemente hasta el stop, genenrando multiples eventos
            match: Se iterara hasta el primer match, genera 1 evento
            noloop: Termina despues de la primera llamada, puede no generar evento alguno
        '''
        #log.debug("start")
        if self.thread == None or not self.thread.is_alive():
            self.stoploop=False
            try:
                #log.debug("SnWatcher.run Thread create")
                self.thread=threading.Thread(target=SnWatcher._loop_callback, args=(self,[callback_obj,callback_function_args,mode, period]))
                #log.debug("SnWatcher.run Thread to start")
                self.thread.start()
                #log.debug("SnWatcher.run Thread to started")
                return True
            except Exception as e:
                log.error(f"Error for event {self.event}",e)
                log.error(traceback.format_exc())

        log.warning("run fail")
        return False
        
    def _loop_callback(self, args):
        try:
            [callback_obj,callback_function_args,mode, period] = args
            if type(callback_obj) == type:
                callback_name=callback_obj.__name__
            else:
                callback_name=callback_obj.__class__.__name__
                
            log.debug( "Watcher START, tid ",threading.get_native_id(), [callback_name, callback_function_args, mode,period])
            # Pasamos como argumento a la funcion externa un diccionario para los datos
            # que necesite persistir entre llamados
            while not self.stoploop:
                try:
                    resp=callback_obj.callback(**callback_function_args)
                except Exception as e:
                    log.warn(threading.get_native_id(),f"Exception from {callback_name} for event {self.event}", e)
                    log.error(traceback.format_exc())
                    # Nos olvidamos de esto y saltamos al proximo ciclo
                    sleep(period)
                    continue
                                       
                # Si la respuesta no es un dict
                # creamos uno con la respuesta como value
                if type(resp) != dict:
                    data=resp
                    resp={"value":data}

                if self.event_pattern == None or re.search(self.event_pattern, resp["value"]) != None:
                    self.em.putEvent(self.event, dict(self.event_params,**resp),self.event_valid_until)
                    if mode=="match":
                        log.debug( "Watcher MATCH trigger, tid ",threading.get_native_id(), self.event_params)
                        break
                    else:
                        log.debug( "Watcher LOOP trigger , tid ",threading.get_native_id(), self.event_params)

                if mode=="noloop" :
                    log.debug( "Watcher NOLOOP end, tid ",threading.get_native_id())
                    break
                    
                # default mode is loop 
                sleep(period)

            log.debug( "Watcher END, tid ",threading.get_native_id(), [callback_name, callback_function_args, mode,period])
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            log.debug( "Watcher FAIL, tid ",threading.get_native_id(),f"_check loop exit, exception for event {self.event}")


    def stop(self, wait_to_finish=False):
        self.stoploop=True
        if wait_to_finish:
            self.thread.join()

 