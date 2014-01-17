from __future__ import print_function

import datetime
import re

from maka.hmmc.HmmcDocument101 import Comment, Fix, TheoData
from maka.format.CommandInterpreterError import CommandInterpreterError
from maka.util.SerialNumberGenerator import SerialNumberGenerator
import maka.device.DeviceManager as DeviceManager
import maka.util.TokenUtils as TokenUtils


_COMMAND_NAME_RE = re.compile(r'^')


class HmmcCommandInterpreter101(object):
    
    
    extensionName = 'HMMC Command Interpreter 1.01'
    documentFormatNames = frozenset(('HMMC Document Format 1.01', "'96 MMRP Grammar 1.01"))


    def __init__(self, doc):
        
        super(HmmcCommandInterpreter101, self).__init__()
        
        self._docFormat = doc.documentFormat
        
        self._savedDate = None
        self._savedTime = None
        
        self._obsNumGenerator = _createObsNumGenerator(doc)
        self._commentIdGenerator = _createCommentIdGenerator(doc)
        
        self._theodolite = None
        self._savedDeclination = None
        self._savedAzimuth = None
        
        self._commands = self._createCommands()
        
        
    def _getTheodolite(self):
        
        # We are careful to get the theodolite from the device manager lazily (that is,
        # only when somebody actually tries to access it by invoking this method) so
        # that the relevant device extension can be loaded when and only when it is
        # actually needed.
        if self._theodolite is None:
            self._theodolite = DeviceManager.getDevice('Theodolite')
            
        return self._theodolite
    
    
    def _createCommands(self):
        return dict((c.name, c) for c in [
            _CommentCommand(self),
            _TheoDataCommand(self),
            _PodFix(self),
            _VesselFix(self),
            _SpinnerPodFix(self),
            _TursiopsPodFix(self),
            _TurtlePodFix(self),
            _ReferenceFix(self),
            _BuoyFix(self),
            _OtherFix(self)
        ])


    def interpretCommand(self, command):
        
        try:
            tokens = TokenUtils.tokenizeString(command)
        except ValueError, e:
            raise CommandInterpreterError('Could not parse command. {:s}'.format(str(e)))
        
        if len(tokens) == 0:
            return
        
        try:
            cmd = self._commands[tokens[0]]
            
        except KeyError:
            # first command token is not a command name
            
            # Try to split one or more digits off from the end of the first token.
            try:
                splitTokens = _splitToken(tokens[0])
            except ValueError:
                _handleUnrecognizedCommandName(tokens[0])
            
            # Try to look up first split token as a command name.
            try:
                cmd = self._commands[splitTokens[0]]
            except KeyError:
                _handleUnrecognizedCommandName(tokens[0])
            
            tokens = splitTokens + tokens[1:]
        
        return cmd(tokens[1:])
    
    
    def _getCurrentDateAndTime(self):
        dt = datetime.datetime.now()
        return (dt.date(), dt.time())


    def _getAndSaveCurrentDateAndTime(self):
        self._savedDate, self._savedTime = self._getCurrentDateAndTime()
        return self._getSavedDateAndTime()
    
    
    def _getSavedDateAndTime(self):
        return (self._savedDate, self._savedTime)
    
    
    def _getNextObsNum(self):
        return self._obsNumGenerator.nextNumber
    
    
    def _getNextCommentId(self):
        return self._commentIdGenerator.nextNumber
    
    
    def _getTheodoliteAngles(self):
        try:
            return self._getTheodolite().readAngles()
        except Exception as e:
            raise CommandInterpreterError('Theodolite read failed. ' + str(e))
        
    def _getAndSaveTheodoliteAngles(self):
        self._savedDeclination, self._savedAzimuth = self._getTheodoliteAngles()
        return self._getSavedTheodoliteAngles()
        
        
    def _getSavedTheodoliteAngles(self):
        return (self._savedDeclination, self._savedAzimuth)


def _createObsNumGenerator(doc):
    return _createSerialNumGenerator(doc, _getObsNum)


def _getObsNum(obs):
    try:
        return getattr(obs, 'observationNum')
    except AttributeError:
        return None
        
        
def _createSerialNumGenerator(doc, getNum, defaultInitialNum=0):
    
    maxNum = None
    
    for obs in doc.observations:
        
        n = getNum(obs)
        
        if n is not None and (maxNum is None or n > maxNum):
            maxNum = n
            
    return SerialNumberGenerator(maxNum + 1 if maxNum is not None else defaultInitialNum)
        
        
def _createCommentIdGenerator(doc):
    return _createSerialNumGenerator(doc, _getCommentId)

    
def _getCommentId(obs):
    if obs.__class__.__name__ == 'Comment':
        return obs.id
    else:
        return None
    
    
_COMPOUND_TOKEN_RE = re.compile(r'^(\D+)(\d+)$')


def _splitToken(token):
    
    m = _COMPOUND_TOKEN_RE.match(token)
     
    if m is None:
        raise ValueError()
    
    else:
        return list(m.groups())
        
    
def _handleUnrecognizedCommandName(name):
    raise CommandInterpreterError('Unrecognized command name "{:s}".'.format(name))


class _Command(object):
    
    
    observationClass = None
    '''the class of the observations created by this command.'''
    

    format = None
    '''
    the format of this command.
    
    A command format comprises a *command name* followed by zero or more
    *field names*, all separated by spaces. For example::
    
        'cmd x y'
        
    is the format of a command named `'cmd'` with the two field names
    `'x'` and `'y'`. The field names must be the names of fields of
    observations of type `observationClass`.
    '''
    
    defaultFieldValues = {}
    '''
    the default field values of this command, a dictionary mapping field
    names and tuples of field names to default values.
    
    A default field value may be specified either as a value of the appropriate
    type or as a callable. A callable must take a single argument, a command
    interpreter, and return a value of the appropriate type.
    
    Default values for multiple fields may be specified by a dictionary
    entry whose key is a tuple of field names and whose value is either a
    tuple of values of the appropriate types or a callable that takes
    a command interpreter and returns such a tuple.
    
    Default field values for a command may be specified not only via the
    `defaultFieldValues` attribute of the command's class, but also via
    the `defaultFieldValues` attributes of its ancestor classes. The
    specified dictionaries are combined when a command instance is
    initialized so that when the command is executed the dictionaries
    are effectively consulted for default field values in accordance with
    the command class's method resolution order (MRO).
    '''
    
    
    def __init__(self, interpreter):
        
        super(_Command, self).__init__()
        
        (self._name, self._fieldNames) = self._parseFormat()
        self._maxNumArgs = len(self._fieldNames)
        
        self._accumulateDefaultFieldValues()
        
        self._interpreter = interpreter
        
        obsClassName = self.observationClass.__name__
        self._obsFormat = self._interpreter._docFormat.getObservationFormat(obsClassName)

        
    def _parseFormat(self):
        
        parts = self.format.split()
        
        commandName = parts[0]
        argNames = parts[1:]
        
        self._checkCommandArgNames(argNames, commandName)
        
        return commandName, argNames
        
        
    def _checkCommandArgNames(self, argNames, commandName):
        
        fieldNames = frozenset(field.name for field in self.observationClass.FIELDS)
        
        for name in argNames:
            if name not in fieldNames:
                raise CommandInterpreterError(
                    ('Bad argument name "{:s}" in command "{:s}" format. Argument '
                     'name must be field name for observation type "{:s}".').format(
                        name, commandName, self.observationClass.__name__))
                                              
    
    def _accumulateDefaultFieldValues(self):
        
        # TODO: Check field names and values in `cls.defaultFieldValues` in the following.
        
        self._defaultFieldValues = {}

        for cls in reversed(self.__class__.__mro__[:-1]):
            
            try:
                defaultFieldValues = cls.defaultFieldValues
            except AttributeError:
                continue
            
            self._defaultFieldValues.update(defaultFieldValues)
        
       
    @property
    def name(self):
        return self._name
    
                         
    def __call__(self, args):
        fieldValues = self._getFieldValues(args)
        return self.observationClass(**fieldValues)
    
    
    def _checkNumArgs(self, args):
        
        if len(args) > self._maxNumArgs:
            
            if self._maxNumArgs == 0:
                message = 'Command "{:s}" takes no arguments.'.format(self.name)
            else:
                message = 'Too many arguments for command "{:s}": maximum number is {:d}.'.format(
                              self.name, self._maxNumArgs)
                
            raise CommandInterpreterError(message)
        
        
    def _getFieldValues(self, args):
        
        fieldValues = dict(self._parseArg(arg, i) for i, arg in enumerate(args))
        
        for key, value in self._defaultFieldValues.iteritems():
            
            if isinstance(key, tuple):
                # key is tuple of field names
                
                names = [name for name in key if name not in fieldValues]
                
                if len(names) != 0:
                    # At least one of the named fields does not yet have a value.
                    # We guard the following with this test to avoid invoking callables
                    # to get field values that are not needed. This is particularly
                    # important for stateful callables such as serial number generators.
                    
                    values = value(self._interpreter) if callable(value) else value
                        
                    for i, name in enumerate(key):
                        if name not in fieldValues:
                            fieldValues[name] = values[i]
                            
            else:
                # key is a single field name
                
                if key not in fieldValues:
                    # named field does not yet have a value
                    
                    fieldValues[key] = value(self._interpreter) if callable(value) else value
                    
        return fieldValues
                
                        
    def _parseArg(self, arg, i):
        
        fieldName = self._fieldNames[i]
        fieldFormat = self._obsFormat.getFieldFormat(fieldName)
        
        try:
            value = fieldFormat.parse(arg)
            
        except ValueError, e:
            raise CommandInterpreterError(
                'Could not parse "{:s}" argument for command "{:s}". {:s}'.format(
                    fieldName, self.name, str(e)))
            
        return fieldName, value
            
            
_Interpreter = HmmcCommandInterpreter101


class _NdtCommand(_Command):
    defaultFieldValues = {
        'observationNum': _Interpreter._getNextObsNum,
        ('date', 'time'): _Interpreter._getCurrentDateAndTime
    }
    
    
class _CommentCommand(_NdtCommand):
    observationClass = Comment
    format = 'c text id'
    defaultFieldValues = { 'id': _Interpreter._getNextCommentId }
    

class _TheoDataCommand(_NdtCommand):
    observationClass = TheoData
    format = 'z'
    defaultFieldValues = {
        ('date', 'time'): _Interpreter._getAndSaveCurrentDateAndTime,
        ('declination', 'azimuth'): _Interpreter._getAndSaveTheodoliteAngles
    }
    
    
class _Fix(_NdtCommand):
    observationClass = Fix
    defaultFieldValues = {
        ('date', 'time'): _Interpreter._getSavedDateAndTime,
        ('declination', 'azimuth'): _Interpreter._getSavedTheodoliteAngles
    }
    
    
def _fix(className, commandName, objectType):
    classAttributes = {
        'format': commandName + ' objectId behavioralState',
        'defaultFieldValues': {'objectType': objectType}
    }
    return type(className, (_Fix,), classAttributes)


_PodFix = _fix('_PodFix', 'p', 'Pod')
_VesselFix = _fix('_VesselFix', 'v', 'Vessel')
_SpinnerPodFix = _fix('_SpinnerPodFix', 'sp', 'Spinner pod')
_TursiopsPodFix = _fix('_TursiopsPodFix', 'bn', 'Tursiops pod')
_TurtlePodFix = _fix('_TurtlePodFix', 'tu', 'Turtle pod')
_ReferenceFix = _fix('_ReferenceFix', 'r', 'Reference')
_BuoyFix = _fix('_BuoyFix', 'by', 'Buoy')
_OtherFix = _fix('_OtherFix', 'os', 'Other')
