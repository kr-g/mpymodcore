
import time

from modcore import modc, Module, LifeCycle


class EventEmitter(Module):

    def init(self):
        self.event = None
        
    def conf(self,config=None):
        if config!=None:
            
            self.event = config.get( self.id + ":event", None )
            self.info("event:", self.event )
     
    def split_event_data(self,eventdata):
        pos = eventdata.find(":")
        if pos<0:
            return eventdata, None
        return eventdata[:pos], eventdata[pos+1:]
     
    def __loop__(self,config=None,event=None,data=None):
        
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self.__loop2__(config,event,data)==False:
            return
        
        if self.__emit__(config)==True:
            if self.event!=None:
                event, data = self.split_event_data( self.event )
                self.fire_event(event,data)

    # overload this if required, return False to return with call emit
    def __loop2__(self,config=None,event=None,data=None):
        pass

    # overload this and return True for emitting the event
    def __emit__(self,config=None):
        pass
    
    