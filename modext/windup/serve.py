"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

from samples.web_sample import *

from modcore.log import logger
from modcore.fiber import FiberLoop, Fiber

from .webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
from .filter import *
from .content import StaticFiles
from .router import Router
from .session import SessionStore

"""
store = SessionStore( )

def serve():
    
    ws = WebServer()
    ws.start()
    logger.info( 'listening on', ws.addr )
    
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
    
    bodyfilter = [
                BodyTextDecodeFilter(),
                JsonParserFilter(),
                FormDataFilter(),
                FormDataDecodeFilter(),
        ]
    
    generators = [
            # serve same static file also under /stat prefixed root
            StaticFiles(["/www"], root="/stat", suppress_id=suppress_info ),
            # place none-root at end -> performance
            StaticFiles(["/www"], suppress_id=suppress_info ),
            router,
            abc_router,
            fiber_router,
        ]
    
    post_proc = [
            store.post_filter(),
        ]
    
    try:
        calls = 0
        pending_requests = []
        done_requests = []
        while True:
            req = None
            try:
                if ws.can_accept():
                    
                    req = ws.accept() 
                        
                    calls += 1
                    
                    req.load_request(allowed=["GET","POST","PUT"])
                    
                    # when logging use argument list rather then
                    # concatenate strings together -> performace
                    
                    logger.info( "request" , req.request )
                    logger.info( "request content len", len( req ) )
                    #req.load_content()
                    
                    req.fiberloop = FiberLoop()
                    
                    request = req.request
                    for f in headerfilter:
                        f.filterRequest( request )
                    
                    # check logging level...
                    if logger.info():
                        logger.info( "cookies",request.xcookies )
                        logger.info( "xsession_is_new", request.xsession_is_new )
                        logger.info( "xpath, xquery", request.xpath, request.xquery )
                        logger.info( "xparam", request.xparam )
                        logger.info( "xkeyval", request.xkeyval )
                        logger.info( "xpar", request.xpar )                      

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
                        logger.warn("no auto content loading. size=", len(req))
                        logger.warn("not all req.x-fields area available")
                    else:
                        for f in bodyfilter:
                            f.filterRequest( request )
                    
                    # after auto cleanup with filter this can be None
                    body = req.request.body 
                    if body!=None:
                        logger.info( "request content", body )
                      
                    req_done = False
                    for gen in generators:
                        req_done = gen.handle( req )
                        if req_done:
                            break
                                                  
                    logger.info( "req_done", req_done )
                    if req_done:
                        # schedule for post processing
                        pending_requests.append( req )
                    else:
                        # not found send 404
                        done_requests.append(req)
                        logger.warn("not found 404", request.xpath )
                        req.send_response( status=404, suppress_id=suppress_info )
                        
            except Exception as ex:
                logger.excep( ex )
                if req!=None:
                    done_requests.append(req)

            try:
                if len(pending_requests)>0:
                    logger.info("pending requests", len(pending_requests))
                    for req in pending_requests:
                        request = req.request
                        try:
                            if req.fiberloop!=None and req.fiberloop.all_done():
                                logger.info("run post proc")
                                for f in post_proc:
                                    ## todo fiber
                                    f.filterRequest( request )
                                    
                                pending_requests.remove( req )
                                done_requests.append( req )
                            else:
                                logger.info( "exe fiberloop" )
                                for status_change in req.fiberloop:
                                    # do something with status_change
                                    # and stop after the first loop 
                                    break
                                logger.info( "exe fiberloop done" )
                                
                        except Exception as ex:
                            logger.excep( ex, "post processing failed" )
                            if req.fiberloop!=None:
                                floop = req.fiberloop
                                # set to None if kill_all fails drop next round
                                req.fiberloop=None
                                floop.kill_all("postfail")
                                
                            pending_requests.remove( req )
                            done_requests.append( req )
                        
                if len(done_requests)>0:
                    logger.info("done requests", len(done_requests))
                    for req in done_requests:
                        done_requests.remove(req)
                        req.close()
                        
            except Exception as ex:
                logger.excep( ex )
                 
    except KeyboardInterrupt:
        logger.info("cntrl+c")        
    finally:
        ws.stop()


"""
