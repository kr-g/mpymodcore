
import ussl

from modcore.log import logger

from modext.webserv.windup import WindUp


def _wrap_socket( sock ):
    #
    # the wrap_socket function depends on the micropython port
    # - see which arguments are supported
    #
    
    keyfile = "/server.key"
    certfile = "/server.crt"
    
    # untested
    return ussl.wrap_socket( sock )

def serve():
    serv = WindUp(wrap_socket=_wrap_socket)

    serv.start()

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()



