
"""

json needs doule-quotes !
curl http://yourip/json -X POST -d '{"hello":"world"}' -H "Content-Type: application/json"

"""

from modcore.log import logger

from modext.windup import WindUp, Router


router = Router( )


# get request

@router.get("/json")
def my_json_get( req, args ):

    data = {
        "args" : args.param
        }
    
    logger.info(data)
    req.send_json( obj=data )


# post request

@router.post("/json")
def my_json_post( req, args ):
    
    body = args.json
    
    data = """
            <h1>json from the router </h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args.param ), repr( body ), type( body ) )
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
