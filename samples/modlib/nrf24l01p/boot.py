# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
import uos as os
import machine
import micropython
import time

# uos.dup<term(None, 1) # disable REPL on UART(0)

print()
print("-" * 7)
print(time.localtime(time.time()))


from machine import Pin, SPI

rf24l01p_spi = SPI(1, baudrate=4_000_000, polarity=0, phase=0)

micropython.alloc_emergency_exception_buf(100)


from modlib.nrf24l01p.const import *

from modlib.nrf24l01p.hal import *
from modlib.nrf24l01p.cmd import *

# for easy checking register settings
# from regcmd import *

# for more easy fine tuned register access
# from regxcmd import *
# from regxcmdconfig import *
# from regxcmdretrans import *
# from regxcmdrfreg import *
# from regxcmdstatus import *

radio = NRF24L01P(rf24l01p_spi, irq_pin=2, debug=True)
print(radio)

print("free", gc.mem_free())
gc.collect()
print("free", gc.mem_free())


default_settings = [
    # keep config and status first
    (CONFIG, EN_CRC),  # slave ptx mode
    (STATUS, RX_DR | TX_DS | MAX_RT),
    # config first since it powers down
    (EN_AA, 0b0111_1111),  # set to 0b0 for nRF2401 compatibility
    (EN_RXADDR, ERX_P1 | ERX_P0),
    (SETUP_AW, AW_5),  # adr width is 5
    (SETUP_RETR, ARD_250 | ARC_3),
    (RF_CH, RF_CH_freq),  # 2.4GHz +2MHz as operating freq as default
    (RF_SETUP, RF_DR_HIGH | RF_PWR),
    (STATUS, RX_DR | TX_DS | MAX_RT),
    (RX_ADDR_P0, RX_ADDR_P0_adr),  # LSB first here
    (RX_ADDR_P1, RX_ADDR_P1_adr),  # symentric defaults!
    (RX_ADDR_P2, RX_ADDR_P2_adr),
    (RX_ADDR_P3, RX_ADDR_P3_adr),
    (RX_ADDR_P4, RX_ADDR_P4_adr),
    (RX_ADDR_P5, RX_ADDR_P5_adr),
    (TX_ADDR, TX_ADDR_adr),
    (RX_PW_P0, 32),  # set payload len to 32 byte fixed
    (RX_PW_P1, 32),
    (RX_PW_P2, 32),
    (RX_PW_P3, 32),
    (RX_PW_P4, 32),
    (RX_PW_P5, 32),
    (DYNPD, 0b0000_0000),
    (FEATURE, 0b000),
]

# use your own setup here !!!
multiceiver_settings = [
    # keep this order
    (RX_ADDR_P0, RX_ADDR_P0_adr + 1),  # LSB first here
    (RX_ADDR_P1, RX_ADDR_P1_adr),  # LSB first here
    # from here onwards only lsb byte of adr p1 !!!
    (RX_ADDR_P2, RX_ADDR_P2_adr),
    (RX_ADDR_P3, RX_ADDR_P3_adr),
    (RX_ADDR_P4, RX_ADDR_P4_adr),
    (RX_ADDR_P5, RX_ADDR_P5_adr),
    # some other settings
    # enable all rx pipes
    (EN_RXADDR, ERX_P0 | ERX_P1 | ERX_P2 | ERX_P3 | ERX_P4 | ERX_P5),
    (RF_CH, RF_CH_freq + 3),  # 2.4GHz + x MHz as operating freq as default
    #
    # your own settings also go here
    #
]


def apply_settings(dev, settings, debug=True):
    """apply the array of given settings in a raw manner"""
    for adr, val in settings:
        rc = dev.exe(RegWrite(adr, val))
        if debug:
            print("adr: ", adr, " val: ", hex(val), rc_frmt(rc))


def setup_master_prx(dev, debug=True):
    apply_settings(dev, multiceiver_settings, debug)


def setup_slave_ptx(dev, pipe=1, adr_width=5, debug=True):
    apply_settings(dev, multiceiver_settings, debug)
    if pipe > 5:
        raise Exception("no pipe")
    tx_adr = multiceiver_settings[0][1]
    if pipe >= 1:
        tx_adr = multiceiver_settings[1][1]
    # convert long int adr to array (reversed order)
    tx_adr = [(tx_adr >> i) & 0xFF for i in range(0, adr_width * 8, 8)]
    if pipe >= 2:
        # set lsb byte
        # make sure to have adr width set up to adr setting
        tx_adr[-1] = multiceiver_settings[pipe][1]
    tx_adr = bytearray(tx_adr)
    if debug:
        print("tx", tx_adr)
    # set tx adr
    dev.exe(RegWrite(TX_ADDR, tx_adr))
    dev.exe(RegWrite(RX_ADDR_P0, tx_adr))


def reset_nrf24(dev, debug=True):
    apply_settings(dev, default_settings, debug)


def power(dev, power=True, master=False, debug=True):
    mode = 0
    if power:
        mode |= PWR_UP
    if master:
        mode |= PRIM_RX
    status, val = dev.exe(RegRead(CONFIG))
    val &= ~(PWR_UP | PRIM_RX)
    val |= mode
    rc = dev.exe(RegWrite(CONFIG, val))
    if debug:
        print("powered: ", mode, rc_frmt(rc))
    # power up ... bit long ...
    time.sleep_ms(3)

    return rc


def status(dev, debug=True):
    status, val = dev._read_status()
    if debug:
        print(bin(val))
    return val


def status_clr(dev):
    status, val = dev.exe(RegWrite(STATUS, RX_DR | TX_DS | MAX_RT))


def fifo(dev, debug=True):
    status, val = dev._read_fifo_status()
    if debug:
        print(bin(val))
    return val


def flush(dev):
    dev(TxFlush())
    dev(RxFlush())
    status_clr(dev)


def slave_enable(dev, pipe=0):
    dev.ce(False)
    reset_nrf24(dev)
    setup_slave_ptx(dev, pipe)
    flush(dev)
    power(dev, master=False)


def slave(pipe=0):
    slave_enable(radio, pipe)

    while True:
        t = str(time.localtime(time.time())[3:6])
        t = bytearray(t)
        rc = radio(TxPayLoad(t))
        radio.ce_pulse(15)
        print(t, rc_frmt(rc))
        if rc[0] & TX_FULL > 0 or rc[0] & MAX_RT > 0:
            print("overflow, flush tx")
            flush(radio)
        time.sleep(3)


def master_enable(dev):
    dev.ce(False)
    reset_nrf24(dev)
    setup_master_prx(dev)
    flush(dev)
    power(dev, master=True)


def master():
    master_enable(radio)
    state = False

    while True:
        if state == False:
            state = True
            radio.ce(state)
            time.sleep_us(150)
        rc = radio(RegRead(STATUS))
        status, fifo_status = radio(RegRead(FIFO_STATUS))
        if status & RX_DR > 0:
            print("unset RX_DR")
            radio._update_reg(STATUS, RX_DR, status | RX_DR)
            radio(RxFlush())
            # above do not work with my chip
            # flush all of them...
            flush(radio)

        if fifo_status & RX_FULL > 0:
            print("flush rx and tx")
            flush(radio)
        if fifo_status & RX_EMPTY == 0:
            state = False
            radio.ce(state)
            # there is data available
            # get the len of the data, works not only with DPL active
            status, rc_len = radio(RxPayloadLen())
            # get the data
            status, data = radio(RxPayload(rc_len=rc_len))
            print(rc_len, data)

        # master is lazy
        # this sleeping period will cause rx overflow in slave
        time.sleep_ms(250)


def shutdown():
    # remove interupt handler
    radio.close()
