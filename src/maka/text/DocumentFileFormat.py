import maka.util.ExtensionManager as ExtensionManager


class FileFormatError(Exception):
    pass


class UnrecognizedFileFormatError(FileFormatError):
    pass


def getDocumentFileFormat(filePath):
    _processFile(filePath, lambda format: format)
    
    
def _processFile(filePath, function):
    
    formats = ExtensionManager.extensions['DocumentFileFormat']
    
    # TODO: Make file format extensions singletons, so we don't have to keep re-instantiating them.
    for formatClass in formats.itervalues():
        format = formatClass()
        if format.isFileRecognized(filePath):
            return function(format)
            
    # If we get here, no file format recognized this file.
    raise UnrecognizedFileFormatError(
        'File "{:s}" is not of a known document type.'.format(filePath))
    
    
def readDocument(filePath):
    return _processFile(filePath, lambda format: format.readDocument(filePath))
            
        
class DocumentFileFormat(object):
    
    extensionName = None
    
    # TODO: Handle Unicode. How should we indicate encoding in Maka data files?
    
    def isFileRecognized(self, filePath):
        raise NotImplementedError()
    
    def readDocument(self, filePath):
        raise NotImplementedError()
    
    def writeDocument(self, document, filePath):
        raise NotImplementedError()
