
from modcore.log import logger

from modext.windup import WindUp, Router


router = Router( )

# use xget or xpost decorator for extraction from url

@router.xget("/user/:user/id/:userid")
def my_form( req, args ):
    
    par = args.rest
    
    # traditional approach
    user = par.get("user")
    userid = par.get("userid")
    logger.info("user, id=", user, userid )
    
    # namespace access
    user = par.user
    userid = par.userid
    
    logger.info("user, id=", user, userid )
    
    data = """
            <h1>rest url data from the router </h1>
            <div> query parameter = %s </div>
            <div>  </div>
            <div>  </div>
            <div>  </div>
            <div> hello %s </div>
            <div> id %s  </div>
            """ % (
                repr( args.param ),
                user, userid,
                )
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



