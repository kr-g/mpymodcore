import sys
import time

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

#

_logstr = {
    CRITICAL : "CRITICAL",
    ERROR    : "ERROR",
    WARNING  : "WARNING",
    INFO     : "INFO",
    DEBUG    : "DEBUG",
    NOTSET   : None,
}

def _timefunc():
    return time.localtime( time.time() )

class LogSupport(object):

    timefunc = _timefunc
    
    level = INFO
    showdate = True
    showtime = True

    def __init__(self, level=None ):
        self.log_level( level )
        self.logname = self.__qualname__
        self.showtime = LogSupport.showtime

    def log_level(self,level=None):
        self._log_level = level if level != None else LogSupport.level

    @staticmethod
    def global_level(level):
        LogSupport.level = level

    def _timestr(self):
        tm = LogSupport.timefunc()[0:6]
        ds = "%04d%02d%02d" % tm[0:3] if LogSupport.showdate else ""
        ls = "-" if LogSupport.showdate else ""
        ts = "%02d%02d%02d" % tm[3:6] 
        return ds + ls +ts

    def _loglevel( self, level ):
        return level >= self._log_level

    def _log( self, level, *args ):
        if len( args ) == 0:
            return self._loglevel( level )
        if self._loglevel( level ):
            self._log2( _logstr[level], *args )
            
    def _log2( self, infostr, *args ):
        if self.showtime:
            print( self._timestr(), end=':' )
        if infostr:
            print( infostr, end=':' )
        print( self.logname, end=':' )
        if "id" in self.__dict__:
            print( self.id, end=':' )
        print( *args )

    def debug( self, *args ):
        return self._log( DEBUG, *args )
    def info( self, *args ):
        return self._log( INFO, *args )
    def warn( self, *args ):
        return self._log( WARNING, *args )
    def error( self, *args ):
        return self._log( ERROR, *args )
    def critical( self, *args ):
        return self._log( CRITICAL, *args )
    
    def excep( self, ex, *args ):
        self.critical( *args )
        sys.print_exception( ex )     


logger = LogSupport()
logger.logname = "main"

          



