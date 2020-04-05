
import time

class Timeout():
    
    def __init__(self,timeout=None,timebase=1000):
        self.timebase = timebase
        self.reset(timeout)
                        
    def reset(self,timeout=None):
        self.timeout = timeout
        self.last_call = time.ticks_ms()
      
    def restart(self):
        self.reset(self.timeout)
        
    def configured(self):
        return self.timeout != None
        
    def elapsed(self):
        
        if self.timeout == None:
            return False
        
        now = time.ticks_ms()
        
        if time.ticks_diff( now, self.last_call ) >= self.timeout * self.timebase:
            self.restart()
            return True
        
        return False
   
   