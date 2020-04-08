
# mpymodcore - a micro framework for MicroPython

an approach to modularize MicroPython projects.

introduce a defined lifecycle and eventing model
for modules / devices for convenient handling
of loose coupled modules/ device

# Related project

`mpymodcore` is the successor of [mpyconfigbase](https://github.com/kr-g/mpyconfigbase)

for configuration of automatic startup of WLAN, SoftAP, and WebRepl refer to the 
source/ sample code also there


# Platform

Tested ESP32 with PSRam and ESP8266 (for latter, see limitations below)

## Development status

Alpha state.
The API or logical call flow might change without prior notice.

In case your code breaks between two versions check
[`CHANGELOG`](https://github.com/kr-g/mpymodcore/blob/master/CHANGELOG.MD)
information first before creating a ticket / issue on github. thanks.


# Limitations

- no asyncio integration as of now
- with all mod's enabled as shown here in the sample
 it will not run on ESP8266 due to memory limit.
 but wlan, softap, and ntp should work 

# Installation

- with pip

    `# install to the current (project) folder`
    
    `python3 -m pip install mpymodcore --target .` 
    
 
- with [pygitgrab](https://github.com/kr-g/pygitgrab)
 download the `mpymodcore.pygg` file from the repo to your local project folder
 and download the sources then with:

    `python3 -m pygitgrab -f mpymodcore.pygg`
 

# Simple Web Server included

In package `modext.webserv` there are some functions for request handling.

In package `modext.webserv.serve` there is an example web server included.
Sample code in
[`serve.py`](https://github.com/kr-g/mpymodcore/blob/master/modext/webserv/serve.py)

Support for body data decoding e.g. form data, json


# Sample Code

some sample code can be found in [`boot.py`](https://github.com/kr-g/mpymodcore/blob/master/boot.py)



    # This file is executed on every boot (including wake-boot from deepsleep)
    #import esp
    #esp.osdebug(None)
    import uos as os
    import machine
    import time
    #uos.dupterm(None, 1) # disable REPL on UART(0)

    interrupts_enabled = False
    import micropython
    
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

    from modcore import modc, Module, LifeCycle
    from modcore import DEBUG, INFO, NOTSET, logger

    from moddev import wlan

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
                # ntp server can have timeout ...
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

    debug_mode = True

    def loop():    

        # turn debug level on for more detailed log info
        #modc.change_log_level( DEBUG if debug_mode else None )

        while True:
            try:
                modc.run_loop( cfg )
                time.sleep(0.25)
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


    print( "current time ->", ntp_serv.localtime() )
    print()
    print( "call loop() to start :-)" )
    print()


