"""

depracted old fiber version 1 process
code will break

# todo refact

"""


from modcore.log import logger

from modext.windup import WindUp, Router
from modext.windup.proc_fiber import ProcessorFiber


router = Router()


@router.get("/simple")
def my_simple_fiber(req, args):

    body = req.request.xform

    def fibered():
        data = """
                <h1>html page generated by fiber processing</h1>
                <div> query parameter = %s </div>
                """ % (
            repr(args),
        )
        logger.info(data)
        req.send_response(response=data)
        # yield ist required to make it a generator func
        yield

    req.send_fiber(fibered())


@router.get("/complex")
def my_complex_fiber(req, args):

    body = req.request.xform

    def fibered():

        # several yield statements inbetween...
        # always cause others to process

        req.send_head()

        yield

        data = """
                <h1>html page generated by fiber processing</h1>
                <h2>submitting single lines</h2>
                <div> query parameter = %s </div>
                """ % (
            repr(args),
        )
        logger.info(data)
        logger.info("splitting lines now")

        lines = data.splitlines()

        yield

        for line in lines:
            logger.info("line", line)
            # this is of course slow since data packages sent are small
            # http overhead for sending counts here
            req.send_data(line)
            yield

    req.send_fiber(fibered())


def serve():
    serv = WindUp()

    # replace standard executor with fiber executor
    serv.exec_class = ProcessorFiber

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
