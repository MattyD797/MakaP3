class Edit(object):
    
    
    def __init__(self, name):
        self._name = name
        
        
    @property
    def name(self):
        return self._name
    
    
    @property
    def inverse(self):
        raise NotImplementedError()
    
    
    def do(self):
        raise NotImplementedError()
    
    
class EditHistory(object):
    
    
    def __init__(self):
        self.clear()
        
        
    def clear(self):
        self._edits = []
        self._redoIndex = 0
        self._savedIndex = 0
    
    
    @property
    def documentSaved(self):
        return self._savedIndex == self._redoIndex
    
    
    def markDocumentSaved(self):
        self._savedIndex = self._redoIndex
        
        
    def append(self, edit):
        
        if self._redoIndex != len(self._edits):
            del self._edits[self._redoIndex:]
            if self._savedIndex is not None and self._savedIndex > len(self._edits):
                self._savedIndex = None
            
        self._edits.append(edit)
        self._redoIndex = len(self._edits)
    
    
    @property
    def undoName(self):
        index = self._redoIndex - 1
        if index < 0:
            return None
        else:
            return self._edits[index].name
        
    
    @property
    def redoName(self):
        try:
            return self._edits[self._redoIndex].name
        except IndexError:
            return None
        
        
    def undo(self):
        
        try:
            edit = self._edits[self._redoIndex - 1]
        except IndexError:
            raise IndexError('No edits to undo.')
        
        inverse = edit.inverse
        inverse.do()
        
        self._redoIndex -= 1
        
        return inverse
        
        
    def redo(self):
        
        try:
            edit = self._edits[self._redoIndex]
        except IndexError:
            raise IndexError('No edits to redo.')
        
        edit.do()
        
        self._redoIndex += 1
        
        return edit
