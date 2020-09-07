
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""


from .const import *
from .cmd import RegRead, RegWrite

# bulk commands for register manipulation

class Config(RegRead):
    
    def __init__(self):
        super().__init__( adr=CONFIG )
 
class ConfigSetup(RegWrite):

    def __init__(self,mode=EN_CRC):
        super().__init__( adr=CONFIG, data= mode )

#

class ESB(RegRead):

    def reg_adr(self):
        return EN_AA

    def trans(self,val):
        return val & (64-1)
    
class ESBEnable(RegWrite):

    def __init__(self,pipe=0b0011_1111):
        super().__init__( adr=EN_AA, data= pipe & (64-1) )

#

class RxAdr(RegRead):

    def reg_adr(self):
        return EN_RXADDR

    def trans(self,val):
        return val & (64-1)
    
class RxAdrEnable(RegWrite):

    def __init__(self,pipe=0b0000_0011):
        super().__init__( adr=EN_RXADDR, data= pipe & (64-1) )

#    
    
class AdrWidth(RegRead):

    def reg_adr(self):
        return SETUP_AW

    def trans(self,val):
        return (val & 0b11) + 2
    
class AdrWidthSetup(RegWrite):

    def __init__(self,width=5):
        width -= 2
        if width<=0 or width>0b11:
            raise Exception("illegal mode")
        super().__init__( adr=SETUP_AW, data= width )

#

class AutoRetrans(RegRead):

    def reg_adr(self):
        return SETUP_RETR

class AutoRetransSetup(RegWrite):

    def __init__(self,mode=0b0000_0011):
        super().__init__( adr=SETUP_RETR, data= mode )

#

class RF(RegRead):

    def reg_adr(self):
        return RF_CH

    def trans(self,val):
        return val & 0b0111_1111
    
class RFSetup(RegWrite):

    def __init__(self,channel=0b10):
        channel &= 0b0111_1111
        super().__init__( adr=RF_CH, data= channel )
   
#

class RFRegister(RegRead):

    def reg_adr(self):
        return RF_SETUP

class RFRegisterSetup(RegWrite):

    def __init__(self,mode= RF_DR_HIGH | RF_PWR ):
        super().__init__( adr=RF_SETUP, data= mode )

#

class Status(RegRead):

    def reg_adr(self):
        return STATUS

class StatusSetup(RegWrite):

    def __init__(self,mode= RX_P_NO ):
        super().__init__( adr=RF_SETUP, data= mode )


class StatusClr(RegWrite):

    def __init__(self,clr_RX_DR=True,clr_TX_DS=True,clr_MAX_RT=True):
        flags = 0
        if clr_RX_DR:
            flags |= RX_DR
        if clr_TX_DS:
            flags |= TX_DS
        if clr_MAX_RT:
            flags |= MAX_RT
        super().__init__( adr=STATUS, data= flags )

#

class TxObserve(RegRead):

    def reg_adr(self):
        return OBSERVE_TX

#

class CarrierDectect(RegRead):

    def reg_adr(self):
        return RPD

    def trans(self,val):
        return val & RPD_carrier_detect

#

class RxAdr(RegRead):

    def __init__(self,pipe=0,rc_len=5):
        self.pipe = pipe
        if pipe >= 2:
            rc_len=1
        if pipe > 5:
            raise Exception("no pipe")
        super().__init__(self.reg_adr(),rc_len=rc_len)

    def reg_adr(self):
        return RX_ADDR_P0 + self.pipe

    def trans(self,val):
        if self.rc_len()>1:
            val = bytearray(reversed(val))
        return val
    
def long2lsb(adr,length):
    buf = bytearray()
    for i in range(0,length):
        byt = adr & 0xff
        buf.append( byt ) 
        adr >>= 8
    return buf

class RxAdrSetup(RegWrite):

    def __init__(self,pipe=0,adr=0xe7e7e7e7e7,length=5):
        self.pipe = pipe
        if pipe >= 2:
            length=1
        if pipe > 5:
            raise Exception("no pipe")
        if length>1:
            buf = long2lsb( adr, length )
        else:
            buf = adr
            
        super().__init__( self.reg_adr(), data= buf )

    def reg_adr(self):
        return RX_ADDR_P0 + self.pipe

#

class TxAdr(RegRead):

    def __init__(self,rc_len=5):
        super().__init__(self.reg_adr(),rc_len=rc_len)

    def reg_adr(self):
        return TX_ADDR

    def trans(self,val):
        if self.rc_len()>1:
            val = bytearray(reversed(val)) # lsb to msb
        return val

    
class TxAdrSetup(RegWrite):

    def __init__(self,adr=0,length=5):
        if length>1:
            buf = long2lsb( adr, length )
        else:
            buf = adr
            
        super().__init__( self.reg_adr(), data= buf )

    def reg_adr(self):
        return TX_ADDR

#

class RxPayloadLen(RegRead):

    def __init__(self,pipe=0):
        self.pipe = pipe
        if pipe > 5:
            raise Exception("no pipe")
        super().__init__(self.reg_adr())

    def reg_adr(self):
        return RX_PW_P0 + self.pipe

class RxPayloadLenSetup(RegWrite):

    def __init__(self,pipe=0,payload_len=32):
        self.pipe = pipe
        if pipe >= 2:
            length=1
        if pipe > 5:
            raise Exception("no pipe")
        payload_len &= RX_PW_bytes 
        super().__init__( self.reg_adr(), data= payload_len )

    def reg_adr(self):
        return RX_ADDR_P0 + self.pipe

#

class FifoStatus(RegRead):

    def reg_adr(self):
        return FIFO_STATUS

#

class DynPayload(RegRead):
    
    def reg_adr(self):
        return DYNPD
    
class DynPayloadSetup(RegWrite):

    def __init__(self,pipe=0):
        pipe &= 0b0111_1111
        super().__init__( adr=DYNPD, data= pipe )
    
#

class Feature(RegRead):
    
    def reg_adr(self):
        return FEATURE
    
    def trans(self,val):
        return val & 0b111
    
class FeatureSetup(RegWrite):

    def __init__(self,mode=0):
        mode &= 0b111
        super().__init__( adr=FEATURE, data= mode )

#

