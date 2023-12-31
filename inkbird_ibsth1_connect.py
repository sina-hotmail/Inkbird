from bluepy import btle
import struct

def get_ibsth1_data(macaddr):
    peripheral = btle.Peripheral(macaddr)
    characteristic = peripheral.readCharacteristic(0x2d)
    (temp, humid, unknown1, unknown2, unknown3) = struct.unpack('<hhBBB', characteristic)
    
    characteristic2 = peripheral.readCharacteristic(0x03)
    ( batt ,) = struct.unpack( 'B' , characteristic2)

    sensorValue = {
            'Temperature': temp / 100,
            'Humidity': humid / 100,
            'unknown1': unknown1,
            'unknown2': unknown2,
            'unknown3': unknown3,
            'Battery' : batt
        }
    return sensorValue
