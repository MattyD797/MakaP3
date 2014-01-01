'''Manages application extensions.'''


extensions = {}


# TODO: Review existing open source extension mechanisms (including Enthought's) and either
# use one of those or implement one more suitable to this project.


'''
extension classes:

Field
Observation
Document

FieldFormat
ObservationFormat
DocumentFormat

DocumentFileFormat

Perhaps every extension class should be a subclass of an `Extension` class.
'''


def initialize():
    
    from maka.format.MakaDocumentFileFormat import MakaDocumentFileFormat
    _addExtensions('DocumentFileFormat', [MakaDocumentFileFormat])
    
    '''
    Document extensions are:
        "'96 MMRP Grammar 1.01"
        "HMMC Document 1.01"
    
    Document format extensions are:
        "'96 MMRP Grammar 1.01"
        "HMMC Document Format 1.01"
        
    Command interpreter extensions are:
        "HMMC Command Interpreter 1.01"
    '''
    
    from maka.hmmc.HmmcDocumentFormat101 import HmmcDocumentFormat101, MmrpDocumentFormat101
    _addExtensions('DocumentFormat', [HmmcDocumentFormat101, MmrpDocumentFormat101])
    
    from maka.hmmc.HmmcCommandInterpreter101 import HmmcCommandInterpreter101
    _addExtensions('CommandInterpreter', [HmmcCommandInterpreter101])
    
    
def _addExtensions(typeName, exts):
    extensions[typeName] = dict((ext.extensionName, ext) for ext in exts)
