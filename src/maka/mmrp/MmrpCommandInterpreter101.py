from __future__ import print_function

import datetime

from maka.command.CommandInterpreterError import CommandInterpreterError
from maka.command.SimpleCommand import SimpleCommand
from maka.command.SimpleCommandInterpreter import SimpleCommandInterpreter
from maka.mmrp.MmrpDocument101 import (
    Station, Observer, Theodolite, Reference, Role, Start, End, Comment, Pod, Vessel,
    Environment, StartScan, StartWhaleScan, EndScan, StartVesselScan, EndVesselScan,
    Orientation, StartFocalSession,
#    StartPlayback, EndPlayback,
    EndFocalSession, Confidence,
    BinocularFix, TheoData, Fix, Sighting, Behavior, BehavioralState, BehaviorsSynchronous,
    BehaviorsAsynchronous, PodEvent, VesselEvent, Affiliation, Disaffiliation,
#    SuspectedAffiliation, SuspectedDisaffiliation,
    FocalPodLost, Lag, DeleteLastEntry,
    DeleteLastSequence, EyepieceHeight, BubbleCheck, Rebalance, TideHeight, ClosestApproach,
    SurfacingNumber)
from maka.util.SerialNumberGenerator import SerialNumberGenerator
import maka.device.DeviceManager as DeviceManager
import maka.util.AngleUtils as AngleUtils


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
        commands = [c(self) for c in _commandClasses]
        return dict((c.name, c) for c in commands)


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
        v, h = self._getTheodoliteAngles()
        self._savedDeclination = AngleUtils.radiansToDegrees(v) if v is not None else v
        self._savedAzimuth = AngleUtils.radiansToDegrees(h) if h is not None else h
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


_commandNum = 0


def _command(format, obsClass, bases=(SimpleCommand,), defaultFieldValues=None):
    
    global _commandNum
    name = '_Command{:03d}'.format(_commandNum)
    _commandNum += 1
    
    attrs = {
        'observationClass': obsClass,
        'format': format
    }
    if defaultFieldValues is not None:
        attrs['defaultFieldValues'] = defaultFieldValues
        
    return type(name, bases, attrs)
    
    
class _Ndt(SimpleCommand):
    defaultFieldValues = {
        'observationNum': _Interpreter._getNextObsNum,
        ('date', 'time'): _Interpreter._getCurrentDateAndTime
    }
    
    
def _ndt(format, obsClass, defaultFieldValues=None):
    return _command(format, obsClass, (_Ndt,), defaultFieldValues)
    
    
_fixDefaults = [
    (('date', 'time'), _Interpreter._getSavedDateAndTime),
    (('declination', 'azimuth'), _Interpreter._getSavedTheodoliteAngles)
]


def _fix(commandName, objectType):
    format = commandName + ' objectId behavioralState'
    defaultFieldValues = dict(_fixDefaults + [('objectType', objectType)])
    return _ndt(format, Fix, defaultFieldValues)


# TODO: Set `code` field to concatenation of `code` argument and `str(podId)`.
def _beh(code, behavior):
    format = code + ' individualId podId'
    defaultFieldValues = {'code': code, 'behavior': behavior}
    return _ndt(format, Behavior, defaultFieldValues)


def _bst(name, state=None):
    format = name + ' podId'
    if state is None: state = name
    return _ndt(format, BehavioralState, {'state': state})


def _pev(code, event):
    return _objectEvent(code, event, 'pod', PodEvent)
    
    
def _objectEvent(code, event, objectName, obsClass):
    format = code + ' ' + objectName + 'Id'
    defaultFieldValues = {'code': code, 'event': event}
    return _ndt(format, obsClass, defaultFieldValues)


def _vev(code, event):
    return _objectEvent(code, event, 'vessel', VesselEvent)


def _cpa(name, objectType):
    format = name + ' objectId podId'
    return _ndt(format, ClosestApproach, {'objectType': objectType})


_commandClasses = [

    # station setup
    _command('station id name latitudeDegrees latitudeMinutes longitudeDegrees '
             'longitudeMinutes elevation magneticDeclination', Station),
    _command('observer initials name', Observer),
    _command('theodolite id name azimuthOffset declinationOffset', Theodolite),
    _command('reference id name azimuth', Reference),
    _ndt('role observer role', Role),
    
    # start and end of observations
    _ndt('start', Start),
    _ndt('end', End),
    
    _ndt('c text id', Comment, { 'id': _Interpreter._getNextCommentId }),
    
    # tracked objects
    _command('pc id numWhales numCalves numSingers', Pod),
    _ndt('vt id type', Vessel),
    
    # scans
    _ndt('ssc scanId visibility beaufort swellHeight numVessels numPods', StartScan),
    _ndt('sws', StartWhaleScan),
    _ndt('esc', EndScan),
    
    # focal sessions
    _ndt(('sfs sessionId podId orientation speed visibility beaufort swellHeight '
          'numVessels aircraftDisturbance playbackType'), StartFocalSession),
    # TODO: Either create commands for StartPlayback and EndPlayback observations
    # or delete the observation types.
    _ndt('svs', StartVesselScan),
    _ndt('evs', EndVesselScan),
    _ndt('efs', EndFocalSession),
    
    _ndt('or orientation speed', Orientation),
    _ndt('env visibility beaufort swellHeight', Environment),
    _ndt('cnf confidence', Confidence),
    
    _ndt('bf objectType objectId reticle azimuth behavioralState', BinocularFix),
    
    # theodolite fixes
    _ndt('z', TheoData, {
             ('date', 'time'): _Interpreter._getAndSaveCurrentDateAndTime,
             ('declination', 'azimuth'): _Interpreter._getAndSaveTheodoliteAngles}),
    _ndt('fx objectType objectId behavioralState', Fix, dict(_fixDefaults)), 
    _fix('p', 'Pod'),
    _fix('v', 'Vessel'),
    _fix('sp', 'Spinner pod'),
    _fix('bn', 'Tursiops pod'),
    _fix('tu', 'Turtle pod'),
    _fix('r', 'Reference'),
    _fix('by', 'Buoy'),
    _fix('os', 'Other'),
    
    _ndt('st observerId objectType objectId behavioralState', Sighting),
    
    # individual behaviors
    
    # respiration
    _beh('fs', 'First surface with no blow'),
    _beh('f',  'First surface blow'),
    _beh('nf', 'Not first surfacing'),
    _beh('b',  'Blow'),
    _beh('n',  'No blow rise'),
    _beh('m',  'Missed blow(s)?'),

    # submergence
    _beh('s',  'Slip under'),
    _beh('a',  'Peduncle arch'),
    _beh('d',  'Fluke down dive'),
    _beh('u',  'Fluke up dive'),
    _beh('sq', 'Unidentified submergence'),

    # non-respiratory markers
    _beh('nr', 'Missed non-respiratory behavior(s)?'),
    _beh('ub', 'Unidentified behavior'),
    _beh('ms', 'Missed surfacing'),

    # subsurface exhalations
    _beh('bc', 'Bubble cloud'),
    _beh('bt', 'Linear bubble trail'),

    # whale vocalizations
    _beh('tb', 'Trumpet blow'),
    _beh('sr', 'Singing reported'),
    _beh('ss', 'Sideslap'),

    # head and leaping behaviors
    _beh('hr', 'Head rise'),
    _beh('hl', 'Head lunge'),
    _beh('mb', 'Motorboating'),
    _beh('hs', 'Head slap'),
    _beh('br', 'Breach'),
    _beh('us', 'Unidentified large splash'),
    _beh('oh', 'Other head behavior'),
    _beh('ap', 'Airplane'),
    _beh('h',  'Helicopter'),

    # tail behaviors
    _beh('te', 'Tail extension'),
    _beh('ts', 'Tail slap'),
    _beh('ls', 'Lateral tail slap'),
    _beh('sw', 'Tail swish'),
    _beh('lt', 'Lateral tail display'),
    _beh('ot', 'Other tail behavior'),
    
    # pectoral fin behaviors
    _beh('pe', 'Pec extension'),
    _beh('ps', 'Pec slap'),
    _beh('rp', 'Rolling pec slap'),
    _beh('op', 'Other pec behavior'),

    # body contact
    _beh('sb', 'Strike with body part'),
    _beh('wc', 'Whale body contact'),

    # pod behavioral states
    _bst('rest'),
    _bst('mill'),
    _bst('trav'),
    _bst('stat'),
    _bst('sact'),
    _bst('unkn'),
    _bst('whalewatch'),
    _bst('1', 'rest'),
    _bst('2', 'mill'),
    _bst('3', 'trav'),
    _bst('4', 'stat'),
    _bst('5', 'sact'),
    _bst('6', 'unkn'),
    _bst('7', 'whalewatch'),
    
    _ndt('sync', BehaviorsSynchronous),
    _ndt('asyn', BehaviorsAsynchronous),
    
    # pod events
    _pev('pd',   'Pod decreases speed'),
    _pev('pi',   'Pod increases speed'),
    _pev('px',   'Pod stops'),
    _pev('p45',  'Pod changes direction 45 to 90 degrees'),
    _pev('p90',  'Pod changes direction 90 to 180 degrees'),
    _pev('p180', 'Pod changes direction 180 degrees'),
    
    # vessel events
    _vev('vs', 'Vessel starts'),
    _vev('vc', 'Vessel changes speed'),
    _vev('vx', 'Vessel stops'),
    
    _ndt('paf oldPodId1 oldPodId2 newPodId', Affiliation),
    _ndt('pds oldPodId newPodId1 newPodId2', Disaffiliation),
    # TODO: Either create commands for the SuspectedAffiliation and SuspectedDisaffiliation
    # observations or delete the observation types.
    _ndt('pl', FocalPodLost),
    
    # document edits
    _ndt('l lag', Lag),
    _ndt('x', DeleteLastEntry),
    _ndt('xx', DeleteLastSequence),
    
    # theodolite
    _ndt('eh height', EyepieceHeight),
    _ndt('tbc', BubbleCheck),
    _ndt('rbt', Rebalance),
    
    _ndt('th height', TideHeight),
    
    # closest approaches
    _cpa('cpav', 'Vessel'),
    _cpa('cpaa', 'Airplane'),
    _cpa('cpah', 'Helicopter'),
    
    _ndt('sn surfacingNum', SurfacingNumber)
    
]
