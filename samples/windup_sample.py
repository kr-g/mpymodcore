from modcore.log import logger

from modext.windup import WindUp, Router


def serve():
    serv = WindUp()

    serv.start()

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()
