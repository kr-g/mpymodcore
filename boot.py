# This file is executed on every boot (including wake-boot from deepsleep)


from modext.misc.boot import *


# some sample test classes ...


class Consumer(Module):
    def watching_events(self):
        return ["ntp", "wlan"]


class ConsumerNetw(Module):
    def watching_events(self):
        return ["WLAN", "softap"]  # case does not matter


class ConsumerNTP(Module):
    def watching_events(self):
        return ["ntp"]

    def __loop__(self, config=None, event=None, data=None):
        if event != None:
            self.info("recv:", event, "data:", data)
            # data can contain True or False
            # setting ntp from server can have timeout ...
            # micropython ntp module throws then exceptions
            # this can take quite a while until it reconnects
            val = self.event_data_value(data)
            if val:
                self.info("recalc schedule...")
            else:
                self.warn("lost ntp connection")


# basic configuration

cfg = {
    "TZ": 60 * 60 * 2,  # ntp, better use ntp_tz_serv, TZ_cet classes
    "SD_SLOT": 3,  # default for esp32 with psram / TTGO
    "SD_PATH": "/sd",
    # this is a variable what can be referenced!
    # led pin for ttgo board
    "led": 21,
}


c1 = Consumer("c1")
modc.add(c1)

c2 = ConsumerNetw("c2")
modc.add(c2)

c3 = ConsumerNTP("c3")
modc.add(c3)


from moddev.interval import Interval


class MyInterval(Interval):
    def __timeout__(self, config=None):
        self.info("timeout")


cfg.update(
    {
        "int1": 5,  # timeout in sec, default timebase 1000
        "int1:event": ["pin:led:toggle"],  # access led parameter from cfg
    }
)

int1 = MyInterval("int1")
modc.add(int1)

cfg.update(
    {
        "int2": 130,
        "int2:timebase": 100,  # 1/100 sec timebase
    }
)

int2 = MyInterval("int2")
modc.add(int2)

cfg.update(
    {
        "int3": 1,
        "int3:timebase": 1000 * 60,  # 1 min timebase
    }
)

int3 = MyInterval("int3")
modc.add(int3)

cfg.update(
    {
        "int_ntp": 5,
        "int_ntp:timebase": 1000 * 60,  # 1 min timebase
        "int_ntp:event": "ntp-sync",  # event to fire
    }
)

int_ntp = Interval("int_ntp")
modc.add(int_ntp)

cfg.update(
    {
        "session_purge": 30,
        "session_purge:timebase": 1000 * 60,  # 1 min timebase
        "session_purge:event": "session-man",  # event to fire
    }
)

session_purge = Interval("session_purge")

from modcore.lifecycle import LifeCycle


@session_purge.hook(LifeCycle.CONFIG, before=True)
def before_config(self):
    self.info("before config hook called")


@session_purge.hook(LifeCycle.CONFIG, after=True)
def after_config(self):
    self.info("after config hook called")


@session_purge.hook(LifeCycle.LOOP, before=True)
def before_loop(self):
    self.info("before loop hook called")


@session_purge.hook(LifeCycle.LOOP, after=True)
def after_loop(self):
    self.info("after loop hook called")


modc.add(session_purge)

from moddev.alarmclock import AlarmClock

cfg.update(
    {
        "alarm1": "11:11",
        "alarm1:utc": False,  # default, can be obmitted
        "alarm1:event": "gc",
    }
)

alarm1 = AlarmClock("alarm1")
modc.add(alarm1)

cfg.update(
    {
        "alarm2": "11:13",
        "alarm2:event": "status:mem_0",  # event, and data to send
    }
)
alarm2 = AlarmClock("alarm2")
modc.add(alarm2)

from moddev.button import Button


cfg.update(
    {
        "boot_btn": 0,  # pin no -> gpio 0
        "boot_btn:debounce": 100,  # 100ms - default, can be obmitted
        "boot_btn:neg_logic": True,  # boot button gpio0 becomes signaled with value 0 by pressing
        "boot_btn:fire_on_up": True,  # default, fires when releasing
        # "boot_btn:event" : "status:mem_1", # event to fire
        # "boot_btn:event" : "pin:21:toggle", # toggle led on pin 21
        "boot_btn:event": [
            "pin:21:toggle",
            "break",
        ],  # raise 2 events
    }
)

boot_btn = Button("boot_btn")
modc.add(boot_btn)

from moddev.alarmcounter import AlarmCounter

cfg.update(
    {
        "alarm_counter": None,  # not configured
        "alarm_counter:delta_period": 5,
        "alarm_counter:under": 1,
        "alarm_counter:above": 10,  # alarm_count counts state changes 0->1, and 1->0
    }
)

alarm_counter = AlarmCounter("alarm_counter")
modc.add(alarm_counter)


status = Router()


@status.get("/break")
def get_break(req, args):
    modc.fire_event(BREAK)
    req.send_response()


@status.get("/status")
def get_status(req, args):

    obj = {
        "mem_alloc": gc.mem_alloc(),
        "mem_free": gc.mem_free(),
    }

    req.send_json(obj)


@status.get("/gc")
def get_gc(req, args):

    before = gc.mem_free(), gc.mem_alloc()
    gc.collect()
    after = gc.mem_free(), gc.mem_alloc()

    obj = {
        "order": "(free,alloc)",
        "before": before,
        "after": after,
        "free_delta": after[0] - before[0],
    }

    req.send_json(obj)


@status.xget("/pin/:pin/:mode")
def get_pin(req, args):

    # namespaced objects
    logger.info("sid cookie", args.cookies.sessionid)

    logger.info("session_id", args.session.xsession_id)
    logger.info("rest parameter", args.rest)

    # keep the variable to avoid dict lookups -> performance
    rest = args.rest
    logger.info("pin", rest.pin)
    # avoid this -> dict lookup
    logger.info("mode", args.rest.mode)

    req.send_response(response="ok")


from modext.windup_auth import AuthRouter

secured_router = AuthRouter()


@secured_router("/top-secret", groups=["admin"])
def tops(req, args):
    req.send_response(response="ok, admin. you have permission")


@secured_router("/user-site", groups=["normaluser", "restricted"])
def tops(req, args):
    req.send_response(response="ok, buddy. you have permission")


# configure
cfg_loader = start_auto_config()

# add all modules before this call
start_modcore(config=cfg)

logger.info("modcore config done. start windup.")

# this is located in modext.misc.boot
# add additional routers
generators.extend(
    [
        status,
        secured_router,
    ]
)

start_windup()

# give some hints
print_main_info()

print("use cfg config settings, for proper startup")
print("e.g. run_loop(cfg)")
print()
