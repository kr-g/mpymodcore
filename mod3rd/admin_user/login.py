
from modcore.log import logger

from modext.windup import WindUp, Router
from modext.windup_auth import security_store


router = Router( )

@router.get("/login")
def my_form( req, args ):

    session = args.session
    
    notify = ""
    user = ""
    
    try:
        user = session.user
        notify = session.notify
    except:
        pass
    finally:
        # keep session clean
        try:
            del session.notify
        except:
            pass
    
    data = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Login</title>
            </head>
            <style>
                div.loginbox {              
                    position: absolute;
                    top: 50%%;
                    left: 50%%;
                    margin-right: -50%%;
                    transform: translate(-50%%, -50%%)
                }
                div.loginnotify {
                    margin-top: 1em;
                    font-weight: bold;
                    text-align: center;                }
            </style>
            <body>

                <div class='loginbox'>
                    <form class='loginbody' action="/login" method="POST">
                        <label for="fname">Name:</label><br>
                        <input type="text" id="fname" name="username" value="%s">
                        <div>&nbsp;</div>
                        <label for="fpasswd">Password:</label><br>
                        <input type="password" id="fpasswd" name="passwd" value=""><br>
                        <div>&nbsp;</div>
                        <input type="submit" value="Login">
                    </form> 

                    <div class='loginnotify'> %s </div>
                </div>

            </body>
            </html>            
            """ % ( user, notify )
    
    logger.info(data)
    req.send_response( response=data )


# post request

@router.post("/login")
def my_form( req, args ):
    
    # get the form data
    username = args.form.username
    password = args.form.passwd

    session = args.session
    
    user = security_store.find_user(username)
    login_ok = security_store.check_password( user, password )
    
    session["user"] = username
    
    if login_ok:
        # set the user, use this rather then session.user
        session.update({ "auth_user" : user } )
        req.send_redirect( url="/" )
        return
   
    session["notify"] = "Login failed."
    
    logger.info("failed login",username)
    req.send_redirect( url="/login" )


# get and post 

@router("/logout")
def my_form( req, args ):

    logger.info( "logging out", args.session.user, args.session.auth_user )
    
    # set the session to destory 
    args.session = None
    
    req.send_redirect( url="/" )

