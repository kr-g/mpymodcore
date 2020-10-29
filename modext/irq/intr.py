import machine
from machine import Pin, Timer

from modcore.log import LogSupport


class Interrupt(LogSupport):

    all_intr_pins = {}

    def __init__(self, pin):
        LogSupport.__init__(self)
        self.pin = pin
        self.intr = Pin(self.pin, Pin.IN)

    def __del__(self):
        self.disable()

    @staticmethod
    def _handler_irq(pin):
        oid = str(pin)
        if oid in Interrupt.all_intr_pins:
            Interrupt.all_intr_pins[oid].callb()

    def callb(self):
        pass

    def enable(self, mode=Pin.IRQ_RISING | Pin.IRQ_FALLING):
        Interrupt.all_intr_pins[str(self.intr)] = self
        self.intr.irq(trigger=mode, handler=Interrupt._handler_irq)
        return self

    def disable(self):
        self.intr.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=None)
        del Interrupt.all_intr_pins[str(self.intr)]
        return self

    def disable_all():
        for i in Interrupt.all_intr_pins:
            Interrupt.all_intr_pins[i].disable()


#


class Counter(Interrupt):
    def __init__(self, pin):
        super().__init__(pin)
        self.reset()

    def callb(self):
        self.debug("íntr")
        if self.do_reset == True:
            self.reset()
        self.count += 1

    def reset(self):
        self.count = 0
        self.do_reset = False

    def __repr__(self):
        return {"count": self.count}


class Button(Interrupt):
    def enable(self, mode=Pin.IRQ_RISING):
        super().enable(mode)
        self.trigger()

    def callb(self):
        self.trigger(True)

    def trigger(self, state=None):
        self._trigger = state

    def popstate(self):
        last = self._trigger
        self.trigger()
        if last:
            self.info("state", last)
        return last
