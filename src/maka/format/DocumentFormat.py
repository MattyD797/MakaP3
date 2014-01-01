class DocumentFormat(object):
    
    
    # These must be provided by a subclass.
    extensionName = None
    documentClass = None
    
    
    def formatDocument(self, obsSeq):
        raise NotImplementedError()
    
    
    def parseDocument(self, lines, startLineNum):
        raise NotImplementedError()


    def getObservationFormat(self, obsClassName):
        raise NotImplementedError()
    
    
    def formatObservation(self, obs):
        return self.getObservationFormat(obs.__class__.__name__).formatObservation(obs)


    # TODO: Add parseObservation method?
    