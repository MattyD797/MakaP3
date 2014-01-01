from maka.device.SokkiaTheodolite import SokkiaTheodolite as Theodolite
from maka.device.TheodoliteError import TheodoliteError
from MakaTests import TestCase


_initParams = {
    'serialPortName': '/dev/cu.usbserial',
    'baudRate': 1200,
    'numDataBits': 8,
    'parity': 'None',
    'numStopBits': 1,
    'readCommand': '\x00',
    'dataFormat': 'hv'
}


def _params(**kwds):
    p = dict(_initParams)
    p.update(kwds)
    return p


class SokkiaTheodoliteTests(TestCase):
    
    def testPortNameErrors(self):
        t = Theodolite(**_params(serialPortName='/dev/bobo'))
        self._assertRaises(TheodoliteError, t.readAngles)
        
    def testBaudRateErrors(self):
        for baudRate in ['bobo', -200, 0]:
            self._testBadInit(baudRate=baudRate)
            
    def _testBadInit(self, **kwds):
        self._assertRaises(ValueError, Theodolite, **_params(**kwds))
        
    def testNumDataBitsErrors(self):
        for numDataBits in ['bobo', -1, 0, 1, 10]:
            self._testBadInit(numDataBits=numDataBits)
            
    def testParityErrors(self):
        for parity in ['bobo', 0]:
            self._testBadInit(parity=parity)
            
    def testNumStopBitsErrors(self):
        for numStopBits in ['bobo', 0, 1.25]:
            self._testBadInit(numStopBits=numStopBits)
            
    def testReadCommandErrors(self):
        for readCommand in [0, ['\x00']]:
            self._testBadInit(readCommand=readCommand)
            
    def testDataFormatErrors(self):
        for dataFormat in ['bobo', 0]:
            self._testBadInit(dataFormat=dataFormat)
            
    def testReadTimeoutErrors(self):
        for timeout in ['bobo', -1]:
            self._testBadInit(readTimeout=timeout)
            
    def testWriteTimeoutErrors(self):
        for timeout in ['bobo', -1]:
            self._testBadInit(writeTimeout=timeout)
