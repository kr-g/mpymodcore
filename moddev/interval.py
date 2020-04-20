
import time

from modcore import modc, Module, LifeCycle

from .eventemitter import EventEmitter
from .timeout import Timeout


TIME_BASE = 1000

class Interval(EventEmitter):

    def on_add(self):
        self.timer = Timeout( None, TIME_BASE )
        
    def conf(self,config=None):
        if config!=None:
            
            # important. call config of EventEmitter
            super().conf(config)
            
            timeout = config.get( self.id, None ) ##todo None?
            timebase = config.get( self.id + ":timebase", TIME_BASE )
            
            self.timeout = Timeout( timeout, timebase )            
            self.info("period", self.timeout )
            
        if self.timer.configured()==False:
            self.warn("timeout not configured")
            
    def start(self):
        self.timeout.restart()
    
    def __emit__(self,config=None):

        if self.timeout.elapsed():
            self.timer.restart()
            return self.__timeout__(config=config) or True
    
    # overload this, return True if outer event shoud emitted
    def __timeout__(self,config=None):
        pass
    
