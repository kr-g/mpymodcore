
"""
stand alone sample webserver

to start call from repl:

from modext.webserv.serve import serve
serve()

with curl

curl http://your-ip
curl http://your-ip/index.html -X POST -d "test-data"


"""

from modcore.log import logger
from .webserv import WebServer, BadRequestException
from .filter import PathSplitFilter, ParameterSplitFilter, \
     ParameterValueFilter, ParameterPackFilter
from .content import StaticFiles

html = """<!DOCTYPE html>
<html>
    <head>
        <title>modcore web server</title>
    </head>
    <body>
        <h1>welcome</h1>
        <h2>mod core is up and running :-)</h2>
        
        <div>hello world</div>
        <div>&nbsp;</div>
        
        <div>number of visits: %s</div>
    </body>
</html>
"""

def serve():
    
    ws = WebServer()
    ws.start()
    logger.info( 'listening on', ws.addr )
    
    webfilter = [
                    PathSplitFilter(),
                    ParameterSplitFilter(),
                    ParameterValueFilter(),
                    ParameterPackFilter(),
                 ]
    
    try:
        calls = 0
        while True:
            try:
                if ws.can_accept():
                    with ws.accept() as req:
                        
                        calls += 1
                        data = html % str(calls)
                        
                        req.load_request(allowed=["GET","POST","PUT"])
                        logger.info( "request" , req.request )
                        logger.info( "request content len", len( req ) )
                        req.load_content()
                        
                        request = req.request
                        for f in webfilter:
                            f.filterRequest( request )
                        
                        logger.info( request.xpath, request.xquery )
                        logger.info( request.xparam )
                        logger.info( request.xkeyval )
                        logger.info( request.xpar )                      
                        
                        body = req.get_body()
                        if body!=None:
                            logger.info( "request content", body.decode() )
                            
                        statf = StaticFiles(["/www"])
                        if statf.handle( req ):
                            continue                        
                        
                        # dummy page
                        req.send_response( response=data )
                    
            except BadRequestException as ex:
                logger.excep( ex )
                
    except KeyboardInterrupt:
        logger.info("cntrl+c")        
    finally:
        ws.stop()


