
from regxcmd import *

# detail commands for register manipulation

# status

class DataPipeNo(RegRead):

    def reg_adr(self):
        return STATUS

    def trans(self,val):
        return ( val >> 1 ) & 0b111

class TxFull(RegRead):

    def reg_adr(self):
        return STATUS

    def trans(self,val):
        return ( val ) & 0b1 > 0

