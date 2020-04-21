
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos as os
import machine
import time
#uos.dupterm(None, 1) # disable REPL on UART(0)

import micropython

interrupts_enabled = False

if interrupts_enabled:
    micropython.alloc_emergency_exception_buf(128)

import gc
gc.collect() 

def mem_info(verbose=True,auto_free=True):
    if auto_free:
       gc.collect()
    if verbose:
        micropython.mem_info(1)
    else:
        micropython.mem_info()
    return gc.mem_free()

def hardreset():
    machine.reset()
    
def gc_print_stat():
    before = gc.mem_free(), gc.mem_alloc()
    gc.collect() 
    after = gc.mem_free(), gc.mem_alloc()
    print( "(free,alloc)", "before", before )
    print( "(free,alloc)", "after", after )


from modcore import modc, Module, LifeCycle
from modcore import DEBUG, INFO, NOTSET, logger

import moddev.control

from moddev import wlan
from moddev.wlan import wlan_ap

from moddev import ntp
from moddev.ntp import ntp_serv, set_log_time

# ntp can change timezone dynamically
# press cntrl+c during loop and fire an event, then call loop() again
# modc.fire_event("tz", 3600*2 ) # 2 hours offset
# modc.fire_event("tz" ) # utc

from moddev import softap

from moddev import webrepl
from moddev.webrepl import webrepl_serv

# some sample test classes ...

class Consumer(Module):
        
    def watching_events(self):
        return ["ntp","wlan"]

class ConsumerNetw(Module):
        
    def watching_events(self):
        return ["WLAN","softap"] # case does not matter

class ConsumerNTP(Module):
        
    def watching_events(self):
        return ["ntp"]
    
    def __loop__(self,config=None,event=None,data=None):
        if event!=None:
            self.info( "recv:", event, "data:", data )
            # data can contain True or False
            # setting ntp from server can have timeout ...
            # micropython ntp module throws then exceptions
            # this can take quite a while until it reconnects
            val = self.event_data_value(data)
            if val:
                self.info("recalc schedule...")
            else:
                self.warn("lost ntp connection")
            
    

c1 = Consumer("c1")
modc.add( c1 )

c2 = ConsumerNetw("c2")
modc.add( c2 )

c3 = ConsumerNTP("c3")
modc.add( c3 )


from moddev.interval import Interval

class MyInterval(Interval):
    
    def __timeout__(self,config=None):
        self.info("timeout")
    

int1 = MyInterval( "int1" )
modc.add( int1 )
int2 = MyInterval( "int2" )
modc.add( int2 )
int3 = MyInterval( "int3" )
modc.add( int3 )

int_ntp = Interval( "int_ntp" )
modc.add( int_ntp )

from moddev.alarmclock import AlarmClock

alarm1 = AlarmClock("alarm1")
modc.add( alarm1 )

alarm2 = AlarmClock("alarm2")
modc.add( alarm2 )

from moddev.button import Button

boot_btn = Button("boot_btn")
modc.add( boot_btn )

# configuration data

cfg = {
        "TZ" : 60*60*2,
        
        "SD_SLOT" : 3, # default for esp32 with psram / TTGO
        "SD_PATH" : "/sd",
        
        "int1" : 5, # timeout in sec, default timebase 1000
        
        "int2" : 130,
        "int2:timebase" : 100, # 1/100 sec timebase
        
        "int3" : 1,
        "int3:timebase" : 1000*60, # 1 min timebase
        
        "int_ntp" : 5,
        "int_ntp:timebase" : 1000*60, # 1 min timebase
        "int_ntp:event" : "ntp-sync", # event to fire
        
        "alarm1" : "11:11",
        "alarm1:utc" : False, # default, can be obmitted
        "alarm1:event" : "gc",
        
        "alarm2" : "11:13",
        "alarm2:event" : "status:mem_0", # event, and data to send

        "boot_btn" : 0, # pin no -> gpio 0
        "boot_btn:debounce" : 100, # 100ms - default, can be obmitted
        "boot_btn:neg_logic" : True, # boot button gpio0 becomes signaled with value 0 by pressing
        "boot_btn:fire_on_up" : True, # default, fires when releasing
        "boot_btn:event" : "status:mem_1", # event to fire

    }


fancy_stuff_i_have_a_sd_card = True

if fancy_stuff_i_have_a_sd_card:
    from moddev.sdcard import SDCard
    sdc = SDCard("sdc")
    modc.add( sdc )
    
    # try
    #
    # for securely removal
    # sdc.change_level(LifeCycle.UMOUNT), or
    # sdc.change_level(LifeCycle.EJECT)
    #
    # use again (no auto detection!)
    # sdc.change_level(LifeCycle.MOUNT)
    

modc.startup(config=cfg)

# just serving some static files
from modext.windup import WindUp
serv = WindUp()

# replace standard executor with fiber executor
#serv.exec_class = ProcessorFiber

import mod3rd
from mod3rd.admin_esp.wlan import router as router_wlan

logger.info("config done. start windup.")

run_not_in_sample_mode = True

if run_not_in_sample_mode:
    serv.start( generators = [
            router_wlan,
        ])

debug_mode = True

def loop(run_until=None):    

    # turn debug level on for more detailed log info
    #modc.change_log_level( DEBUG if debug_mode else None )

    while run_until==None:
        if run_until!=None:
            run_until -= 1
            if run_until<0:
                run_until=None
        try:
            # modules
            modc.run_loop( cfg )
            # web server
            serv.loop()
            
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


print()
gc_print_stat()

print( "ip ->", wlan_ap.ifconfig() )
print( "current time ->", ntp_serv.localtime() )
print()
print( "call loop() to start :-)" )
print()


#from samples.windup_fiber import serve

#end 