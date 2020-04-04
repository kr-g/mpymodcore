
import time
import ntptime

from modcore import modc, Module, LifeCycle
from modcore.log import LogSupport


class NTP(Module):
         
    def on_add(self):
        self.init()
        
    def init(self):
        self.offset = 0
        self._timeout = False
        
    def conf(self,config=None):
        if config!=None:
            self.set_tz_ofset( config.get("TZ") )
        
    def watching_events(self):
        return ["WLAN","TZ"] # case does not matter

    def _settime(self):
        try:
            ntptime.settime()
            self._timeout = False
            self.info( "ntp time", self.localtime() )
        except Exception as ex:
            self._timeout = True
            self.excep( ex, "ntp settime" )
        self.fire_event( "ntp", not self._timeout )

    def loop(self,config=None,event=None):
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self._timeout:
            self._settime()
        
        if event==None:
            return        
        val = self.event_value(event)
        
        if self.is_event( event, "wlan" ):
            if val:
                self._settime()
            else:
                self.fire_event( "ntp", False )
                
        if self.is_event( event, "tz" ):
            if val:
                self.set_tz_ofset( val )
            else:
                self.set_tz_ofset( 0 )
     
    def utc(self):
        return time.time()

    def utctime(self):
        return time.localtime( self.utc() )

    def set_tz_ofset(self,offset):
        try:
            offset = int(offset)
        except:
            offset = 0
        self.debug( "tz offset", offset )
        self.offset = offset
    
    def time(self):
        return self.utc() + self.offset
        
    def localtime(self):
        return time.localtime( self.time() )
    
    
ntp_serv = NTP("ntp")
modc.add( ntp_serv )


def _timefunc():
    return ntp_serv.localtime()

def _utctimefunc():
    return ntp_serv.utctime()

def set_log_time(utc=False):
    LogSupport.timefunc = _utctimefunc if utc else _timefunc

set_log_time()



