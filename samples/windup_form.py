
"""

form data
curl http://yourip/form -X POST -d 'field1=value1&field2=value2' -H "Content-Type: application/x-www-form-urlencoded"

"""

from modcore.log import logger

from modext.webserv.windup import WindUp, Router

router = Router( )

# get request

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
    req.send_response( response=data )


# post request

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
    req.send_response( response=data )


def serve():
    serv = WindUp()

    serv.start(generators=[
            router,
        ])

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()


