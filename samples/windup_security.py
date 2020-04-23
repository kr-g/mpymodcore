
from modcore.log import logger

from modext.windup import WindUp, Router

from modext.windup_auth import security_store

# fake login just with user name, no password check
from samples.windup_session import router as login_router


@login_router.get("/custom")
def custom_page(req,args):
    req.send_response( response="go back to <a href='/login'>login</a>" )


from modext.windup_auth import AuthRouter

# this return redirect to a custom page
# omit this to get plain 401
secured_router = AuthRouter(status=302,location="/custom")

@secured_router.get("/top-secret",groups=["admin"])
def tops(req,args):
    req.send_response( response="ok, admin. you have permission" )

@secured_router.get("/user-site",groups=["normaluser"])
def tops(req,args):
    req.send_response( response="ok, buddy. you have permission" )


def serve():
    serv = WindUp()

    serv.start(generators=[
            login_router,
            secured_router,
        ])

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()



