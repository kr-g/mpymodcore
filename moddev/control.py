"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import micropython
import machine
import gc
import sys


from modcore import modc, Module, LifeCycle


STOP = "stop"  ##todo
CONT = "cont"  ##todo

HALT = "halt"  ##todo

RESTART = "restart"
SERV_HARD = "hard"
SERV_MODCORE = "modcore"

STATUS = "status"
SERV_MEM0 = "mem_0"
SERV_MEM1 = "mem_1"
SERV_MEM_FREE = "memfree"

LOGLEVEL = "loglevel"  ##todo

GC = "gc"
PIN = "pin"
EXIT = "exit"
BREAK = "break"


class ControlServer(Module):
    def watching_events(self):
        return [
            RESTART,
            GC,
            STATUS,
            PIN,
            EXIT,
            BREAK,
        ]

    def start(self):
        self.breaksignal = False

    def loop(self, config=None, event=None):

        self.breaksignal = False  # throw away last capture

        if event == None:
            return

        val = self.event_value(event)
        if val != None:
            val = val.lower()
        self.info("received service call", event.name, val)

        if self.is_event(event, EXIT):
            sys.exit(0)

        if self.is_event(event, BREAK):
            self.breaksignal = True

        if self.is_event(event, RESTART):

            if val == SERV_HARD:
                machine.reset()

            if val == SERV_MODCORE:
                modc.reconfigure()

        if self.is_event(event, STATUS):
            self.info("---------------------", val, "----")
            if val == SERV_MEM0:
                micropython.mem_info()
            if val == SERV_MEM1:
                micropython.mem_info(1)
            if val == SERV_MEM_FREE:
                self.info(SERV_MEM_FREE, gc.mem_free())
            self.info("---------------------", val, "done")

        if self.is_event(event, GC):
            before = gc.mem_free(), gc.mem_alloc()
            gc.collect()
            after = gc.mem_free(), gc.mem_alloc()
            self.info(GC, "(free,alloc)", "before", before)
            self.info(GC, "(free,alloc)", "after", after)

        if self.is_event(event, PIN):
            try:
                pinno, mode = val.split(":")
                try:
                    pinno = int(pinno)
                except:
                    # not an integer
                    # load pin no from config
                    pinno = int(config[pinno])
                pin = machine.Pin(pinno, machine.Pin.OUT)
                mode = mode.lower()
                if mode not in [
                    "on",
                    "off",
                    "toggle",
                ]:
                    raise Exception("mode not supported", mode)
                if mode == "on":
                    pin.on()
                if mode == "off":
                    pin.off()
                if mode == "toggle":
                    pin.value(not pin.value())
            except Exception as ex:
                self.warn(ex, "failed", val)


control_serv = ControlServer("watchdog")
modc.add(control_serv)
