
import os

from modcore.log import LogSupport
from .webserv import RequestHandler


class ContentGenerator(LogSupport):
    
    def __init__(self):
        LogSupport.__init__(self)
        
    def handle(self,request):
        pass
    
    
class StaticFiles(ContentGenerator):

    def __init__(self,static_paths=None, suppress_id=False ):
        LogSupport.__init__(self)
        self.static_paths = static_paths
        self.suppress_id = suppress_id

    def handle(self,req):
        
        request = req.request
        
        if self.static_paths==None or len(self.static_paths)==0:
            return
        
        if request.xpath[0]!="/":
            self.warn("malformed path", request.xpath )
            return
        
        for p in self.static_paths:
            fp = p + request.xpath
            try:
                ## todo checking valid path
                self.info( "check path", "'"+fp+"'" )
                if StaticFiles.is_file(fp):
                    self.send_file( req, fp )
                    return True
            except Exception as ex:
                self.excep( ex )
    
    @staticmethod
    def is_file(fnam):
        try:
            stat = os.stat( fnam )
            return stat[0] == 0x8000
        except Exception as ex:
            pass
            #self.excep( ex )
        return False
    
    def send_file( self, request, path ):
        
        with open(path) as f:
            c = f.read()
            request.send_response( response=c, suppress_id=self.suppress_id )
    
    
    