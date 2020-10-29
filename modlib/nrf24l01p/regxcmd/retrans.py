from . import *

# detail commands for register manipulation

# automatic retransmission


class AutoRetransDelay(RegRead):
    def reg_adr(self):
        return SETUP_RETR

    def trans(self, val):
        return val >> 4


class AutoRetransDelaySetup(RegUpdate):
    def __init__(self, data=0):
        super().__init__(self, data=data)

    def reg_adr(self):
        return SETUP_RETR

    def trans(self, val):
        return (val & 0x0F) | (self.data() << 4)


class AutoRetransCount(RegRead):
    def reg_adr(self):
        return SETUP_RETR

    def trans(self, val):
        return val & 0b1111


class AutoRetransCountSetup(RegUpdate):
    def __init__(self, data=0b0011):
        super().__init__(self, data=data)

    def reg_adr(self):
        return SETUP_RETR

    def trans(self, val):
        return (val & 0xF0) | (self.data() & 0b1111)
