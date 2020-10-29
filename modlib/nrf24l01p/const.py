# register table map (as in tab. 28 page 57 ff)
# mnemonics

CONFIG = const(0x00)
MASK_RX_DR = const(1 << 6)
MASK_TX_DS = const(1 << 5)
MASK_MAX_RT = const(1 << 4)
EN_CRC = const(1 << 3)
CRCO = const(1 << 2)
PWR_UP = const(1 << 1)
PRIM_RX = const(1 << 0)

EN_AA = const(0x01)  # Enhanced ShockBurst
ENAA_P5 = const(1 << 5)
ENAA_P4 = const(1 << 4)
ENAA_P3 = const(1 << 3)
ENAA_P2 = const(1 << 2)
ENAA_P1 = const(1 << 1)
ENAA_P0 = const(1 << 0)

EN_RXADDR = const(0x02)
ERX_P5 = const(1 << 5)
ERX_P4 = const(1 << 4)
ERX_P3 = const(1 << 3)
ERX_P2 = const(1 << 2)
ERX_P1 = const(1 << 1)
ERX_P0 = const(1 << 0)

SETUP_AW = const(0x03)
AW_3 = 0b01  # 3 bytes adress
AW_4 = 0b10
AW_5 = 0b11

SETUP_RETR = 0x04  # retransmit delay
ARD_250 = 0b0000 << 4
ARD_500 = 0b0001 << 4
ARD_750 = 0b0010 << 4
# each bit adds 250 us
ARD_4000 = 0b1111 << 4
# retransmit count
ARC_disabled = 0b0000
ARC_1 = 0b0001
ARC_2 = 0b0010
ARC_3 = 0b0011  # default
# each bit counts
ARC_15 = 0b1111

RF_CH = 0x05
RF_CH_freq = 0b0000010

RF_SETUP = 0x06
CONT_WAVE = 1 << 7
RF_DR_LOW = 1 << 5
PLL_LOCK = 1 << 4
RF_DR_HIGH = 1 << 3
#
# [RF_DR_LOW, RF_DR_HIGH]:
# ‘00’ – 1Mbps
# ‘01’ – 2Mbps
# ‘10’ – 250kbps
# ‘11’ – Reserved
#
RF_PWR = 0b11 << 1
# Set RF output power in TX mode
#'00' – -18dBm
#'01' – -12dBm
#'10' – -6dBm
#'11' – 0dBm

STATUS = 0x07
RX_DR = 1 << 6
TX_DS = 1 << 5
MAX_RT = 1 << 4
RX_P_NO = 0b111 << 1  # data pipe for payload
TX_FULL = 1 << 0

OBSERVE_TX = 0x08  # masks
PLOS_CNT = 0b1111 << 4
ARC_CNT = 0b1111

RPD = 0x09
RPD_carrier_detect = 1 << 0

RX_ADDR_P0 = 0x0A  # default 0xE7E7E7E7E7
RX_ADDR_P0_adr = 0xE7E7E7E7E7
RX_ADDR_P1 = 0x0B  # default 0xc2c2c2c2c2
RX_ADDR_P1_adr = 0xC2C2C2C2C2
RX_ADDR_P2 = 0x0C  # default 0xc3
RX_ADDR_P2_adr = 0xC3
RX_ADDR_P3 = 0x0D  # default 0xc4
RX_ADDR_P3_adr = 0xC4
RX_ADDR_P4 = 0x0E  # default 0xc5
RX_ADDR_P4_adr = 0xC5
RX_ADDR_P5 = 0x0F  # default 0xc6
RX_ADDR_P5_adr = 0xC6

TX_ADDR = 0x10  # default 0xE7E7E7E7E7 only PTX
TX_ADDR_adr = 0xE7E7E7E7E7

RX_PW_bytes = 0b11111
RX_PW_P0 = 0x11
RX_PW_P1 = 0x12
RX_PW_P2 = 0x13
RX_PW_P3 = 0x14
RX_PW_P4 = 0x15
RX_PW_P5 = 0x16

FIFO_STATUS = 0x17
TX_REUSE = 1 << 6
FIFO_TX_FULL = 1 << 5
TX_EMPTY = 1 << 4
RX_FULL = 1 << 1
RX_EMPTY = 1 << 0

DYNPD = 0x1C  # dynamic payload length
DPL_P5 = 1 << 5
DPL_P4 = 1 << 4
DPL_P3 = 1 << 3
DPL_P2 = 1 << 2
DPL_P1 = 1 << 1
DPL_P0 = 1 << 0

FEATURE = 0x1D
EN_DPL = 1 << 2
EN_ACK_PAY = 1 << 1
EN_DYN_ACK = 1 << 0

# end-of register table map, mnemonics
