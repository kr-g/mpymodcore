# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos as os

# import machine
# import time

# uos.dupterm(None, 1) # disable REPL on UART(0)

import micropython
import gc


def mem_info(verbose=True, auto_free=True):
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
    print("(free,alloc)", "before", before)
    print("(free,alloc)", "after", after)


from modcore import modc, logger, Module  # , LifeCycle

from moddev.control import control_serv, BREAK

from moddev import softap
from moddev import wlan
from moddev import webrepl
from moddev import ntp

from moddev.softap import soft_ap
from moddev.wlan import wlan_ap
from moddev.ntp import ntp_serv, set_log_time

from modext.windup import WindUp, Router
import modext.windup.session_mod

import modext.misc.main as mod_main


def auto_config():
    #
    # dynamic loading of all modules in mod3rd having
    # __app__.py in their module path present
    #
    from modext.auto_config.core import Loader

    cfg_load = Loader()

    all_ext = []
    all_3rd = cfg_load.find_3rd()
    all_ext.extend(all_3rd)
    all_app = cfg_load.find_apps()
    all_ext.extend(all_app)

    for ext in all_ext:
        logger.info("loading", ext)
        _app_ext = cfg_load.do_import(ext, globals())
        # print(_app_ext)

        try:
            gen_spec = _app_ext.app_ext
            if gen_spec == None:
                continue
            if type(gen_spec) != list:
                gen_spec = [gen_spec]
            for gen in gen_spec:
                # set the path_spec
                gen.path_spec = ext
                logger.info("config generators", gen.caption, gen.path_spec)
                global generators
                generators.extend(gen.generators)
        except Exception as ex:
            logger.excep(ex, "auto-discovery-configuration")

    return cfg_load


def set_timezone(tz_handler=None):
    from moddev.ntp import ntp_serv
    from moddev.ntp_tz import ntp_tz_serv

    ntp_tz_serv.set_tz_handler(tz_handler)


def set_cet_timezone():
    from moddev.ntp_tz_cet import TZ_cet

    set_timezone(TZ_cet)


def enable_sd_card():
    ## todo add slot parameter
    from moddev.sdcard import SDCard

    sdc = SDCard("sdc")
    modc.add(sdc)


def with_interrupts():
    micropython.alloc_emergency_exception_buf(128)


def start_auto_config(tz_handler_cls=None):
    "call common config function, enable cet tz handler as default"
    if tz_handler_cls != None:
        set_timezone(tz_handler_cls)
    else:
        set_cet_timezone()
    enable_sd_card()
    with_interrupts()
    cfg_loader = auto_config()
    return cfg_loader


def start_modcore(config):
    """add all modules to start automatically before this call"""

    modc.startup(config=config)

    print()
    print("softap ip ->", soft_ap.ifconfig())
    print("wlan ip ->", wlan_ap.ifconfig())
    print("current time ->", ntp_serv.localtime())
    print()


def start_windup():
    "start windup with defined set of generators"
    logger.info("config done. start windup.")
    serv.start(generators=generators)


def loop(config=None, debug=True):
    mod_main.debug_mode = debug
    serv.run_outbound_loop = True
    mod_main.loop(config, add_loop=serv.loop, ha_mode=False)


def loop_ha(config=None, debug=True):
    mod_main.debug_mode = debug
    serv.run_outbound_loop = False
    mod_main.loop(config, add_loop=[serv.loop, serv.run_outbound], ha_mode=True)


def run_loop(config=None, debug=True):
    import modext.misc.main_async as mod_main_async

    mod_main.debug_mode = debug

    # bring up windup as async task
    # serve outbound in a seperate async endless_loop
    serv.run_outbound_loop = False
    mod_main_async.run_loop(
        config, add_loop=[serv.loop, serv.run_outbound], ha_mode=True
    )


generators = []
serv = WindUp()


print()
gc_print_stat()


def print_main_info():
    print()
    print("to start :-)")
    print("call loop() - looping mode")
    print("call loop_ha() - high available mode where outbound is processed seperately")
    print("call run_loop() - run in async mode ")
    print()
    print("all loop methods can be called with optional config parameter")
    print()
