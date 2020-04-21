
from modcore import modc, Module, LifeCycle

from .session import purge_expired


SESSION_CLR="session-man"

class SessionManager(Module):

    def watching_events(self):
        return [SESSION_CLR,]
    
    def __loop_event__(self,config=None,event=None,data=None):
        
        if event==SESSION_CLR:
            self.info("purge expired")
            purge_expired()
            self.info("purge done")
            
        
session_man = SessionManager(SESSION_CLR)
modc.add( session_man )

