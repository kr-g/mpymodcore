
import time

from modcore import modc, Module, LifeCycle

from .timeout import Timeout


TIME_BASE = 1000

class Interval(Module):

    def on_add(self):
        self.timer = Timeout( None, TIME_BASE )
        
    def conf(self,config=None):
        if config!=None:
            
            timeout = config.get( self.id, None ) ##todo None?
            timebase = config.get( self.id + ":timebase", TIME_BASE )
            
            self.timeout = Timeout( timeout, timebase )
            self.event = config.get( self.id + ":event", None )
            
            self.info("config", self.timeout, "event:", self.event )
            
        if not self.timeout.configured():
            self.warn( "interval not configured" )

    def start(self):
        self.timeout.restart()
    
    def __loop__(self,config=None,event=None,data=None):
        
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self.timeout.elapsed():
            self.timer.restart()
            if self.event!=None:
                self.fire_event(self.event)
            return self.__timeout__(config=config)
    
    def __timeout__(self,config=None):
        pass
    
