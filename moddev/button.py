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


class Button(EventEmitter):
    def init(self):

        super().init()

        self.check_lifecycle = False  ##todo ?

        self.pin = None
        self.neg_logic = False
        self.debounce = Timeout(None)
        self.fire_on_up = True

        self.pressed = None
        self.last_state = False

    def conf(self, config=None):

        if config != None:

            # important. call config of EventEmitter
            super().conf(config)

            pin = config.get(self.id, None)  ##todo None?
            if pin != None:
                self.pin = Pin(pin, Pin.IN)
            self.info("pin", pin)

            self.neg_logic = config.get(self.id + ":neg_logic", self.neg_logic)
            self.info("neg_logic", self.neg_logic)

            debounce = config.get(self.id + ":debounce", 100)  # 100ms debounce
            debounce = int(debounce)

            self.debounce = Timeout(debounce, 1)  # 1ms timebase
            self.info("debounce ms", self.debounce)

            self.fire_on_up = config.get(
                self.id + ":fire_on_up", self.fire_on_up
            )  # waits for releasing

        if self.pin == None:
            self.warn("pin not configured")

    def start(self):
        self.pressed = None
        self.last_state = False

    def __emit__(self, config=None):

        if self.pin == None:
            return

        signaled = self.pin.value() ^ self.neg_logic
        if signaled == self.last_state and self.pressed == None:
            return

        self.last_state = signaled

        if self.pressed == None:
            self.info("deboucing")
            self.pressed = _ticks()
            self.debounce.restart()
            return

        if not self.debounce.elapsed():
            return False

        self.pressed = None

        if signaled and not self.fire_on_up:
            self.info("pressed")
            return self.__button__(config=config) or True

        if not signaled and self.fire_on_up:
            self.info("released")
            return self.__button__(config=config) or True

    # overload this
    def __button__(self, config=None):
        pass
