from modcore.log import logger

from modext.windup import WindUp, Router


def _html404(req):
    logger.info("custom 404 called")
    data = """
    <html>
        <head>
            <title>not found</title>
        </head>
        <body>
            <h1>url not found</h1>
            so sorry ...
        </body>
    </html>
    """

    req.send_response(status=404, response=data)


def serve():
    serv = WindUp()
    serv.html404 = _html404

    serv.start()

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()
