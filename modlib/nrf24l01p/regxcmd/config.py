from . import *

# detail commands for register manipulation

# config


class CRC(RegRead):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & EN_CRC > 0


class CRCon(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val | EN_CRC


class CRCoff(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & ~EN_CRC


class CRCScheme(RegRead):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return ((val >> 2) & 0b1) + 1


class CRC1bytes(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & ~CRCO


class CRC2bytes(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val | CRCO


class Powered(RegRead):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & PWR_UP > 0


class PowerOff(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & ~PWR_UP


class PowerOn(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val | PWR_UP


class IsMaster(RegRead):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & PRIM_RX > 0


class MasterPRX(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val | PRIM_RX


class SlavePTX(RegUpdate):
    def reg_adr(self):
        return CONFIG

    def trans(self, val):
        return val & ~PRIM_RX
