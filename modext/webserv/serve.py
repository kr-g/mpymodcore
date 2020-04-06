
"""
stand alone sample webserver

to start call from repl:

from modext.webserv.serve import serve
serve()

with curl

curl http://yourip
curl http://yourip/index.html 

curl http://yourip/special 
curl http://yourip/special -X POST -d "test-data"

more then one 'a' parameter here
curl 'http://yourip/special/app?a=5&b=6&a=7' 

json needs doule-quotes !
curl http://yourip/json -X POST -d '{"hello":"world"}' -H "Content-Type: application/json"

form data
curl http://yourip/form -X POST -d 'field1=value1&field2=value2' -H "Content-Type: application/x-www-form-urlencoded"


"""
import time

from modcore.log import logger
from .webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
from .filter import *
from .content import StaticFiles
from .router import Router


html = """<!DOCTYPE html>
<html>
    <head>
        <title>modcore web server</title>
    </head>
    <body>
        <h1>welcome</h1>
        <h2>modcore is up and running :-)</h2>
        
        <div>hello world</div>
        <div>&nbsp;</div>        
        <div>number of visits: %s</div>
        <div>&nbsp;</div>        
        <div>this is a dummy page since your request was not processed</div>        
    </body>
</html>
"""

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


def serve():
    
    ws = WebServer()
    ws.start()
    logger.info( 'listening on', ws.addr )
    
    # depending on app needs filter are added, or left out
    webfilter = [
                    CookieFilter(),
                    # keep them together
                    PathSplitFilter(),
                    ParameterSplitFilter(),
                    ParameterValueFilter(),
                    ParameterPackFilter(),
                    # optional dense len(list)==1 to single element 
                    ParameterDenseFilter(),
                    #
                 ]
    
    contentfilter = [
                BodyTextDecodeFilter(),
                JsonParserFilter(),
                FormDataFilter(),
        ]
    
    webcontent = [
            StaticFiles(["/www"], suppress_id=suppress_info ),
            router,
        ]
    
    try:
        calls = 0
        while True:
            try:
                if ws.can_accept():
                    with ws.accept() as req:
                        
                        calls += 1
                        
                        req.load_request(allowed=["GET","POST","PUT"])
                        logger.info( "request" , req.request )
                        logger.info( "request content len", len( req ) )
                        #req.load_content()
                        
                        request = req.request
                        for f in webfilter:
                            f.filterRequest( request )
                        
                        # check logging level...
                        if logger.info():
                            logger.info( "cookies",request.xcookies )
                            logger.info( "xpath, xquery", request.xpath, request.xquery )
                            logger.info( "xparam", request.xparam )
                            logger.info( "xkeyval", request.xkeyval )
                            logger.info( "xpar", request.xpar )                      
                        
                        req.load_content()
                        for f in contentfilter:
                            f.filterRequest( request )
                        
                        # after auto cleanup with filter this can be None
                        body = req.request.body 
                        if body!=None:
                            logger.info( "request content", body )
                          
                        req_done = False
                        for gen in webcontent:
                            req_done = gen.handle( req )
                            if req_done:
                                break
                        logger.info( "req_done", req_done )
                        if req_done:
                            continue
                        
                        # not really important from here on...
                        
                        header = None
                        
                        COKY="my-cookie"                        
                        if request.xcookies==None or COKY not in request.xcookies:
                            # send cookie if none coming from the browser
                            header = req.set_cookie( header, COKY, time.time() )
                            logger.info( header )
                            
                        # always delete this cookie
                        header = req.set_cookie( header, "dmy-cookie", None )
                        
                        # dummy page
                        data = html % str(calls)
                        req.send_response( response=data, header=header, \
                                           suppress_id=suppress_info )
                    
            except BadRequestException as ex:
                logger.excep( ex )
                
            except Exception as ex:
                logger.excep( ex )
                
    except KeyboardInterrupt:
        logger.info("cntrl+c")        
    finally:
        ws.stop()


