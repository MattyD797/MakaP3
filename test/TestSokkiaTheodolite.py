from __future__ import print_function

from serial import Serial
import math
import serial

from maka.device.SokkiaTheodolite import SokkiaDt4Theodolite
from maka.device.TheodoliteError import TheodoliteError


_SERIAL_PORT_NAME = '/dev/cu.usbserial'


def _main():
    
    _readAnglesUsingTheodoliteClass()
#    _readAnglesSimple()
#    _demonstrateExceptionLeak()
#    _demonstrateHangOnClose()
    
    
def _readAnglesUsingTheodoliteClass():
    
    try:
        theodolite = SokkiaDt4Theodolite(_SERIAL_PORT_NAME)
        vertical, horizontal = theodolite.readAngles()
        vertical = _toString(vertical)
        horizontal = _toString(horizontal)
        print('read {:s} {:s}'.format(vertical, horizontal))
        
    except ValueError as e:
        print(str(e))
        
    except TheodoliteError as e:
        print(str(e))
        
        
def _toString(angle):
    
    angle *= 180. / math.pi
    
    seconds = int(round(angle * 3600))
    degrees = seconds // 3600
    seconds -= degrees * 3600
    minutes = seconds // 60
    seconds -= minutes * 60
    
    return '{:d}:{:02d}:{:02d}'.format(degrees, minutes, seconds)  


def _readAnglesSimple():
    
    port = Serial(
        port=None,
        baudrate=1200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
        writeTimeout=3)
    
    port.port = _SERIAL_PORT_NAME
    port.open()
    
    try:
        port.write('\x00')
        print('read "{:s}"'.format(port.read(23)))
        
    except Exception as e:
        print('{:s} {:s}'.format(e.__class__.__name__, str(e)))
        
    finally:
        port.close()


def _demonstrateExceptionLeak():
    Serial('/dev/nonexistent')
    
    
def _demonstrateHangOnClose():
    
    # On Mac OS 10.8.5 with a Sokkia USB-to-serial cable based on a
    # Prolific PL-2303 USB-to-serial bridge controller and using version
    # 1.5.1 of Prolific's Mac OS X device driver, I have found that if
    # we raise an exception immediately after the call to port.write
    # below (this happened accidentally at one point during development),
    # then the call to port.close hangs and the only way I have found to
    # make the serial port usable again is to restart the computer.
    # (I couldn't even kill the hung process with kill -9!) I have tried
    # calling port.flushOutput (and also port.flushInput) before calling
    # port.close in an attempt to avoid this problem, but it did not help.
    # If we don't write to the port before raising the AttributeError
    # then the hang does not occur.
    # TODO: Understand why the hang occurs and defend against it if possible.
        
    port = Serial(
        port=None,
        baudrate=1200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
        writeTimeout=3)
    
    port.port = _SERIAL_PORT_NAME
    port.open()
    
    try:
        port.write('\x00')
        raise AttributeError()
        
    finally:
        port.close()
        
        
if __name__ == '__main__':
    _main()
