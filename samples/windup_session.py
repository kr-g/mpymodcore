
from modcore.log import logger

from modext.windup import WindUp, Router

from modext.windup_auth import security_store

router = Router( )

#
# example for session usage
# login and logout sample
#
# note:
#  this is _not_ a recommandation for handling user login/logout
#

@router.get("/login")
def my_form( req, args ):

    session = args.session
    
    logger.info( session )

    # a not recommended scnario ... 
    # get the last login name, or default 
    login = session.get("user", "")

    data = """
            <!DOCTYPE html>
            <html>
            <body>

            <h2>Login</h2>

            <form action="/login" method="POST">
              <label for="fname">Name:</label><br>
              <input type="text" id="fname" name="fname" value="%s"><br>
              <input type="submit" value="Login">
            </form> 

            <p>To send Login data click the "Submit" button</p>

            </body>
            </html>            
            """ % ( login )
    
    logger.info(data)
    req.send_response( response=data )


# post request

@router.post("/login")
def my_form( req, args ):
    
    # get the form data
    user = args.form.fname

    session = args.session
    
    # get the login from the session
    login = session.get("user")

    # just set the name in the session
    # thats all
    session["user"] = user
    
    # just load the user if available
    session.update({ "auth_user" : security_store.find_user(user) } )
    

    data = """
            <h2> Login result </h2>
            <div> last login %s </div>
            <div> name %s </div>
            <div> <a href="/login">back to login page</a> </div>
            <div> <a href="/logout">click to logout</a> </div>
            """ % ( login, user )
    
    logger.info(data)
    req.send_response( response=data )


# get and post 

@router("/logout")
def my_form( req, args ):

    session = args.session
    
    # get the login from the session
    login_get = session.get("user")

    # or using namespace access
    login = session.user
    
    logger.info( "logging out", login, login_get )
    
    # set the xsession to None will destory the session
    args.session = None
    
    req.send_redirect( url="/login" )


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

