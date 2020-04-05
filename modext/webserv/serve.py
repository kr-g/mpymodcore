
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
from .webserv import WebServer


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
    
    try:
        calls = 0
        while True:
            if ws.can_accept():
                with ws.accept() as req:
                    
                    calls += 1
                    data = html % str(calls)
                    logger.info( "request" , req.request )
                    logger.info( "request content len", len( req ) )
                    req.load_content()
                    body = req.get_body()
                    if body!=None:
                        logger.info( "request content", body.decode() )
                        
                    req.send_response( response=data )
                    
    except KeyboardInterrupt:
        logger.info("cntrl+c")        
    finally:
        ws.stop()


