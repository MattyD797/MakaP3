from __future__ import print_function

import datetime
import re

from maka.hmmc.HmmcDocument101 import Station, TheoData
from maka.text.CommandInterpreterError import CommandInterpreterError
from maka.util.SerialNumberGenerator import SerialNumberGenerator
import maka.device.DeviceManager as DeviceManager
import maka.text.TokenUtils as TokenUtils


# TODO: Implement unquoted comments for HMMC?


_compoundTokenRe = re.compile(r'^(\D+)(\d+)$')


class HmmcCommandInterpreter101(object):
    
    
    extensionName = 'HMMC Command Interpreter 1.01'
    documentFormatNames = frozenset(('HMMC Document Format 1.01', "'96 MMRP Grammar 1.01"))


    def __init__(self, doc):
        super(HmmcCommandInterpreter101, self).__init__()
        self.obsNumGenerator = _createObsNumGenerator(doc)
        self._theodolite = None
        
        
    @property
    def theodolite(self):
        if self._theodolite is None:
            self._theodolite = DeviceManager.getDevice('Theodolite')
        return self._theodolite
    
    
    def interpretCommand(self, command):
        
        tokens = self._tokenizeCommand(command)
        
        if len(tokens) == 0:
            return
        
        try:
            cmd = _commands[tokens[0]]
            
        except KeyError:
            raise CommandInterpreterError('Unrecognized command "{:s}".'.format(tokens[0]))
        
        else:
            return cmd(tokens[1:], self)
    
    
    def _tokenizeCommand(self, command):
        
        tokens = TokenUtils.tokenizeString(command)
        
        # TODO: Offer the following only as an HMMC customization? It might be better for the
        # default command parser to be simpler.
        if len(tokens) != 0:
            
            m = _compoundTokenRe.match(tokens[0])
            
            if m is not None:
                tokens = list(m.groups()) + tokens[1:]
    
        return tokens            


def _createObsNumGenerator(doc):
    
    maxObsNum = -1
    
    for obs in doc.observations:
        
        try:
            obsNum = getattr(obs, 'observationNum')
        except AttributeError:
            continue
        
        if obsNum > maxObsNum:
            maxObsNum = obsNum
            
    return SerialNumberGenerator(maxObsNum + 1)
        
        
class _Command(object):
    
    
    def __init__(self, template, obsClass):
        
        super(_Command, self).__init__()
        
        parts = template.split()
        self.cmdName = parts[0]
        self.paramNames = parts[1:]
        
        self.obsClass = obsClass
        
        
    def __call__(self, args, interpreter):
        # Construct dictionary mapping field names to values.
        # Construct and return observation.
        print(self.cmdName, args)
    
    
class _TheoDataCommand(_Command):
    
    
    def __init__(self):
        super(_TheoDataCommand, self).__init__('z', TheoData)
        
        
    def __call__(self, args, interpreter):
        
        obsNum = interpreter.obsNumGenerator.nextNumber
        
        date, time = _getCurrentDateAndTime()
        
        theodolite = interpreter.theodolite
        
        try:
            declination, azimuth = theodolite.readAngles()
        except Exception as e:
            raise CommandInterpreterError('Theodolite read failed. ' + str(e))
        
        return self.obsClass(
            observationNum=obsNum, date=date, time=time, declination=declination, azimuth=azimuth)
    
        
def _getCurrentDateAndTime():
    dt = datetime.datetime.now()
    return (dt.date(), dt.time())


_commands = dict((c.cmdName, c) for c in [
    _TheoDataCommand(),
    _Command(
        'station id name latitudeDegrees latitudeMinutes longitudeDegrees longitudeMinutes '
        'elevation magneticDeclination', Station)
])
