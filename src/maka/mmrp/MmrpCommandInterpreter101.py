from __future__ import print_function

import datetime

from maka.command.CommandInterpreterError import CommandInterpreterError
from maka.command.SimpleCommand import SimpleCommand
from maka.command.SimpleCommandInterpreter import SimpleCommandInterpreter
from maka.mmrp.MmrpDocument101 import Comment, Fix, TheoData
from maka.util.SerialNumberGenerator import SerialNumberGenerator
import maka.device.DeviceManager as DeviceManager


class MmrpCommandInterpreter101(SimpleCommandInterpreter):
    
    
    extensionName = 'MMRP Command Interpreter 1.01'
    documentFormatNames = frozenset(["'96 MMRP Grammar 1.01"])


    def __init__(self, doc):
        
        super(MmrpCommandInterpreter101, self).__init__(doc)
        
        self._savedDate = None
        self._savedTime = None
        
        self._obsNumGenerator = _createObsNumGenerator(doc)
        self._commentIdGenerator = _createCommentIdGenerator(doc)
        
        self._theodolite = None
        self._savedDeclination = None
        self._savedAzimuth = None
        
        
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
    
    
    def _getTheodolite(self):
        
        # We are careful to get the theodolite from the device manager lazily (that is,
        # only when somebody actually tries to access it by invoking this method) so
        # that the relevant device extension can be loaded when and only when it is
        # actually needed.
        if self._theodolite is None:
            self._theodolite = DeviceManager.getDevice('Theodolite')
            
        return self._theodolite
    
    
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
    
    
_Interpreter = MmrpCommandInterpreter101


class _NdtCommand(SimpleCommand):
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
