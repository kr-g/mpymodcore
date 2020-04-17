
import ubinascii

from modcore.log import logger
from modcore import modc
from moddev.wlan import wlan_ap, WLAN_RESTART
from modext.windup import Router

router = Router( root="/admin" )

# get request

netw = {}

@router.get("/wlan")
def my_form( req, args ):
    
    networks = wlan_ap.scan()
    
    netwdiv = ""
    
    for nam, mac, _, _, _, _ in networks:
        
        nam = nam.decode() 
        mac = ubinascii.hexlify(mac).decode()
        
        global netw
        netw[mac]=nam
        
        netwdiv += "<div>"
        netwdiv += '<input type="radio" id="f_'+mac+'" name="fwifi" value="'+mac+'" >'
        netwdiv += '<label for="f_'+mac+'">'+nam+'</label>'
        netwdiv += "</div>"
    
    data = """
            <!DOCTYPE html>
            <html>
            <body>

            <h2>WLAN configuration</h2>

            <div> &nbsp; </div>
            <div> Currently connected to: '%s' </div>
            <div> &nbsp; </div>

            <form action="/admin/wlan" method="POST">
            
                <div> Available Networks nearby </div>
                <div> &nbsp; </div>
                <div> %s </div>

                <div> &nbsp; </div>
                <label for="f_passwd">Password:</label><br>
                <input type="text" id="f_passwd" name="fpasswd" value=""><br>

                <input type="submit" value="Connect">
                <div> Make sure to connect via SoftAP for setting up WLAN
                        otherwise Connection might get lost.
                </div>
            </form> 

            </body>
            </html>            
            """ % ( str(wlan_ap.ssid), netwdiv )
    
    logger.info(data)
    req.send_response( response=data )


# post request

@router.post("/wlan")
def my_form( req, args ):
    
    form = req.request.xform
    
    ssid = netw[ form[ "fwifi" ]]
    passwd = form[ "fpasswd" ]
    
    data = """
            <h1>WLAN configuration saved</h1>
            <div> &nbsp; </div>
            <div> Networkname: '%s' </div>
            """ % ( ssid )
    
    wlan_ap.wlan_config( ssid, passwd )
    
    # restart in next loop, otherwise connection breaks and response fails
    modc.fire_event(WLAN_RESTART)
    
    logger.info(data)
    req.send_response( response=data )





