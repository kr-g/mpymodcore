
import ubinascii

from modcore.log import logger
from moddev.wlan import wlan_ap
from modext.webserv.windup import WindUp, Router

router = Router( root="/admin" )

# get request

@router.get("/wlan")
def my_form( req, args ):
    
    networks = wlan_ap.scan()
    
    netw = []
    netwdiv = ""
    
    for nam, mac, _, _, _, _ in networks:
        
        nam = nam.decode() 
        mac = ubinascii.hexlify(mac).decode()
        
        netwdiv += "<div>"
        netwdiv += '<input type="radio" id="f_'+mac+'" name="fwifi" value="'+mac+'" >'
        netwdiv += '<label for="f_'+mac+'">'+nam+'</label>'
        netwdiv += "</div>"
    
    data = """
            <!DOCTYPE html>
            <html>
            <body>

            <h2>WLAN config</h2>

            <form action="/admin/wlan" method="POST">
            
                <div> Available Networks nearby </div>
                <div> &nbsp; </div>
                <div> %s </div>

                <div> &nbsp; </div>
                <label for="f_passwd">Password:</label><br>
                <input type="text" id="f_passwd" name="fpasswd" value=""><br>

                <input type="submit" value="Connect">
            </form> 

            </body>
            </html>            
            """ % ( netwdiv )
    
    logger.info(data)
    req.send_response( response=data )


# post request

@router.post("/wlan")
def my_form( req, args ):
    
    body = req.request.xform
    
    data = """
            <h1>WLAN config data</h1>
            <div> query parameter = %s </div>
            <div> post data = %s </div>
            <div> post type = %s </div>
            """ % ( repr( args ), repr( body ), type( body ) )
    
    logger.info(data)
    req.send_response( response=data )





