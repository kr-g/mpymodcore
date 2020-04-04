
import time

from modcore import modc, Module, LifeCycle


TIME_BASE = 1000

class Interval(Module):

    def on_add(self):
        self._call_every = None
        self._time_base = TIME_BASE
        
    def conf(self,config=None):
        if config!=None:
            self._call_every = config.get( self.id, None )
            self._time_base = config.get( self.id + "_timebase", TIME_BASE )
        if self._call_every == None:
            self.warn( "interval not configured" )

    def start(self):
        self._last_call = time.ticks_ms()
    
    def __loop__(self,config=None,event=None,data=None):
        
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self._call_every == None:
            return
        
        now = time.ticks_ms() 
        
        if time.ticks_diff( now, self._last_call ) >= self._call_every * self._time_base:
            self._last_call = now
            return self.__timeout__(config=config)
    
    def __timeout__(self,config=None):
        pass
    
