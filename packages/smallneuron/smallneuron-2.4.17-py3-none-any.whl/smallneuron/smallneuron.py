from time import sleep, time
import threading
import queue
import re
import os
import json
from .logger import Logger, logger_with_method
from .snwatcher import SnWatcher
import traceback
from datetime import datetime
import sys
import glob
import bisect
import copy
#
# Para que funcione el tooltip debe set en formato svg, para generarlo usar:
#
#    dot -Tsvg -osmallneuron.svg smallneuron.dot
#
# Despues visualizar smallneuron.svg con chrome
#

log= Logger("smallneuron")

# tooltip format
def ttfmt(txt):
    # Eliminamos los espacion entre \n y el primer caracter
    return re.sub(r"\n +", "\n", txt)


class Node:
    nodelist = {}

    def __init__(self, state, desc="", style=""):
        self.state = state
        self.change_state=False
        self.event_manager = None  # Este link es llenado durante addEdge del event manager
        self.desc = desc
        self.style = style
        self._cmd=False
        if state in Node.nodelist:
            raise "Estado ya existe como Nodo" + state
        Node.nodelist[state] = self
        
    def leave(self, event, params, stateTo):
        log.perfMark("     In Node.leave()")

    def enter(self, event, params, stateFrom):
        log.perfMark("     In Node.enter()")

    def leave(self, event, params, stateTo):
        log.perfMark("     In Node.leave()")

    def __eq__(self, other):
        if other == None:
            return False
        else:
            return self.state == other.state
       

class LambdaNode(Node):
    def __init__(self, state, lambdaEnter,lambdaLeave=None, desc="", style=""):
        super().__init__(state, desc, style)
        self.enter = lambdaEnter
        if lambdaLeave!= None:
            self.leave = lambdaLeave
            

    def __eq__(self, other):
        return self.state == other.state


# def TimerThread(queue, event, params, time, logging):
#     # print("TimerThread ", event, time, "s")
#     sleep(time)
#     queue.put((event, params, { "time": time, "logging":logging}))
#     # print("TimerThread ", event, " done")

class EventManager:
    def __init__(self, graphDir_and_prefix="."):
        # for public use, general context
        self.context={}
        
        
        self.currentState = None
        self.currentArgs = None
        self.currentNode =None
        self.prevState = None
        self.count = 0 # state count
        self.graph_n = 0
        self.events = queue.SimpleQueue()
        self.net = (
            {}
        )  # estructura es { "evento1": { "estado Origen1" : (nodoDestino1, "event_desc1" ), "estadoOrigen2": (nodoDestino2, "event_desc2") }, "evento2"...
        self.cmds = (
            {}
        )  # estructura es { "evento1": (nodoDestino1, "event_desc1" ), "evento2": (nodoDestino2, "event_desc2")...
        self.graphDir=graphDir_and_prefix

        log.notice("*** STARTED ***")
        
    # Retorna una tupla (nodo, desc) asociado aevento y Nodo From
    def getNetToNode(self, event, nodeFrom ):
        if event in self.net:
            if nodeFrom.state in self.net[event]:
                return self.net[event][nodeFrom.state]
        return None
        
    def linkEdge(self, event, nodeFrom: Node, nodeTo: Node, desc=""):
        if event in self.cmds:
            print("Error event already in cmds ", event)
            raise "Error event already in cmds"
        elif event in self.net:               
            if nodeFrom.state in self.net[event]:
                print("Error edge already included ", event, nodeFrom, nodeTo)
                raise "Error edge already included"
            else:
                self.net[event][nodeFrom.state] = (nodeTo, desc)
        else:
            self.net[event] = {nodeFrom.state: (nodeTo, desc)}
            nodeFrom.event_manager = self
            nodeTo.event_manager = self

    def linkCmd(self, event, nodeTo: Node, change_state=False, desc=""):
        if event in self.cmds:
            print("Error event already in cmds ", event)
            raise "Error event already in cmds "
        elif event in self.net:
            print("Error event already in edges ", event)
            raise "Error event already in edges "
        else:
            nodeTo.change_state=change_state
            self.cmds[event] = (nodeTo, desc)
            nodeTo.event_manager = self
            nodeTo._cmd =True

    # Agregamos un evento a la cola
    def putEvent(self, event, params=None, valid_until=0):  # lanzamos un evento ahora
        log.debug("putEvent:", event, "params:", params, "valid_until", valid_until) 
        if params == None:
            params = {}

        self.events.put((event, params, valid_until))

    # lanza un thread para leer de un callback en varias modalidades
    # que generaran eventos
    def watchEvent(self,event, # Evento que se generara 
                   event_params={}, # Parametros del evento
                   data_pattern=None, # patron buscado en el retorno del callback
                    callback_obj=None, # objeto del callback
                    callback_function_args={}, #paramatros de l afuncion de callback
                    mode="loop",period=1,
                    valid_until=0 #  validUntil
                ):
                watcher=SnWatcher(self,event,event_params,event_pattern=data_pattern, valid_until=valid_until)
                watcher.start(callback_obj,callback_function_args,mode,period)
                return watcher
    

    def graph(self, f, bold_event=None, filename=None):
        if filename !=None:
           f.write(f"//{filename}\n\n")            
        f.write("digraph { \n")
        f.write('  layout="dot" \n')
        f.write("  //rankdir=LR \n")
        f.write('  graph [ overlap="true" fontsize = 10 ] \n')
        f.write('  node [ style="rounded,filled" shape="rect" fillcolor="#0000a0", fontcolor=white ]\n')
        # print("write ", len(Node.nodelist), "nodes")
        for state in Node.nodelist:
            node = Node.nodelist[state]
            style = node.style
            if node.desc != "":
                style = 'tooltip="' + ttfmt(node.desc) + '" ' + style
            if state == self.currentState:
                style = style+' color=red penwidth=6.0 '
            elif state == self.prevState:
                style = style+' color=red penwidth=2.0 '
            if node._cmd == True:
                style = style+'fillcolor="#a0a0a0" ' 

            f.write('"%s" [%s]\n' % (state, style))

        # print("write ", len(self.net), "events")
        for event in self.net:
            for state_from in self.net[event]:
                state_to = self.net[event][state_from][0].state
                desc = self.net[event][state_from][1]

                tooltip = ""
                if desc != "":
                    tooltip = 'labeltooltip="' + ttfmt(desc) + '" tooltip="' + ttfmt(desc) + '"'

                if bold_event == event and state_from == self.prevState and state_to == self.currentState:
                    args="ERR"
                    try :
                        args = " " + json.dumps(self.currentArgs).replace('"', '\\"')
                    except:
                        pass
                    
                    f.write(
                        '"%s" -> "%s" [ label = "%s" fontcolor="red" %s ]\n'
                        % (state_from, state_to, event + args, tooltip)
                    )
                else:
                    f.write('"%s" -> "%s" [ label = "%s" %s  ]\n' % (state_from, state_to, event, tooltip))

        # print("write ", len(self.cmds), "commands")
        if len(self.cmds) > 0:
            f.write(
                '"*" [ label="" style="filled" fixedsize=true width=0.2 shape="circle" fillcolor="red" tooltip = "desde todos los estados" ]\n'
            )
            for event in self.cmds:
                state_to = self.cmds[event][0].state
                desc = self.cmds[event][1]

                tooltip = ""
                if desc != "":
                    tooltip = 'labeltooltip="' + ttfmt(desc) + '" tooltip="' + ttfmt(desc) + '"'

                if bold_event == event:
                    f.write('"*" -> "%s" [ label = "%s" fontcolor="red" %s ]\n' % (state_to, event, tooltip))
                else:
                    f.write('"*" -> "%s" [ label = "%s" %s ]\n' % (state_to, event, tooltip))

        f.write("}\n")
            
    def printGraph(self,bold_event=None):
        # Si ya hay archivo base lo renombramos al nombre historico
        filename = self.graphDir+"_"+datetime.now().strftime("%Y-%m-%d_%H:%M:%S_") + \
            str(self.count%10000).zfill(4)+"_"+str(self.graph_n%10000).zfill(4)+".dot"
        log.info("dotFile:",filename)
        self.graph_n=self.graph_n+1
        # Creamos el archivo con todos los permisos
        # The default umask is 0o22 which turns off write permission of group and others
        os.umask(0)

        desc = os.open(
            path=filename,
            flags=(
                os.O_WRONLY  # access mode: write only
                | os.O_CREAT  # create if not exists
                | os.O_TRUNC  # truncate the file to zero
            ),
            mode=0o666
        )

        with open(desc, 'w') as f:
            self.graph(f, bold_event, filename=filename)
    
    def readGraphFile(self, file, delta=0):
        dotList=glob.glob(self.graphDir+'*.dot')
        dotList.sort()
        
        index=-1
        if len(dotList) == 0:
            return ""        
        index=bisect.bisect_left(dotList,file)+delta
        if index < 0:
            index=0
        elif index >= len(dotList):
            index=-1
            
        nextfile= dotList[index]

        with open(nextfile, 'r') as content_file:
            return content_file.read()
        return ""
            
    def start(self, n_first: Node):
        n_start = Node(
            "_start_",
            desc="start",
            style='label="" style="filled" fixedsize=true width=0.2 shape="circle" fillcolor="green"',
        )
        self.linkEdge("_start_", n_start, n_first, desc="start")
        self.currentState = "_start_"
        self.currentNode=n_start
        threading.Thread(target=self.loop).start()
        self.putEvent("_start_")  # lanzamos evento de inicio

    def change_state_deprecated(self,event, params,node_to:Node):       
        self.currentNode=node_to
        self.prevState = self.currentState
        self.currentState = node_to.state
        self.currentArgs = params
        self.count = self.count + 1  # increment event count
        log.perfMark(f"     print graph")


    def do_change(self,event, params,node_to:Node):
        # copiamos por si leave o enter los modifica y reportar lo que llego
        original_params=copy.deepcopy(params) 


        # indicamos al nodo actual que salimos
        log.info("[",self.count,"] Leave:", self.currentNode.state)
        self.currentNode.leave(event,params,node_to.state)

        
        # Cambiamos de estado
        self.currentNode=node_to
        self.prevState = self.currentState
        self.currentState = node_to.state
        self.currentArgs = original_params
        self.count = self.count + 1  # increment event count

        # Entramos al nodo nuevo
        log.info("[",self.count,"] Enter:", node_to.state, params)
        node_to.enter(event, params, self.currentState)


        
    def loop(self):
        last_count=self.count-1
        log.debug( "main loop start, tid ",threading.get_native_id())
        try:
            self.printGraph()
            while True:
                if self.count == last_count:
                    log.notice("[",self.count,"] Same:", self.currentState)
                else:
                    log.notice("[",self.count,"] State:", self.currentState)
                last_count=self.count
                
                log.perfMark("event end:")
                eventTuple = self.events.get()
                event      = eventTuple[0]  # text del evento
                params     = eventTuple[1]  # argumentos del evento
                validUntil = eventTuple[2]  # valid Until

                log.perfMark(f"[%d] start event %s"%(self.count,event))
                

                if validUntil != 0 and validUntil < self.count:
                    log.notice("[",self.count,"] Caduced:", event, " ", validUntil, "<", self.count)
                else:
                    log.notice("[",self.count,"] Event:", event, params)
                    if event in self.net:
                        log.perfMark(f"     event in net")
                        if not self.currentState in self.net[event]:
                            log.warn("[",self.count,"] Invalid:", event, "not valid for state ", self.currentState, "discarted!")
                        else:
                            node_to: Node = self.net[event][self.currentState][0]
                            
                            self.do_change(event, params, node_to)                
                            
                            # Imprimimos el estado actual despues del enter
                            self.printGraph(event)
                    elif event in self.cmds:
                        log.info("[", self.count, "] Command:", event)
                        node_to: Node = self.cmds[event][0]
                        log.perfMark(f"     enter cmd")
                        if node_to.change_state:
                            self.do_change(event, params, node_to)
                        else:
                            log.info("[",self.count,"] Enter:", node_to.state, params)
                            node_to.enter(event, params, self.currentState)
                        self.printGraph(event)
                    else:
                        log.warn("[",self.count,"] Unknown:", event, " not exist")
        except Exception as e:
            log.error(e)
            log.error(traceback.format_exc())
            exit(1)

