
from modcore.log import LogSupport
from modext.fiber import FiberLoop, Fiber

from modext.http.webserv import WebServer, COOKIE_HEADER, SET_COOKIE_HEADER

from .filter import *
from .content import StaticFiles
from .router import Router
from .session import SessionStore

from .proc import Processor


store = SessionStore( )

class WindUp(LogSupport):
    
    def __init__(self, wrap_socket=None, suppress_id=False):
        LogSupport.__init__(self)
        self.suppress_id = suppress_id
        self.ws = WebServer(wrap_socket=wrap_socket)
        self._set_default()
        
    def _set_default(self):
        self.headerfilter = self.headerfilter_default()
        self.bodyfilter = self.bodyfilter_default()
        self.generators = self.generators_default()
        self.post_proc = self.post_proc_default()
        
        self.allowed=["GET","POST","PUT"]
        
        self.html404 = None
        
        self.exec_class = Processor

        self.calls = 0
        self.exec = []
        
    def start(self, generators=None ):        
        self.ws.start()
        self.info( 'listening on', self.ws.addr )
        if generators:
            self.generators.extend(generators)

    def stop(self):
        self.ws.stop()
        for e in self.exec:
            e.kill("stop")
            e.close()
        self.exec = []

    def headerfilter_default(self):
        # depending on app needs filter are added, or left out
        headerfilter = [
                        CookieFilter(),
                        store.pre_filter(),
                        # keep them together
                        PathSplitFilter(),
                        XPathDecodeFilter(),
                        ParameterSplitFilter(),
                        ParameterValueFilter(),
                        ParameterPackFilter(),
                        # optional
                        XPathSlashDenseFilter(),
                        # optional dense len(list)==1 to single element 
                        ParameterDenseFilter(),
                        #
                     ]
        return headerfilter
    
    def bodyfilter_default(self):
        bodyfilter = [
                    BodyTextDecodeFilter(),
                    JsonParserFilter(),
                    FormDataFilter(),
                    FormDataDecodeFilter(),
            ]
        return bodyfilter
    
    def generators_default(self):
        generators = [
                StaticFiles(["/www"], suppress_id=self.suppress_id ),
            ]
        return generators

    def post_proc_default(self):
        post_proc = [
                store.post_filter(),
            ]
        return post_proc
    
    def loop(self):

        req = None
        exec = None
        try:
            if self.ws.can_accept():
                
                req = self.ws.accept()                                                 
                self.calls += 1
                
                # create processor
                exec = self.exec_class( self )
                self.exec.append(exec)
                req_done = exec.run(req)
                self.info( "req_done", req_done )
                
                if req_done:
                    exec._after_run_done( req )      
                else:                   
                    exec._after_run_undone( req )
                    
        except Exception as ex:
            self.excep( ex )
            if exec!=None:
                exec.kill("run-fail")
                exec.close()
                self.exec.remove(exec)
            else:
                req.close()
            return

        for e in self.exec:
            try:
                if e.done()==True:
                    self.exec.remove(e)
                    
                    req = e.req
                    request = req.request  
                    self.info("run post proc")

                    try:
                        for f in self.post_proc:
                            f.filterRequest( request )
                    except Exception as ex:
                        self.excep( ex, "filter post-proc")
                        
                    e.close()

                    self.info("exec done", type(e))
                else:
                    self.info("pending exec", len(self.exec))
                    e.loop()
                    
            except Exception as ex:
                self.excep( ex )
                e.kill("post-proc-fail")
                e.close()
                self.exec.remove(e)
                  
    def call404(self,req):
        self.warn("not found 404", req.request.xpath )
        if self.html404==None:
            req.send_response( status=404, suppress_id=self.suppress_id )
        else:
            # custom 404 page
            # req gets destructed by next round
            self.html404( req )
        
        