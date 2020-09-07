
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

# commands (as in tab. 20 page 51)

R_REGISTER = const(0b000_11111) # 5 bits are adr
W_REGISTER = const(0b001_11111) # 5 bits are adr

#MASK_REGISTER = const(0b000_11111)
UNMASK_REGISTER = const(0b111_00000)

R_RX_PAYLOAD = const(0b0110_0001)
W_TX_PAYLOAD = const(0b1010_0000)

FLUSH_TX = const(0b1110_0001)
FLUSH_RX = const(0b1110_0010)

REUSE_TX_PL = const(0b1110_0011)
R_RX_PL_WID = const(0b0110_0000)

W_ACK_PAYLOAD = const(0b1010_1_111) # 3 bits are PIPE
W_TX_PAYLOAD_NOACK = const(0b1011_0000)

NOP = const(0b1111_1111)

# end-of commands

class Command(object):
    
    def __init__(self,cmd=NOP,data=None,rc_len=0):
        self._cmd = cmd
        self._data = data
        self._rc_len = rc_len
    
    def cmd(self):
        return self._cmd
    
    def data(self):
        return self._data

    def rc_len(self):
        """len of data to read if cmd provides result data"""
        return self._rc_len
    
    def exe( self, hal ):
        val = hal.send_cmd( self.cmd(), self.data(), self.rc_len() )
        return val
         
class RegCmd(Command):
    
    def __init__(self,cmd,adr,data=None,rc_len=0):
        super().__init__(cmd,data,rc_len)
        self._adr = adr
        
    def reg_adr(self):
        return self._adr

    def cmd(self):
        reg = self.reg_adr()
        if reg>=0x18 and reg<=0x1b:
            raise Exception("bad address")
        cmd = self._cmd
        cmd &= UNMASK_REGISTER
        cmd |= reg
        return cmd

class RegRead(RegCmd):

    def __init__(self,adr=0x18,rc_len=1):
        super().__init__(R_REGISTER,adr,rc_len=rc_len)

    def trans(self,val):
        return val

    def exe( self, hal ):
        status, val = super().exe(hal)
        return status, self.trans(val)

class RegWrite(RegCmd):

    def __init__(self,adr=0x18,data=None,rc_len=0):
        super().__init__(W_REGISTER,adr,data,rc_len=rc_len)

#        

class NoOperation(Command):
    pass

class RxPayloadLen(Command):
    
    def __init__(self):
        super().__init__(R_RX_PL_WID,rc_len=1)

# untested

class RxPayload(Command):
    
    def __init__(self,rc_len=1):
        super().__init__(R_RX_PAYLOAD,rc_len=rc_len)

class TxPayLoad(Command):
    # PRIM_RX set to 0 as slave PTX
    def __init__(self,data,ack=True,padding=32):
        mode = W_TX_PAYLOAD if ack else W_TX_PAYLOAD_NOACK
        if padding!=None:
            if len(data)<padding:
                # fill up data block with 0
                # zo have same package size
                pad = [ 0 for i in range(len(data),padding) ]
                data.extend( bytearray( pad ) )
        super().__init__(mode,data=data)
        
class TxPipePayLoad(Command):
    # PRIM_RX set to 1 as master PRX
    def __init__(self,data,pipe=0):
        mode = W_ACK_PAYLOAD | ( pipe & 0b111 )
        super().__init__(mode,data=data)
        
class TxFlush(Command):

    def __init__(self,rc_len=1):
        super().__init__(FLUSH_TX)

class RxFlush(Command):

    def __init__(self,rc_len=1):
        super().__init__(FLUSH_RX)
   
    