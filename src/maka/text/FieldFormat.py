class FieldFormat(object):
    
    
    def __init__(self, hint=None):
        self._hint = hint
        
        
    @property
    def hint(self):
        return self._hint
    
    
    def format(self, v, editing=False):
        raise NotImplementedError()
    
    
    def parse(self, s, editing=False):
        raise NotImplementedError()
