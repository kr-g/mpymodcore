"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time

from machine import Pin

from modcore import modc, Module, LifeCycle

from .eventemitter import EventEmitter
from .timeout import Timeout


def _ticks():
    return time.ticks_ms()


def _diff(t1, t2):
    return time.diff_ticks(t1, t2)


TIME_BASE = 1000


class AlarmCounter(EventEmitter):
    def init(self):

        super().init()

        # self.check_lifecycle = False ##todo ?

        self.pin = None
        self.delta_period = None
        self.under_count = None
        self.above_count = None

        self.count = 0
        self.last_state = False

    def conf(self, config=None):

        if config != None:

            # important. call config of EventEmitter
            super().conf(config)

            pin = config.get(self.id, None)  ##todo None?
            if pin != None:
                self.pin = Pin(pin, Pin.IN)
            self.info("pin", pin)

            delta_period = config.get(self.id + ":delta_period", 1)
            timebase = config.get(self.id + ":timebase", TIME_BASE)

            self.delta_period = Timeout(delta_period, timebase)
            self.info("delta_period", self.delta_period)

            self.under_count = config.get(self.id + ":under", None)
            self.above_count = config.get(self.id + ":above", None)
            self.info("range", self.under_count, "..", self.above_count)

        if self.pin == None:
            self.warn("pin not configured")

    def start(self):
        self.count = 0
        self.last_state = False
        self.delta_period.restart()

    def __emit__(self, config=None):

        if self.pin == None:
            return

        signaled = self.pin.value()

        if signaled != self.last_state:
            # counts state changes: both 0->1, and 1->0
            self.count += 1
            self.last_state = signaled

        if not self.delta_period.elapsed():
            return False

        self.delta_period.restart()

        try:
            if self.under_count != None and self.count <= self.under_count:
                self.info("lower bound alarm", self.count)
                return self.__alarm__(config) or True
            if self.above_count != None and self.count >= self.above_count:
                self.info("upper bound alarm", self.count)
                return self.__alarm__(config) or True
        finally:
            self.count = 0

    # overload this
    def __alarm__(self, config=None):
        pass
