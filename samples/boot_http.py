# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos as os
import machine
import time

# uos.dupterm(None, 1) # disable REPL on UART(0)

from modcore import modc, logger

import moddev.wlan
import moddev.ntp
import moddev.webrepl
import moddev.softap

# configuration data

cfg = {
    "TZ": 60 * 60 * 2,
}

# add all modules to start automatically before this call
modc.startup(config=cfg)

import gc

gc.collect()

#
# only with 'modext.http' package
#

from modext.http.webserv import WebServer

ws = WebServer()
ws.start()
logger.info("listening on", ws.addr)

print("(alloc/free)", (gc.mem_alloc(), gc.mem_free()))

print()
print("call loop() to start :-)")
print()


debug_mode = True


def loop():

    # turn debug level on for more detailed log info
    # modc.change_log_level( DEBUG if debug_mode else None )

    while True:
        try:
            # modules
            modc.run_loop(cfg)

            try:
                if ws.can_accept():
                    with ws.accept() as req:
                        req.send_response(response="hello there :-)")
            except:
                pass
            # your code

        except KeyboardInterrupt:
            logger.info("\ncntrl+c, auto shutdown=", not debug_mode)
            if not debug_mode:
                modc.shutdown()
            if not debug_mode:
                logger.info("call first")
                logger.info("modc.startup(config=cfg)")
            logger.info("call loop() to continue")
            break
        except Exception as ex:
            logger.excep(ex)
