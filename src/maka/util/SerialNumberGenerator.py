class SerialNumberGenerator(object):
    
    
    def __init__(self, nextNumber=0):
        super(SerialNumberGenerator, self).__init__()
        self._nextNumber = nextNumber
        
        
    @property
    def nextNumber(self):
        result = self._nextNumber
        self._nextNumber += 1
        return result
    
    
    @nextNumber.setter
    def nextNumber(self, number):
        self._nextNumber = number
