from modcore.log import logger

from modext.windup import WindUp, Router


router = Router()

# accepts get and post
@router("/app")
def my_app(req, args):
    data = """
            <h1>from the router</h1>
            <div> query parameter = %s </div>
            """ % repr(
        args.param
    )
    logger.info(data)
    req.send_response(response=data)


def serve():
    serv = WindUp()

    serv.start(
        generators=[
            router,
        ]
    )

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()
