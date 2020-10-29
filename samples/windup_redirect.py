from modcore.log import logger

from modext.windup import WindUp, Router


router = Router()

# accepts get and post
@router("/redirect-me")
def my_app(req, args):
    req.send_redirect(url="/test.html")


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
