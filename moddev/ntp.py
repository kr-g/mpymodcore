
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time
import ntptime

from modcore import modc, Module, LifeCycle
from modcore.log import LogSupport

from .timeout import Timeout


WLAN="wlan"
TZ="tz"
NTP_SYNC="ntp-sync"

class NTP(Module):
         
    def on_add(self):
        self.init()
        
    def init(self):
        self.offset = 0
        self._timeout = False
        self.retry_after = Timeout( 5 ) ## todo config
        
    def conf(self,config=None):
        if config!=None:
            self.set_tz_ofset( config.get("TZ"), fire_event=False ) # dont fire extra event
        
    def watching_events(self):
        return [WLAN,TZ,NTP_SYNC,] 

    def _settime(self):
        
        ## todo grace period for setting ntp time
        ## otherwise ntp is raise twice during startup
        ## 1. during ntp module startup when ntptime.settime() internal grace commits
        ## 2. when wlan event is reached
        
        try:
            ntptime.settime()
            self._timeout = False
            #self.retry_after.reset() ##todo config
            self.info( "ntp time", self.localtime() )
            self.fire_event( "ntp", True )
        except Exception as ex:
            self._timeout = True
            self.retry_after.restart()
            self.excep( ex, "ntp settime" )

    def loop(self,config=None,event=None):
        if self.current_level() != LifeCycle.RUNNING:
            return
        
        if self._timeout and self.retry_after.elapsed():
            self._settime()
        
        if event==None:
            return
        
        val = self.event_value(event)
        
        if self.is_event( event, WLAN ):
            if val:
                self._settime()
            else:
                # ntp lost
                self.fire_event( "ntp", False )
                
        if self.is_event( event, NTP_SYNC ):
            self._settime()
                
        if self.is_event( event, TZ ):
            if val:
                self.set_tz_ofset( val )
            else:
                self.set_tz_ofset( 0 )
     
    def utc(self):
        return time.time()

    def utctime(self):
        return time.localtime( self.utc() )

    def set_tz_ofset(self,offset,fire_event=True):
        try:
            offset = int(offset)
        except:
            offset = 0
        self.debug( "tz offset", offset )
        if self.offset != offset:
            self.info( "timezone", offset )
            if fire_event:
                self.fire_event( "ntp", True )
            self.offset = offset
    
    def time(self):
        return self.utc() + self.offset
        
    def localtime(self,cron_dow=False):
        local = time.localtime( self.time() )
        if cron_dow==True:
            local = list(local)
            local[6] += 1
        return local
    
    def cron_dow(self):
        """
            unix cron day of week
        """
        dow = time.localtime( self.time() )[6] + 1
        return dow
    
    
ntp_serv = NTP("ntp")
modc.add( ntp_serv )


def _timefunc():
    return ntp_serv.localtime()

def _utctimefunc():
    return ntp_serv.utctime()

def set_log_time(utc=False):
    LogSupport.timefunc = _utctimefunc if utc else _timefunc

set_log_time()



