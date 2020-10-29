from . import *

# detail commands for register manipulation

# rf setup register


class RFDataRate(RegRead):
    def reg_adr(self):
        return RF_SETUP

    def trans(self, val):
        rc = 0
        if val & RF_DR_LOW:
            rc |= 1 << 1
        if val & RF_DR_HIGH:
            rc |= 1 << 0
        return rc


class RFDataRateSetup(RegUpdate):
    def __init__(self, data=0b01):

        data &= 0b11
        if data == 0b11:
            raise Exception("reserved")

        super().__init__(self, data=data)

    def reg_adr(self):
        return RF_SETUP

    def trans(self, val):

        val &= 0b1101_0111

        if (self.data() & 1 << 1) > 0:
            val |= RF_DR_LOW
        if (self.data() & 1 << 0) > 0:
            val |= RF_DR_HIGH

        return val


class TxPower(RegRead):
    def reg_adr(self):
        return RF_SETUP

    def trans(self, val):
        return (val >> 1) & 0b11


class TxPowerSetup(RegUpdate):
    def __init__(self, data=0b11):
        data &= 0b11
        super().__init__(self, data=data)

    def reg_adr(self):
        return RF_SETUP

    def trans(self, val):

        val &= 0b1111_1001
        val |= self.data() << 1

        return val
