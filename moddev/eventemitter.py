
import time

from modcore import modc, Module, LifeCycle


class EventEmitter(Module):

    def init(self):
        self.event = None
        
    def conf(self,config=None):
        if config!=None:
            
            self.event = config.get( self.id + ":event", None )
            self.info("event:", self.event )
            
    def __loop__(self,config=None,event=None,data=None):
        
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self.__emit__(config)==True:
            if self.event!=None:
                self.fire_event(self.event)

    # overload this and return True for emitting the event
    def __emit__(self,config=None):
        pass
    
    