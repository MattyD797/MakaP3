from maka.text.DocumentFormat import DocumentFormat


class ReprDocumentFormat(DocumentFormat):
    
    
    def __init__(self):
        docClass = self.documentClass
        self._evalGlobals = dict((c.__name__, c) for c in docClass.observationClasses)
        self._evalGlobals.update(dict((c.__name__, c) for c in docClass.fieldClasses))
        
        
    def format(self, obsSeq):
        return '\n'.join(repr(obs) for obs in obsSeq)
    
    
    def parse(self, lines, startLineNums):
        
        observations = []
        lineNum = startLineNums
        
        for line in lines:
            
            if line != '':
                
                # TODO: Protect against code injection.
                # TODO: Handle errors.
                obs = eval(line, self._evalGlobals)
                
                observations.append(obs)
                
            lineNum += 1
            
        return observations
