# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos as os
import machine
import time
#uos.dupterm(None, 1) # disable REPL on UART(0)

from modcore import modc, logger

import moddev . wlan
import moddev . ntp
import moddev . webrepl
import moddev . softap

# package 'modext.fiber' is not required only 'http' and 'windup'

from modext.windup import WindUp, Router
serv = WindUp()

myapp=Router()

@myapp("/app")
def get( req, args ):
    req.send_response( response="hello world" )


serv.start( generators = [  myapp, ] )

# configuration data

cfg = {
        "TZ" : 60*60*2,
}

# add all modules to start automatically before this call
modc.startup(config=cfg)

import gc
gc.collect()

print("(alloc/free)", (gc.mem_alloc(), gc.mem_free()))

debug_mode = True

def loop():    

    # turn debug level on for more detailed log info
    #modc.change_log_level( DEBUG if debug_mode else None )

    while True:
        try:
            # modules
            modc.run_loop( cfg )
            # web server
            serv.loop()

            # your code
            
        except KeyboardInterrupt:
            logger.info( "\ncntrl+c, auto shutdown=", not debug_mode)
            if not debug_mode:
                modc.shutdown()                
            if not debug_mode:
                logger.info("call first")
                logger.info("modc.startup(config=cfg)")
            logger.info( "call loop() to continue" )
            break
        except Exception as ex:
            logger.excep( ex )


