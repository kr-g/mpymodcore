
import os

from modcore.log import LogSupport
from .webserv import RequestHandler
from .http_func import BadRequestException


class ContentGenerator(LogSupport):
    
    def __init__(self):
        LogSupport.__init__(self)
        
    def handle(self,request):
        pass
    

class StaticFiles(ContentGenerator):

    def __init__( self, static_paths=None, suppress_id=False ):
        LogSupport.__init__(self)
        self.static_paths = static_paths
        self.suppress_id = suppress_id

    def handle(self,req):
        
        if self.static_paths==None or len(self.static_paths)==0:
            return
        
        request = req.request
        path = request.xpath
        
        if path[0]!="/":
            raise BadRequestException("malformed path", path )
        
        if not self._handle_index( req, path ):                
            return self._handle_file( req, path )
        return True

    def _handle_index(self,req,path):
        if path.endswith("/"):
            path += "index"
        if path.endswith("/index"):
            for p in [".html",".htm"]:
                fp = path + p
                if self._handle_file( req, fp ):
                    return True

    def _handle_file(self,req,path):
        for p in self.static_paths:
            fp = p + path
            try:
                ## todo checking valid path
                self.info( "check path", "'"+fp+"'" )
                if StaticFiles.is_file(fp):
                    self.info( "found", fp )
                    self.send_file( req, fp )
                    self.info( "send", fp )
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
    
    
    