"""

this uses the fake login router without any password check !!!

"""

from modcore.log import logger

from modext.windup import WindUp, Router

from modext.windup_auth import security_store

# fake login just with user name, no password check
from samples.windup_session import router as login_router


@login_router.get("/custom")
def custom_page(req, args):
    req.send_response(response="go back to <a href='/login'>login</a>")


from modext.windup_auth import AuthRouter

# this return redirect to a custom page
# omit this to get plain 401
secured_router = AuthRouter(status=302, location="/custom")


@secured_router.get("/top-secret", groups=["admin"])
def tops(req, args):
    req.send_response(response="ok, admin. you have permission")


@secured_router.get("/user-site", groups=["normaluser"])
def tops(req, args):
    req.send_response(response="ok, buddy. you have permission")


"""

test with: (replace your-ip with ip, or add to /etc/hosts)

curl http://your-ip/login -X POST -d 'fname=John' -H "Content-Type: application/x-www-form-urlencoded" --cookie cookies.txt --cookie-jar cookies.txt

curl http://your-ip/userid/MyUserId --cookie cookies.txt 

curl http://your-ip/userdata/MyUserId -X POST -d '{"hello":"world"}' -H "Content-Type: application/json" --cookie cookies.txt 


"""


@secured_router.xget("/userid/:user", groups=["restricted"])
def tops(req, args):
    uid = args.rest.user
    req.send_response(response="ok, received '" + uid + "'")


@secured_router.xpost("/userdata/:user", groups=["restricted"])
def tops(req, args):
    uid = args.rest.user
    json = args.json
    req.send_response(response="ok, received '" + repr(json) + "' for " + uid)


def serve():
    serv = WindUp()

    serv.start(
        generators=[
            login_router,
            secured_router,
        ]
    )

    try:
        while True:
            serv.loop()
    except KeyboardInterrupt:
        logger.info("cntrl+c")
    finally:
        serv.stop()


# from samples.windup_security import serve
