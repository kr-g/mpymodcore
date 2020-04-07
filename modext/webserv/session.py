
import time

from modcore.log import LogSupport
from .filter import Filter


SID = "xsession_id"
EXPIRES = "xsession_expires"
CREATED = "xsession_created"
TIMEOUT = 60*60*30
    
        
class SessionLoad(Filter):
    
    def __init__(self, session_store, cleanup=None):
        Filter.__init__(self,cleanup=cleanup)
        self.session_store = session_store
        
    def filterRequest( self, request ):
        
        coky = self.session_store.cookie_name
        
        created = False
        
        if request.xcookies==None:
            request.xcookies = {}
        
        sid = request.xcookies.get(coky)
        
        if sid==None:
            created = True
            sid = self.session_store.create()
        
        sess = self.session_store.load(sid)
        
        if sess==None:
            created = True
            sid = self.session_store.create()            
            sess = self.session_store.load(sid)
            
        if created:
            request.xcookies[coky] = sess
        
        request.xsession_cookie = self.session_store.cookie_name
        request.xsession_is_new = created
        request.xsession_id = sid
        request.xsession = sess
        
        self.info( "sid", request.xsession_id, "created", request.xsession_is_new )
        

class SessionSave(Filter):
    
    def __init__(self, session_store, cleanup=None):
        Filter.__init__(self,cleanup=cleanup)
        self.session_store = session_store

    def filterRequest( self, request ):
        
        if request.xsession==None:
            if request.xsession_id!=None:
                self.session_store.destroy( request.xsession_id )
        else:
            self.session_store.store( request.xsession_id, request.xsession )                   
        
        self.info( "sid", request.xsession_id )
 
 
class SessionStore(LogSupport):
            
    def __init__(self,cookie_name="sessionid", expires_after=TIMEOUT, cleanup=None):
        LogSupport.__init__(self)
        self.cookie_name = cookie_name
        self.expires_after = expires_after
        self.sessions = {}
        self.cleanup = cleanup
        
    def _create_id(self):
        sessionid = str(time.ticks_us()) \
                    + "_" + str( time.ticks_cpu() ) \
                    + "_" + str( time.ticks_ms() )
        return sessionid
    
    def renew(self,session):
        session.update( { EXPIRES : time.time() + self.expires_after } )
    
    def create(self):
        while True:
            sid = self._create_id()
            if sid not in self.sessions:
                break
            self.warn("ups...")
            
        session = { SID : sid, CREATED : time.time() }
        self.renew(session)
        self.sessions[sid] = session
        return sid
    
    def load(self,sid):
        session = self.sessions.get(sid,None)
        if session==None:
            return
        exp = session.get(EXPIRES, time.time()-153 ) 
        now = time.time()
        if now>exp:
            self.destroy(sid)
            return        
        self.renew(session)
        return session
    
    def cleanup_expired(self):
        now = time.time()
        for sid,session in self.sessions.items():
            exp = session.get(EXPIRES, time.time()-153 )             
            if now>exp:
                self.destroy(sid)                  
    
    def store(self,sid,session):
        session = self.sessions.get(sid,None)
        if session==None:
            return        
        self.sessions[sid] = session
        
    def destroy(self,sid):
        session = self.sessions.get(sid,None)
        if session==None:
            return        
        del self.sessions[sid]

    def pre_filter(self):
        return SessionLoad(self,cleanup=self.cleanup)
    
    def post_filter(self):
        return SessionSave(self,cleanup=self.cleanup)

         
        