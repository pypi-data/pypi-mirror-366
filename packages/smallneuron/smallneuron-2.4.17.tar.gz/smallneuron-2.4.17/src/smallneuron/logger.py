import syslog
from datetime import datetime
from time import time
import sys
import inspect
import os
import functools

# Este decorador agrega el nombre de la funcion al logging
def logger_with_method(log):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            class_name = args[0].__class__.__name__
            method_name = f"{class_name}.{func.__name__}"
            log.prefix=method_name
            result = func(*args, **kwargs)
            return result
        return wrapper

    return decorator


class Logger:
    perf_enable=False
    prev_time=time()
    logLevel=syslog.LOG_DEBUG
    def __init__(self, service_name, include_file_line=True, log_level=None):
        self.include_file_line= include_file_line
        self.service_name = service_name
        self.prefix=""
        if log_level != None:
            self.logLevel=log_level

    def error(self, *args):
        if syslog.LOG_ERR <= self.logLevel:
            self.__logger(syslog.LOG_ERR, *args)

    def warn(self, *args):
        if syslog.LOG_WARNING <= self.logLevel:
            self.__logger(syslog.LOG_WARNING, *args)

    def notice(self, *args):
        if syslog.LOG_NOTICE <= self.logLevel:
            self.__logger(syslog.LOG_NOTICE, *args)

    def info(self, *args):
        if syslog.LOG_INFO <= self.logLevel:
            self.__logger(syslog.LOG_INFO, *args)

    def debug(self, *args):
        if syslog.LOG_DEBUG <= self.logLevel:
            self.__logger(syslog.LOG_DEBUG, *args)

    def set_level(level):
        Logger.logLevel=level

    def set_perf(setOn):
        Logger.perf_enable=setOn

    def perfMark(self,text):
        if Logger.perf_enable:
            pre=""
            if self.include_file_line:
                frame = inspect.currentframe().f_back
                archivo = os.path.basename(inspect.getfile(frame))
                linea = frame.f_lineno
                pre=f"{archivo}:{linea} - "
            t=time()
            print(self.service_name, pre, t, t-Logger.prev_time, text, file=sys.stderr)
            Logger.prev_time=t
        
    def __logger(self, severity, *args):
        try:
            syslog.openlog(self.service_name, syslog.LOG_CONS | syslog.LOG_PID | syslog.LOG_NDELAY, syslog.LOG_LOCAL1)
            if self.include_file_line:
                frame = inspect.currentframe().f_back.f_back
                archivo = os.path.basename(inspect.getfile(frame))
                linea = frame.f_lineno
                msg=f"{archivo}:{linea} - "
            else:
                msg = ""
            for a in args:
                msg = msg + " " + str(a)

            syslog.syslog(severity, msg)
            if syslog.LOG_ERR >= severity:
                print(msg)
            syslog.closelog()
        except Exception as e:
            print("Syslog fail ", e)

    def ___current_full_date(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    


