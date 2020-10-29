import machine


class IRQSuspendCxt(object):
    def __init__(self):
        self._state_irq = None

    def __enter__(self):
        self._state_irq = machine.disable_irq()
        return self

    def __exit__(self, ex_type, value, traceback):
        machine.enable_irq(self._state_irq)
        self._state_irq = None
        if ex_type != None:
            raise ex
