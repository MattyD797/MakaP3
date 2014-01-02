import re

from maka.hmmc.HmmcDocument101 import Station
import maka.util.TextUtils as TextUtils


class HmmcCommandInterpreter101(object):
    
    
    extensionName = 'HMMC Command Interpreter 1.01'
    documentFormatNames = frozenset(('HMMC Document Format 1.01', "'96 MMRP Grammar 1.01"))


    def interpretCommand(self, command):
        
        tokens = _tokenizeCommand(command)
        
        if len(tokens) == 0:
            return
        
        try:
            cmd = _commands[tokens[0]]
            
        except KeyError:
            raise # TODO: Handle this.
        
        else:
            return cmd(*tokens[1:])
    
    
_compoundTokenRe = re.compile(r'^(\D+)(\d+)$')


def _tokenizeCommand(command):
    
    tokens = TextUtils.tokenizeString(command)
    
    if len(tokens) != 0:
        
        m = _compoundTokenRe.match(tokens[0])
        
        if m is not None:
            tokens = list(m.groups()) + tokens[1:]

    return tokens            


class _SimpleCommand(object):
    
    def __init__(self, template, obsClass):
        
        parts = template.split()
        self.cmdName = parts[0]
        self.paramNames = parts[1:]
        self.obsClass = obsClass
        
    def __call__(self, *args):
        # Construct dictionary mapping field names to values.
        # Construct and return observation.
        print(self.cmdName, args)
    
    
_commands = dict((c.cmdName, c) for c in [
    _SimpleCommand(
        'station id name latitudeDegrees latitudeMinutes longitudeDegrees longitudeMinutes '
        'elevation magneticDeclination', Station)
])
