
"""


deprecated samples






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
#from modcore.fiber import FiberLoop, Fiber

#from modext.webserv.webserv import WebServer, BadRequestException, COOKIE_HEADER, SET_COOKIE_HEADER
#from modext.webserv.filter import *
#from modext.webserv.content import StaticFiles
from modext.webserv import Router
#from modext.webserv.session import SessionStore


#
# log level is info -> lot of output
#


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

@router.get("/json")
def my_json_get( req, args ):

    data = {
        "args" : args
        }
    
    logger.info(data)
    req.send_json( obj=data, suppress_id=suppress_info )


@router.post("/json")
def my_json_post( req, args ):
    
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
                <h1>html page generated by fiber processing</h1>
                <div> query parameter = %s </div>
                """ % ( repr( args ), )
        logger.info(data)
        req.send_response( response=data, suppress_id=suppress_info )
        # yield ist required to make it a generator func
        yield
        
    req.send_fiber( fibered() )

@fiber_router.get("/complex")
def my_complex_fiber( req, args ):
    
    body = req.request.xform
    
    def fibered():
        
        # several yield statements inbetween...
        # always cause others to process
        
        req.send_head( suppress_id=suppress_info )
        
        yield
        
        data = """
                <h1>html page generated by fiber processing</h1>
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
        
    req.send_fiber( fibered() )
    
# accepts get and post 
@router("/redirect-me")
def my_app( req, args ):
    req.send_redirect( url="/", suppress_id=suppress_info )

