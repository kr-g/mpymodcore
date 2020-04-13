
from modcore.log import LogSupport
from modcore.fiber import FiberLoop, Fiber

from .webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
from .filter import *
from .content import StaticFiles
from .router import Router
from .session import SessionStore


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

        self.calls = 0
        self.pending_requests = []

    def start(self,generators=None):        
        self.ws.start()
        self.info( 'listening on', self.ws.addr )
        if generators:
            self.generators.extend(generators)

    def stop(self):
        self.ws.stop()
        for req in self.pending_requests:
            req.fiberloop.kill_all("stop")
            req.close()
        self.pending_requests = []

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
        done_requests = []
        req = None
        try:
            if self.ws.can_accept():
                
                req = self.ws.accept() 
                                                
                self.calls += 1
                
                req.load_request(self.allowed)
                
                # when logging use argument list rather then
                # concatenate strings together -> performace
                
                self.info( "request" , req.request )
                self.info( "request content len", len( req ) )
                #req.load_content()
                
                req.fiberloop = FiberLoop()
                
                request = req.request
                for f in self.headerfilter:
                    f.filterRequest( request )
                
                # check logging level...
                if self.info():
                    self.info( "cookies",request.xcookies )
                    self.info( "xsession_is_new", request.xsession_is_new )
                    self.info( "xpath, xquery", request.xpath, request.xquery )
                    self.info( "xparam", request.xparam )
                    self.info( "xkeyval", request.xkeyval )
                    self.info( "xpar", request.xpar )                      

                req.load_content( max_size=4096 )
                if req.overflow == True:
                    # if bodydata is too big then no data is loaded automatically
                    # dont run body filters automatically if max size exceeds
                    # if a request contains more data the generator
                    # needs to decide what to do in detail
                    #
                    # some req.x-fields are then not available !!!
                    # because each filter sets them on its own !!!
                    #
                    self.warn("no auto content loading. size=", len(req))
                    self.warn("not all req.x-fields area available")
                else:
                    for f in self.bodyfilter:
                        f.filterRequest( request )
                
                # after auto cleanup with filter this can be None
                body = req.request.body 
                if body!=None:
                    self.info( "request content", body )
                  
                req_done = False
                for gen in self.generators:
                    req_done = gen.handle( req )
                    if req_done:
                        break
                                              
                self.info( "req_done", req_done )
                if req_done:
                    # schedule for post processing
                    self.pending_requests.append( req )
                else:
                    # not found send 404
                    done_requests.append(req)
                    self.warn("not found 404", request.xpath )
                    req.send_response( status=404, suppress_id=self.suppress_id )
                    
        except Exception as ex:
            self.excep( ex )
            if req!=None:
                done_requests.append(req)

        try:
            if len(self.pending_requests)>0:
                self.info("pending requests", len(self.pending_requests))
                for req in self.pending_requests:
                    request = req.request
                    try:
                        if req.fiberloop!=None and req.fiberloop.all_done():
                            self.info("run post proc")
                            for f in self.post_proc:
                                ## todo fiber
                                f.filterRequest( request )
                                
                            self.pending_requests.remove( req )
                            done_requests.append( req )
                        else:
                            self.info( "exe fiberloop" )
                            for status_change in req.fiberloop:
                                # do something with status_change
                                # and stop after the first loop 
                                break
                            self.info( "exe fiberloop done" )
                            
                    except Exception as ex:
                        self.excep( ex, "post processing failed" )
                        if req.fiberloop!=None:
                            floop = req.fiberloop
                            # set to None if kill_all fails drop next round
                            req.fiberloop=None
                            floop.kill_all("postfail")
                            
                        self.pending_requests.remove( req )
                        done_requests.append( req )
                    
            if len(done_requests)>0:
                self.info("done requests", len(done_requests))
                for req in done_requests:
                    done_requests.remove(req)
                    req.close()
                    
        except Exception as ex:
            self.excep( ex )
                 
        