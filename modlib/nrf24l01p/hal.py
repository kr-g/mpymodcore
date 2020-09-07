
"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""

import time
from machine import Pin

R_REGISTER = const(0b000_00000) # 5 bits are adr
W_REGISTER = const(0b001_00000) # 5 bits are adr

R_RX_PAYLOAD = const(0b0110_0001)
R_RX_PL_WID = const(0b0110_0000)

STATUS = 0x07
RX_DR = 1 << 6
TX_DS = 1 << 5
MAX_RT = 1 << 4

FIFO_STATUS = 0x17
RX_EMPTY = 1 << 0

#
# hal layer
#

class HalCmdCtx(object):
    
    def __init__(self,hal):
        self.hal = hal
        
    def __enter__(self):
        self.hal.csn(False)
        return self.hal
    
    def __exit__(self ,ex_type, value, traceback):
        self.hal.csn(True)


def _2_bytes(ba):
    if ba==None:
        return "None"
    if type(ba)==bool:
        return str(ba)
    if type(ba)==int:
        return bin(ba) + "/" + hex(ba)
    rc = "0x"
    for b in ba:
        rc += hex(b)[2:]
    return rc
        
def rc_frmt( rc ):
    return "status= " + _2_bytes(rc[0]) +", rc= "+ _2_bytes(rc[1]) 


_register = {}

class NRF24L01P(object):
    
    def __init__(self, spi, irq_pin=2, ce_pin=15, csn_pin=0, debug=False ):
        self.spi = spi
        self.irq_pin = irq_pin
        self.ce_pin = Pin( ce_pin, Pin.OUT )
        self.csn_pin = Pin( csn_pin, Pin.OUT )
        self.status = 0b1110,0b1110
        self.rx_payload = None
        self.debug = debug
        
        self.intr = None
        
        if self.irq_pin != None:
            self.intr = Pin( self.irq_pin, Pin.IN )
            self.intr.irq(trigger=Pin.IRQ_FALLING, handler=self._handler_irq)
            _register[str(self.intr)]=self

        self._ce_csn(False)
        
    def close(self):
        self.intr.irq(trigger=Pin.IRQ_FALLING, handler=None)
        _register[str(self.irq_pin)]=None

    def exe( self, nrfCommand ):
        return nrfCommand.exe(self)

    def __call__( self, nrfCommand ):
        return self.exe(nrfCommand )

    @staticmethod
    def _handler_irq( irq_pin ):
        #print( "irq", irq_pin )
        hal = _register[str(irq_pin)]
        # read status register tuple
        rc = hal._read_status()
        #print( "irq status", rc_frmt(rc) )
        hal.status = rc
        hal._irq( rc[1] )
     
    def _irq(self,status):
        if self.debug:
            print( "irq status", bin(status) )
        
        if status & RX_DR > 0:
            status = self._irq_rx_dr(status)   
        if status & TX_DS > 0:
            status = self._irq_tx_ds(status)
        if status & MAX_RT > 0:
            status = self._irq_max_rt(status)
        
        # clr the required bits
        if self.debug:
            print( "irq status reset to", bin(status) )
        self._update_reg( STATUS, RX_DR | TX_DS | MAX_RT, status )

    def _irq_rx_dr(self,status):
        if self.debug:
            print( "irq RX_DR" )
            
        while True:
            if self.rx_payload != None:
                if self.debug:
                    print("drop old payload")
            # read payload
            data = self._read_payload()
            self.rx_payload = data
            self.rx_callb( data )
            # clr RX_DR
            # self._update_reg( STATUS, RX_DR, status | RX_DR )
            # read until rx fifo is not empty
            s, fs = self._read_fifo_status()
            if self.debug:
                print("fifo", bin(s), bin(fs))
            if fs & RX_EMPTY > 0:
                # fifo empty
                break
        
        # clear irq bits
        return status | RX_DR
    
    def _read_payload(self):
        rc_len = self._read_payload_len()
        rc,data = self.send_cmd( R_RX_PAYLOAD, rc_len=rc_len )
        return data
    
    def _read_payload_len(self):
        # overload this if fix payload len 
        # get top payload len
        rc, rc_len = self.send_cmd( R_RX_PL_WID, rc_len=1 )
        return rc_len

    def rx_callb(self,data):
        # pop payload here, default discard
        if self.debug:
            print("recv", self.pop_rx() )

    def pop_rx(self):
        try:
            return self.rx_payload
        finally:
            self.rx_payload = None

    def _irq_tx_ds(self,status):
        if self.debug:
            print( "irq TX_DS" )
        self.tx_callb()
        return status | TX_DS

    def tx_callb(self):
        # transmission was ok
        pass

    def _irq_max_rt(self,status):
        if self.debug:
            print( "irq MAX_RT" )
        return status | MAX_RT

    def _update_reg(self,reg,mask,orbits=0):
        # read cmd
        rc,val = self.send_cmd( R_REGISTER | reg, rc_len=1 )
        # mask out existing bits
        val &= ~mask
        # set bits
        val |= orbits
        # write cmd
        rc,val = self.send_cmd( W_REGISTER | reg, rc_len=0 )
        
    def _read_status(self):
        rc = self.send_cmd( STATUS, rc_len=1 )
        return rc 
        
    def _read_fifo_status(self):
        rc = self.send_cmd( FIFO_STATUS, rc_len=1 )
        return rc 
        
    def ce(self,mode=True):
        self.ce_pin.value(mode)
        
    def csn(self,mode=False):
        self.csn_pin.value(mode)
        
    def ce_pulse(self,duration=11): # must be > 10 usec
        self.ce(True)
        time.sleep_us(duration)
        self.ce(False)
                
    def __repr__(self):
        return "nrf24l01p( spi:" + str(self.spi) + ", irq:" + str(self.intr) \
               + ", ce:" + str(self.ce_pin) \
               + ", csn:" + str(self.csn_pin) \
               + " )"

    def _ce_csn( self, enable=True ):
        if enable:
            self.ce( enable )
            self.csn( not enable )
        else:
            self.csn( not enable )
            self.ce( enable )

    def send_cmd( self, cmd, data=None, rc_len=0 ):
        with HalCmdCtx(self) as hal:
            status = bytearray(1)
            rc_data = None
            hal.spi.readinto( status, cmd )
            if data != None:
                if type(data)==int:
                    data = bytearray([data])
                hal.spi.write( data )
            if rc_len>0:
                rc_data = hal.spi.read(rc_len)
                if len(rc_data)==1:
                    rc_data = rc_data [0]
        return status[0], rc_data
    
