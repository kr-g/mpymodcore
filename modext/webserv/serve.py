
"""
stand alone sample webserver

to start call from repl:

from modext.webserv.serve import serve
serve()

with curl

curl http://yourip
curl http://yourip/index.html 
curl http://yourip/app

curl http://yourip/special 
curl http://yourip/special -X POST -d "test-data"

more then one 'a' parameter here
curl 'http://yourip/special/app?a=5&b=6&a=7' 

json needs doule-quotes !
curl http://yourip/json -X POST -d '{"hello":"world"}' -H "Content-Type: application/json"

form data
curl http://yourip/form -X POST -d 'field1=value1&field2=value2' -H "Content-Type: application/x-www-form-urlencoded"


curl http://yourip/abc/app

curl 'http://yourip/user/your-name/id/your-date/ending'


"""
import time

from modcore.log import logger
from modcore.fiber import FiberLoop, Fiber

from .webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
from .filter import *
from .content import StaticFiles
from .router import Router
from .session import SessionStore


# show board unique id in http server header
suppress_info=False    

router = Router( suppress_id=suppress_info )

# accepts get and post 
@router("/app")
def my_app( req, args ):
    data = """
            <h1>from the router </h1>
            <div> query parameter = %s </div>
            """ % repr( args )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

@router.get("/special")
def my_get( req, args ):
    data = """
            <h1>get from the router </h1>
            <div> query parameter = %s </div>
            """ % repr( args )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

# same path as above
@router.post("/special")
def my_post( req, args ):
    
    body = req.get_body()
    
    data = """
            <h1>post from the router </h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args ), repr( body ), type( body ) )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

@router.post("/json")
def my_json( req, args ):
    
    body = req.request.xjson
    
    data = """
            <h1>json from the router </h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args ), repr( body ), type( body ) )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

@router.get("/form")
def my_form( req, args ):
    
    data = """
            <!DOCTYPE html>
            <html>
            <body>

            <h2>HTML Form</h2>

            <form action="/form" method="POST">
              <label for="fname">First name:</label><br>
              <input type="text" id="fname" name="fname" value="John"><br>
              <label for="lname">Last name:</label><br>
              <input type="text" id="lname" name="lname" value="Doe"><br><br>
              <input type="submit" value="Submit">
            </form> 

            <p>If you click the "Submit" button, the form-data will be sent.</p>

            </body>
            </html>            
            """ 
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

@router.post("/form")
def my_form( req, args ):
    
    body = req.request.xform
    
    data = """
            <h1>form data from the router </h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args ), repr( body ), type( body ) )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )


# rest style url 
@router.xget("/user/:user/id/:userid/ending")
def my_form( req, args ):
    
    body = req.request.xurl
    
    data = """
            <h1>rest url data from the router </h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args ), repr( body ), type( body ) )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

# create a new router
abc_router = Router( root="/abc", suppress_id=suppress_info )

# see at the notation of the next decorators
# it is e.g.
# @_name_of_the_router_variable_.get(...)
# @_name_of_the_router_variable_.post(...)
# etc

# accepts get and post 
@abc_router("/app")
def my_app( req, args ):
    data = """
            <h1> new router available under /abc/app </h1>
            <div> query parameter = %s </div>
            """ % repr( args )
    logger.info(data)
    req.send_response( response=data, suppress_id=suppress_info )

@abc_router("/appgen")
def my_gen( req, args ):
    data = """
            <h1> new router available under /abc/appgen </h1>
            <div> query parameter = %s </div>
            """ % repr( args )
    logger.info(data)
    
    def _chunk():
        lines = data.splitlines()
        for l in lines:
            yield l

    # generate content with generator func
    req.send_response( response_i=_chunk, suppress_id=suppress_info )


# new router
fiber_router = Router( root="/fiber", suppress_id=suppress_info )

@fiber_router.get("/simple")
def my_simple_fiber( req, args ):
    
    body = req.request.xform
    
    def fibered():
        data = """
                <h1>html page generated by fiber post processing</h1>
                <div> query parameter = %s </div>
                """ % ( repr( args ), )
        logger.info(data)
        req.send_response( response=data, suppress_id=suppress_info )
        #
        yield
        
    req.fiberloop.add( Fiber( fibered() ) )

@fiber_router.get("/complex")
def my_complex_fiber( req, args ):
    
    body = req.request.xform
    
    def fibered():
        
        # several yield statements inbetween...
        # always cause others to process
        
        req.send_head( suppress_id=suppress_info )
        
        yield
        
        data = """
                <h1>html page generated by fiber post processing</h1>
                <h2>submitting single lines</h2>
                <div> query parameter = %s </div>
                """ % ( repr( args ), )
        logger.info(data)
        logger.info("splitting lines now")

        lines = data.splitlines()
        
        yield
        
        for line in lines:
            # this is of course slow since data packages sent are small
            # http overhead for sending counts here 
            req.send_data(line)            
            yield 
        
    req.fiberloop.add( Fiber( fibered() ) )
    


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
                        logger.warn("not found 404", request.xpath )
                        req.send_response( status=404, suppress_id=suppress_info )
                        
            except Exception as ex:
                logger.excep( ex )

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


