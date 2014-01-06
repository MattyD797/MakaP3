import re

from maka.hmmc.HmmcDocument101 import Station, TheoData
import maka.text.TokenUtils as TokenUtils


# TODO: Implement unquoted comments for HMMC?


_compoundTokenRe = re.compile(r'^(\D+)(\d+)$')


class HmmcCommandInterpreter101(object):
    
    
    extensionName = 'HMMC Command Interpreter 1.01'
    documentFormatNames = frozenset(('HMMC Document Format 1.01', "'96 MMRP Grammar 1.01"))


    def interpretCommand(self, command):
        
        tokens = self._tokenizeCommand(command)
        
        if len(tokens) == 0:
            return
        
        try:
            cmd = _commands[tokens[0]]
            
        except KeyError:
            raise # TODO: Handle this.
        
        else:
            return cmd(*tokens[1:])
    
    
    def _tokenizeCommand(self, command):
        
        tokens = TokenUtils.tokenizeString(command)
        
        # TODO: Offer the following only as an HMMC customization? It might be better for the
        # default command parser to be simpler.
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
    _SimpleCommand('z arg', TheoData),
    _SimpleCommand(
        'station id name latitudeDegrees latitudeMinutes longitudeDegrees longitudeMinutes '
        'elevation magneticDeclination', Station)
])
