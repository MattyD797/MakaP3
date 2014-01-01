class ObservationFormat(object):
    
    
    def __init__(self, obsClass):
        super(ObservationFormat, self).__init__()
        self._obsClass = obsClass
        self._fieldOrder = ()
        
        
    @property
    def observationClass(self):
        return self._obsClass
    
    
    def formatObservation(self, obs):
        raise NotImplementedError()
    
    
    def parseObservation(self, s):
        raise NotImplementedError()
    
        
    @property
    def fieldOrder(self):
        return self._fieldOrder
    
    
    def getFieldFormat(self, fieldName):
        raise NotImplementedError()
    
    
    def formatFieldValue(self, fieldName, obs, editing=False):
        format = self.getFieldFormat(fieldName)
        value = getattr(obs, fieldName)
        return format.format(value, editing)
    
    
    def parseFieldValue(self, fieldName, value, editing=False):
        format = self.getFieldFormat(fieldName)
        return format.parse(value, editing)
