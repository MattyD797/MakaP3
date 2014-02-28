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
    return _createSerialNumGenerator(doc, _getCommentId, 1)

    
def _getCommentId(obs):
    if obs.__class__.__name__ == 'Comment':
        return obs.id
    else:
        return None
    
    
_Interpreter = MmrpCommandInterpreter101


class _CommandNameGenerator(object):
    
    def __init__(self):
        self._commandNum = -1
        
    def generateCommandName(self):
        self._commandNum += 1
        return '_Command{:03d}'.format(self._commandNum)
    
    
_commandNameGenerator = _CommandNameGenerator()


def _command(format, obsClass, bases=(SimpleCommand,), defaultFieldValues=None):
    
    name = _commandNameGenerator.generateCommandName()
    
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
    
    
def _binocularFix(commandName, objectType):
    format = commandName + ' objectId azimuth reticle behavioralState'
    defaultFieldValues = {'objectType': objectType}
    return _ndt(format, BinocularFix, defaultFieldValues)


_fixDefaults = [
    (('date', 'time'), _Interpreter._getSavedDateAndTime),
    (('declination', 'azimuth'), _Interpreter._getSavedTheodoliteAngles)
]


def _fix(commandName, objectType):
    format = commandName + ' objectId behavioralState'
    defaultFieldValues = dict(_fixDefaults + [('objectType', objectType)])
    return _ndt(format, Fix, defaultFieldValues)


def _behaviorFieldValuesHook(self, fieldValues):
    id = fieldValues['individualId']
    if id is not None:
        fieldValues['code'] += str(id)
    return fieldValues


def _behavior(code, behavior):
    format = code + ' individualId podId'
    defaultFieldValues = {'code': code, 'behavior': behavior}
    cls = _ndt(format, Behavior, defaultFieldValues)
    cls._fieldValuesHook = _behaviorFieldValuesHook
    return cls


def _behavioralState(name, state=None):
    format = name + ' podId'
    if state is None: state = name
    return _ndt(format, BehavioralState, {'state': state})


def _podEvent(code, event):
    return _objectEvent(code, event, 'pod', PodEvent)
    
    
def _objectEvent(code, event, objectName, obsClass):
    format = code + ' ' + objectName + 'Id'
    defaultFieldValues = {'code': code, 'event': event}
    return _ndt(format, obsClass, defaultFieldValues)


def _vesselEvent(code, event):
    return _objectEvent(code, event, 'vessel', VesselEvent)


def _closestApproach(name, objectType):
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
    
    # binocular fixes
    _ndt('bf objectType objectId azimuth reticle behavioralState', BinocularFix),
    _binocularFix('bp', 'Pod'),
    _binocularFix('bv', 'Vessel'),
    
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
    _behavior('fs', 'First surface with no blow'),
    _behavior('f',  'First surface blow'),
    _behavior('nf', 'Not first surfacing'),
    _behavior('b',  'Blow'),
    _behavior('n',  'No blow rise'),
    _behavior('m',  'Missed blow(s)?'),

    # submergence
    _behavior('s',  'Slip under'),
    _behavior('a',  'Peduncle arch'),
    _behavior('d',  'Fluke down dive'),
    _behavior('u',  'Fluke up dive'),
    _behavior('sq', 'Unidentified submergence'),

    # non-respiratory markers
    _behavior('nr', 'Missed non-respiratory behavior(s)?'),
    _behavior('ub', 'Unidentified behavior'),
    _behavior('ms', 'Missed surfacing'),

    # subsurface exhalations
    _behavior('bc', 'Bubble cloud'),
    _behavior('bt', 'Linear bubble trail'),

    # whale vocalizations
    _behavior('tb', 'Trumpet blow'),
    _behavior('sr', 'Singing reported'),
    _behavior('ss', 'Sideslap'),

    # head and leaping behaviors
    _behavior('hr', 'Head rise'),
    _behavior('hl', 'Head lunge'),
    _behavior('mb', 'Motorboating'),
    _behavior('hs', 'Head slap'),
    _behavior('br', 'Breach'),
    _behavior('us', 'Unidentified large splash'),
    _behavior('oh', 'Other head behavior'),
    _behavior('ap', 'Airplane'),
    _behavior('h',  'Helicopter'),

    # tail behaviors
    _behavior('te', 'Tail extension'),
    _behavior('ts', 'Tail slap'),
    _behavior('ls', 'Lateral tail slap'),
    _behavior('sw', 'Tail swish'),
    _behavior('lt', 'Lateral tail display'),
    _behavior('ot', 'Other tail behavior'),
    
    # pectoral fin behaviors
    _behavior('pe', 'Pec extension'),
    _behavior('ps', 'Pec slap'),
    _behavior('rp', 'Rolling pec slap'),
    _behavior('op', 'Other pec behavior'),

    # body contact
    _behavior('sb', 'Strike with body part'),
    _behavior('wc', 'Whale body contact'),

    # pod behavioral states
    _behavioralState('rest'),
    _behavioralState('mill'),
    _behavioralState('trav'),
    _behavioralState('stat'),
    _behavioralState('sact'),
    _behavioralState('unkn'),
    _behavioralState('whalewatch'),
    _behavioralState('1', 'rest'),
    _behavioralState('2', 'mill'),
    _behavioralState('3', 'trav'),
    _behavioralState('4', 'stat'),
    _behavioralState('5', 'sact'),
    _behavioralState('6', 'unkn'),
    _behavioralState('7', 'whalewatch'),
    
    _ndt('sync', BehaviorsSynchronous),
    _ndt('asyn', BehaviorsAsynchronous),
    
    # pod events
    _podEvent('pd',   'Pod decreases speed'),
    _podEvent('pi',   'Pod increases speed'),
    _podEvent('px',   'Pod stops'),
    _podEvent('p45',  'Pod changes direction 45 to 90 degrees'),
    _podEvent('p90',  'Pod changes direction 90 to 180 degrees'),
    _podEvent('p180', 'Pod changes direction 180 degrees'),
    
    # vessel events
    _vesselEvent('vs', 'Vessel starts'),
    _vesselEvent('vc', 'Vessel changes speed'),
    _vesselEvent('vx', 'Vessel stops'),
    
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
    _closestApproach('cpav', 'Vessel'),
    _closestApproach('cpaa', 'Airplane'),
    _closestApproach('cpah', 'Helicopter'),
    
    _ndt('sn surfacingNum', SurfacingNumber)
    
]
