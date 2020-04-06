
"""
stand alone sample webserver

to start call from repl:

from modext.webserv.serve import serve
serve()

with curl

curl http://your-ip
curl http://your-ip/index.html -X POST -d "test-data"


"""
import time

from modcore.log import logger
from .webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
from .filter import PathSplitFilter, ParameterSplitFilter, \
     ParameterValueFilter, ParameterPackFilter, CookieFilter
from .content import StaticFiles

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
    </body>
</html>
"""

known_clients = {}

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
                    #
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
                        req.load_content()
                        
                        request = req.request
                        for f in webfilter:
                            f.filterRequest( request )
                        
                        logger.info( request.xcookies )
                        logger.info( request.xpath, request.xquery )
                        logger.info( request.xparam )
                        logger.info( request.xkeyval )
                        logger.info( request.xpar )                      
                        
                        body = req.get_body()
                        if body!=None:
                            logger.info( "request content", body.decode() )
                          
                        # show board unique id in http server header
                        suppress_info=False    
                            
                        statf = StaticFiles(["/www"], suppress_id=suppress_info )
                        if statf.handle( req ):
                            continue                        
                        
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


