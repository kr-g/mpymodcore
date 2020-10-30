from modcore.log import logger

from moddev.softap import soft_ap

from modext.windup import Router
from modext.windup import Namespace

from mod3rd.simplicity import *

router = Router(root="/admin")


@router.get("/softap")
def my_form(req, args):

    t = """
            <!DOCTYPE html>
            <html lang="en">
            <html>
            <head>
                <meta charset="utf-8">
                <title>SoftAP configuration</title>
            </head>
            <body>

                <h2>SoftAP configuration</h2>
                <form action="/admin/softap" method="POST">
                    <label for="f_softap">SoftAP SSID:</label><br>
                    <input type="text" id="f_softap" name="fssid" value="{softap}" ><br>
                    <label for="f_password">Password:</label><br>
                    <input type="text" id="f_password" name="fpassword" value="{password}" ><br>       
                    <input type="submit" value="Connect">
                </form>
                <div> Hint: a name like e.g. "modcore-$id$" will be expanded 
                        to: $id$ = your board unique id
                </div>
            
            </body>
            </html>
    """

    ## todo load data
    softap = "modcore-$id$"
    password = "12345678"

    smpl = Simplicity(t, esc_func=simple_esc_html)
    ctx = Namespace()
    ctx.update(
        {
            "softap": softap,
            "password": password,
        }
    )

    data = smpl.print(ctx)

    # logger.info(data)
    req.send_response(response=data, fibered=True)


@router.post("/softap")
def my_form(req, args):

    form = args.form

    logger.info(form.fssid, form.fpassword)

    ## todo save data
    ## todo reconfigure

    req.send_response()
