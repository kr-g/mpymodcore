
import time

from machine import Pin

from modcore import modc, Module, LifeCycle

from .eventemitter import EventEmitter
from .timeout import Timeout


def _ticks():
    return time.ticks_ms()

def _diff(t1,t2):
    return time.diff_ticks(t1,t2)


class Button(EventEmitter):

    def init(self):
        
        super().init()
        
        self.check_lifecycle = False ##todo ?
        
        self.pin = None
        self.neg_logic = False
        self.debounce = Timeout( None )
        
        self.pressed = None
        self.last_state = False

    def conf(self,config=None):
                
        if config!=None:
            
            # important. call config of EventEmitter
            super().conf(config)
            
            pin = config.get( self.id, None ) ##todo None?
            pin = int(pin)
            if pin!=None:
                self.pin = Pin(pin,Pin.IN)
            self.info("pin", pin )
            
            self.neg_logic = config.get( self.id + ":neg_logic", self.neg_logic )
            self.info("neg_logic", self.neg_logic )
            
            debounce = config.get( self.id + ":debounce", 100 ) # 100ms debounce
            debounce = int(debounce)
            
            self.debounce = Timeout( debounce, 1 ) # 1ms timebase          
            self.info("debounce ms", self.debounce )
         
        if self.pin==None:
            self.warn("pin not configured")
            
    def start(self):
        self.pressed = None
        self.last_state = False    
    
    def __emit__(self,config=None):
        
        if self.pin==None:
            return
        
        signaled = self.pin.value() ^ self.neg_logic
        if signaled == self.last_state and self.pressed==None:
            return
        
        self.last_state = signaled
        
        if self.pressed==None:
            self.info("pressed")
            self.pressed = _ticks()
            self.debounce.restart()
            return
        
        if self.debounce.elapsed() and not signaled:            
            self.info("released")
            self.pressed = None
            return self.__timeout__(config=config) or True
    
    # overload this, return True if outer event shoud emitted
    def __timeout__(self,config=None):
        pass
    

