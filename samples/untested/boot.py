# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos as os
import machine
import time

# uos.dupterm(None, 1) # disable REPL on UART(0)


from ble_core import *
