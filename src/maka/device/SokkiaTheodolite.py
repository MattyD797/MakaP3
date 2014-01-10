'''
Module containing classes `LietzDt4Theodolite` and `TheodoliteError`.

Note that this module depends on the PySerial serial communications Python extension.
'''


from __future__ import print_function

import math

from maka.device.SerialPort import SerialPort
from maka.device.TheodoliteError import TheodoliteError


_TILT_ERROR_MESSAGE = 'Tilt angle is outside of compensation range. Please re-level theodolite.'

_THEODOLITE_ERROR_MESSAGES = {                     
    '100': 'Could not measure horizontal angle. Please re-index horizontal circle.',
    '101': 'Could not measure vertical angle. Please re-index vertical circle.',
    '114': _TILT_ERROR_MESSAGE,
    '115': _TILT_ERROR_MESSAGE,
    '116': _TILT_ERROR_MESSAGE,
    '117': _TILT_ERROR_MESSAGE
}
'''
Theodolite error messages, from page 19 of the Sokkia DT4/DT4S Operator's Manual.
The manual is available at http://www.glm-laser.com/glm/files/operators_manual_dt4_and_dt4s.pdf
as of 19 November 2013.
'''


class SokkiaTheodolite(object):
    
    '''Reads vertical and horizontal angles a Sokkia theodolite through a serial port.'''
    
    
    def __init__(
        self,
        serialPortName,
        baudRate,
        numDataBits,          # 5, 6, 7, 8
        parity,               # 'None', 'Even', 'Odd', 'Mark', 'Space'
        numStopBits,          # 1, 1.5, 2
        readCommand,          # e.g. '\x00'
        dataFormat,           # e.g. `hv`
        readTimeout=3,
        writeTimeout=3):
        
        '''
        Initializes this theodolite.
        
        :Parameters:
        
            serialPortName : `str`
                the name of the serial port through which to communicate with the theodolite,
                for example `'COM1'` on Windows or `'/dev/{cu,tty}.usbserial'` on Mac OS X.
                
            baudRate : `int`
                the baud rate for serial communication with the theodolite, for example 1200.
                
            numDataBits : `int`, either 5, 6, 7, or 8
                the number of data bits for serial communication with the theodolite.
                
            parity : `str`, either `'None'`, `'Even'`, `'Odd'`, `'Mark'`, or `'Space'`.
                the parity for serial communication with the theodolite.
                
            numStopBits : `float`, either 1, 1.5, or 2
                the number of stop bits for serial communication with the theodolite.
                
            readCommand : `str`
               the command to send to the theodolite to read data from it.
               
            dataFormat : `str`
               the format of the data read from the theodolite.
               
               The format should contain two or three characters, including an `'h'`
               (for horizontal angle), a `'v'` (for vertical angle), and an optional
               `'d'` (for distance), for example `'hv'` or `'dvh'`. The order of the
               characters in the format indicates the order of the fields included in
               the data returned by the theodolite. This order varies with theodolite
               model. For example, it is 'dvh' for the Sokkia DT4 theodolite but 'hv'
               for the DT500.
               
            readTimeout : `float`
                the serial communication read timeout in seconds, or `None` for no timeout.
                
            writeTimeout : `float`
                the serial communication write timeout in seconds, or `None` for no timeout.
                
        :Raises ValueError:
            if one of the specified parameter values is out of range or otherwise bad.
            
        :Raises TheodoliteException:
            if the specified serial port cannot be initialized.
        '''
        
        self._readCommand = self._checkReadCommand(readCommand)
        self._dataFormat = self._checkDataFormat(dataFormat)
        self._serialPort = SerialPort(
            serialPortName, baudRate, numDataBits, parity, numStopBits, readTimeout, writeTimeout,
            TheodoliteError)
        
        
    def _checkReadCommand(self, readCommand):
        
        if not isinstance(readCommand, str):
            raise ValueError('Theodolite read command must be string.')
        
        return readCommand
    
    
    def _checkDataFormat(self, dataFormat):
        
        if not isinstance(dataFormat, str):
            raise ValueError('Theodolite data format must be string.')
        
        h = dataFormat.count('h')
        v = dataFormat.count('v')
        d = dataFormat.count('d')
        
        if h != 1 or v != 1 or d > 1 or h + v + d != len(dataFormat):
            raise ValueError(
                ('Bad theodolite data format "{:s}". Format must contain one "h", one "v", '
                 'at most one "d", and no other characters.').format(dataFormat))
        
        return dataFormat
    
    
    def readAngles(self):
        
        '''
        Reads vertical and horizontal angles from this theodolite.
        
        :Returns:
            a pair `(verticalAngle, horizontalAngle)` of angles in radians.
            
        :Raises TheodoliteError:
            if data cannot be read from the theodolite, if the read data are not
            in the expected form, or if the theodolite reports a measurement error.
        '''
        
        port = self._serialPort
        
        port.open()
        
        try:
            port.write(self._readCommand)
            return self._readAngles()
        finally:
            port.close()
                        
            
    def _readAngles(self):
        
        # For error reporting in the `_read` method, we accumulate read data in `self._data`.
        self._data = ''
        
        for (i, c) in enumerate(self._dataFormat):
            
            if i != 0:
                # not first field
                
                # skip single space
                self._read(1)
                
            if c == 'v':
                # vertical angle
                
                v = self._readAngle('vertical')
                
            elif c == 'h':
                # horizontal angle
                
                h = self._readAngle('horizontal')
                
            else:
                # distance
                
                self._read(7)
                
        return (v, h)
    
    
    def _read(self, numBytes):
        
        data = self._serialPort.read(numBytes)
        self._data += data
        
        if len(data) != numBytes:
            
            if len(self._data) == 0:
                message = 'No data were received.'
            else:
                message = 'Data received were "{:s}".'.format(self._data)
                
            raise TheodoliteError('Theodolite read timed out. {:s}'.format(message))
        
        return data
        
        
    def _readAngle(self, description):
                
        # Read the next character from the theodolite. This will be an "E" if the theodolite
        # is reporting an error, or a digit if it is reporting an angle.
        c = self._read(1)
        
        if c == 'E':
            # theodolite is reporting an error
            
            # Read three-digit error code.
            errorCode = self._read(3)
            
            message = _THEODOLITE_ERROR_MESSAGES.get(
                errorCode, 'No further explanation is available.')
                
            raise TheodoliteError(
                'Theodolite read returned error {:s}. {:s}'.format(errorCode, message))
        
        else:
            # theodolite is reporting an angle
            
            # Read remaining digits of dddmmss angle and convert from degrees to radians.
            return self._toRadians(c + self._read(6), description)

    
    def _toRadians(self, angleString, description):
        
        try:
            degrees = int(angleString[0:3])
            minutes = int(angleString[3:5])
            seconds = int(angleString[5:7])
            
        except ValueError:
            raise TheodoliteError(
                'Bad {:s} angle "{:s}" in string "{:s}" received from theodolite.'.format(
                    description, angleString, self._data))
            
        else:
            return (degrees + minutes / 60. + seconds / 3600.) * math.pi / 180.


class SokkiaDt4Theodolite(SokkiaTheodolite):
    
    extensionName = 'Sokkia DT4 Theodolite'
    
    def __init__(self, serialPortName=None, readTimeout=3, writeTimeout=3):
        
        super(SokkiaDt4Theodolite, self).__init__(
            serialPortName=serialPortName,
            baudRate=1200,
            numDataBits=8,
            parity='None',
            numStopBits=1,
            readCommand='\x00',
            dataFormat='dvh',
            readTimeout=readTimeout,
            writeTimeout=writeTimeout)
    
    
class SokkiaDt500Theodolite(SokkiaTheodolite):
    
    extensionName = 'Sokkia DT500 Theodolite'
    
    def __init__(self, serialPortName=None, readTimeout=3, writeTimeout=3):
        
        super(SokkiaDt500Theodolite, self).__init__(
            serialPortName=serialPortName,
            baudRate=1200,
            numDataBits=8,
            parity='None',
            numStopBits=1,
            readCommand='\x00',
            dataFormat='hv',
            readTimeout=readTimeout,
            writeTimeout=writeTimeout)
