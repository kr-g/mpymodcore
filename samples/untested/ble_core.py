
"""

work in progress

samples at the end of the file

"""


"""
    (c)2020 K. Goger (k.r.goger@gmail.com)
    legal: https://github.com/kr-g/mpymodcore/blob/master/LICENSE
"""


import sys
import struct
import time

import binascii

import bluetooth
from bluetooth import BLE

from micropython import const
import machine
from machine import Pin


_IRQ_CENTRAL_CONNECT                 = const(1 << 0)
_IRQ_CENTRAL_DISCONNECT              = const(1 << 1)
_IRQ_GATTS_WRITE                     = const(1 << 2)
_IRQ_GATTS_READ_REQUEST              = const(1 << 3)
_IRQ_SCAN_RESULT                     = const(1 << 4)
_IRQ_SCAN_COMPLETE                   = const(1 << 5)
_IRQ_PERIPHERAL_CONNECT              = const(1 << 6)
_IRQ_PERIPHERAL_DISCONNECT           = const(1 << 7)
_IRQ_GATTC_SERVICE_RESULT            = const(1 << 8)
_IRQ_GATTC_CHARACTERISTIC_RESULT     = const(1 << 9)
_IRQ_GATTC_DESCRIPTOR_RESULT         = const(1 << 10)
_IRQ_GATTC_READ_RESULT               = const(1 << 11)
_IRQ_GATTC_WRITE_STATUS              = const(1 << 12)
_IRQ_GATTC_NOTIFY                    = const(1 << 13)
_IRQ_GATTC_INDICATE                  = const(1 << 14)


"""
micropython-git code copy
https://github.com/micropython/micropython/blob/master/examples/bluetooth/ble_advertising.py
"""
# Advertising payloads are repeated packets of the following form:
#   1 byte data length (N + 1)
#   1 byte type (see constants below)
#   N bytes type-specific data

_ADV_TYPE_FLAGS = const(0x01)
_ADV_TYPE_NAME = const(0x09)
_ADV_TYPE_UUID16_COMPLETE = const(0x3)
_ADV_TYPE_UUID32_COMPLETE = const(0x5)
_ADV_TYPE_UUID128_COMPLETE = const(0x7)
_ADV_TYPE_UUID16_MORE = const(0x2)
_ADV_TYPE_UUID32_MORE = const(0x4)
_ADV_TYPE_UUID128_MORE = const(0x6)
_ADV_TYPE_APPEARANCE = const(0x19)


# Generate a payload to be passed to gap_advertise(adv_data=...).
def advertising_payload(limited_disc=False, br_edr=False, name=None, services=None, appearance=0):
    payload = bytearray()

    def _append(adv_type, value):
        nonlocal payload
        payload += struct.pack("BB", len(value) + 1, adv_type) + value

    _append(
        _ADV_TYPE_FLAGS,
        struct.pack("B", (0x01 if limited_disc else 0x02) + (0x00 if br_edr else 0x04)),
    )

    if name:
        _append(_ADV_TYPE_NAME, name)

    if services:
        for uuid in services:
            b = bytes(uuid)
            if len(b) == 2:
                _append(_ADV_TYPE_UUID16_COMPLETE, b)
            elif len(b) == 4:
                _append(_ADV_TYPE_UUID32_COMPLETE, b)
            elif len(b) == 16:
                _append(_ADV_TYPE_UUID128_COMPLETE, b)

    # See org.bluetooth.characteristic.gap.appearance.xml
    _append(_ADV_TYPE_APPEARANCE, struct.pack("<h", appearance))

    return payload

"""
end of micropython-git code copy
"""

"""
https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.gap.appearance.xml
"""

APPEARANCE_GENERIC_COMPUTER = const(128)


class BtService(object):
    
    def __init__(self):
        self.bt = None
        self.ble = None
        self._handle = None
        self.read_handle = None
        self.notify_handle = None
        self.write_handle = None
    
    def service(self):
        return self.service_uuid(), self.service_characteristics()
    
    def service_characteristics(self):
        charac = []
        if self.can_read():
            if not self.can_notify():
                charac.append( self.characateristic(bluetooth.FLAG_READ) )
            if self.can_notify():
                charac.append( self.characateristic(bluetooth.FLAG_READ|bluetooth.FLAG_NOTIFY) )
        if self.can_write():
            charac.append( self.characateristic(bluetooth.FLAG_WRITE) )
        return tuple( charac )

    def _pop_handles(self):
        hndl = list(self._handle)
        if self.can_read():
            self.read_handle = hndl.pop(0)
#        if self.can_notify():
#            self.notify_handle = hndl.pop(0)
        if self.can_write():
            self.write_handle = hndl.pop(0)

    def service_uuid(self):
        return bluetooth.UUID( self._service() )

    def characateristic(self,mode):
        return self.charac_uuid(), mode 
     
    def charac_uuid(self):
        return bluetooth.UUID( self._charac() )

    def can_read(self):
        return self.mode()[0]
    
    def can_notify(self):
        return self.mode()[1]
    
    def can_write(self):
        return self.mode()[2]

    def _to_hex(self,ident,plain=True,group=2):
        ident = binascii.hexlify( ident ).decode()
        if plain:
            return ident
        return ':'.join(ident[i:i+2] for i in range(0,len(ident),group))

    def on_register(self):
        self.write()
    
    def read(self,data):
        #print("hndl",data)
        data = self.ble.gatts_read( self.write_handle )
        print(self.__class__.__name__,"read data",data)
        self._read(data)
    
    def write( self, data=None ):
        if data==None:
            data = self._write()
        self.write_adapt( data )
        if self.can_notify():
            self.bt.notify( self )
            
    def write_adapt(self, data ):
        print(self.__class__.__name__,"write data",data)
        if data!=None and len(data)>0:
            self.ble.gatts_write( self.read_handle, data )

    #
    # overload
    #

    # refer to
    # https://www.bluetooth.com/de/specifications/gatt/services/   
    def _service(self):
        raise Exception("implementation missing")
    
    # refer to
    # https://www.bluetooth.com/de/specifications/gatt/characteristics/   
    def _charac(self):
        raise Exception("implementation missing")
        
    def mode(self):
        # read, notify, write 
        return True, False, False
        
    def _read(self,data):
        pass
    
    def _write(self):
        pass
        

class Bluetooth(object):
    
    def __init__(self):
        self.ble = BLE()
        if not self.ble.active():
            self.ble.active(True)
            
        self.connections = set()
        self.ble.irq(handler=self._irq_handler)
        
        self.services = {}
        self.payload = b''
        
    def add(self,btserv):
        uuid = btserv.service_uuid() 
        if uuid not in self.services:
            self.services[uuid]=list()
        self.services[uuid].append(btserv)
        
    def remove(self,btserv):
        self.services[btserv._service].remove(btserv)
        ## todo len -> del key

    def all_services(self):
        
        keys = []
        all = []
        
        for servk in self.services.keys():
            keys.append(servk)
            flatten = list()
            _all = list(map( lambda x : flatten.extend(x.service_characteristics()), self.services[servk] ))
            
            all.append( (servk, tuple(flatten)) )
        
        return tuple(all), keys
    
    def all_service_uuids(self):
        return list(self.services.keys())
    
    def register(self):
        # stop advertising
        #self.advertise_stop()
        
        all_services, keys = self.all_services()
        all_handles = self.ble.gatts_register_services( all_services )
      
        #print(list(zip(all_handles, all_services )))
      
        for hndl, serv_uuid  in zip(all_handles, all_services ):
            for serv in self.services[serv_uuid[0]]:
                serv.bt = self
                serv.ble = self.ble
                handle = hndl
                #print(handle,serv_uuid[0])
                serv._handle = handle
                serv._pop_handles()
                serv.on_register()
    
    def advertise(self):
        name = "modcore-bt"#+self.sysid()
        self.payload = advertising_payload(
            name=name, services=self.all_service_uuids(), appearance=APPEARANCE_GENERIC_COMPUTER
        )
        self._advertise()

    def _advertise(self, interval_us=500000, payload=None ):
        print( self.payload )
        if payload==None:
            payload = self.payload
        self.ble.gap_advertise(interval_us, adv_data=payload )
        
    def advertise_stop(self):
        self.payload = b''
        self._advertise(interval_us=None)

    def notify( self, serv ):
        for conn in self.connections:
            self.ble.gatts_notify( conn, serv.read_handle )
    
    def mac(self,plain=True):
        _id = self.ble.config("mac")
        return self._adr(_id,plain)
    
    def sysid(self,plain=True):
        _id = machine.unique_id()
        return self._adr(_id,plain)
        
    def _adr(self,ident,plain=True,group=2):
        ident = binascii.hexlify( ident ).decode()
        if plain:
            return ident
        return ':'.join(ident[i:i+2] for i in range(0,len(ident),group))
    
    def _irq_handler( self, event, data ):
        
        print( "irq", event, data )
        
        if event == _IRQ_CENTRAL_CONNECT:
            # A central has connected to this peripheral.
            conn_handle, addr_type, addr = data
            self.connections.add(conn_handle)
            
        elif event == _IRQ_CENTRAL_DISCONNECT:
            # A central has disconnected from this peripheral.
            conn_handle, addr_type, addr = data
            self.connections.remove(conn_handle)
            self._advertise()

        elif event == _IRQ_GATTS_WRITE:
            # A central has written to this characteristic or descriptor.
            conn_handle, attr_handle = data
            for uuid in self.services.keys():
                for c in self.services[uuid]:
                    if c.write_handle==attr_handle:
                        c.read(data)
                        return


#
# just some samples - NOT - gatt compliant - values have different format
#


class SystemID_BtService(BtService):
    
    def _service(self):
        return 0x183C # org.bluetooth.service.device_information
    
    def _charac(self):
        return 0x2A25 # org.bluetooth.characteristic.serial_number_string
            
    def _write( self ):
        return "modcore/"+self._to_hex( machine.unique_id() )


class Clock_BtService(BtService):
    
    def _service(self):
        return 0x1805 # org.bluetooth.service.current_time
    
    def _charac(self):
        return 0x2A2B # org.bluetooth.characteristic.current_time
            
    # not gatt compliant...
    def _write( self ):
        ct = time.localtime(time.time())
        return "%02d.%02d.%02d %02d:%02d:%02d" % ( ct[0], ct[1], ct[2], ct[3], ct[4], ct[5]) 
    

class Led_BtService(BtService):
    
    def _service(self):
        return 0x1815 # org.bluetooth.service.automation_io
    
    def _charac(self):
        return 0x2A57 # org.bluetooth.characteristic.digital_output
     
    def mode(self):
        return False, False, True
        
    # nil
    def write_adapt( self, data=None ):
        pass

    # not gatt compliant...
    def _read(self,data):
        led = machine.Pin(21,Pin.OUT)
        if data[0]==0:
            led.on()
        elif data[0]==1:
            led.off()
        elif data[0]==2:
            led.value( not led.value() ) 

 
bt = Bluetooth()

sysid = SystemID_BtService()
bt.add(sysid)

led = Led_BtService()
bt.add(led)

clock = Clock_BtService()
bt.add(clock)

"""
call

bt.register()
bt.advertise()

-> play with bluetoothctl (see below)

bt.advertise_stop()
-end-


can be tested on linux with 'bluetoothctl'

use:

scan on
-> wait until dev appears
scan off
pair dev_id
menu gatt
list-attributes

select-attribute _long_characteristic_name_ (not uuid!!!)

-> for system id, and clock -> read
-> for led -> write [0|1|2] => on|off|toggle

back
remove dev_id

"""
"""
notes:

security:
bluetooth core spec v5.2
- vol 3 part c section 5
- vol 3 part g section 8
- vol 6 part e - low energy link layer security

micropython github
https://github.com/micropython/micropython/pull/5051 

master branch / extmod / modbluetooth.h|c



"""

