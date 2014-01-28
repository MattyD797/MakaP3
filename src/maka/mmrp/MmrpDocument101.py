'''MMRP field and observation classes.'''


from __future__ import print_function

from maka.data.Field import Date, Decimal, Float, Integer, String, Time
from maka.data.Observation import Observation
    

'''
How to specify string formatting and parsing?

I like the idea of using format strings somewhat like those of Python 3:

'Fix': '{num:05d} {date} {time} Fix Dec {declination} Az {azimuth} {object_type} {object_id}'

How to arrange for formatting of dates, times, and angles?
Should theo declinations and azimuths be stored as floating point numbers, or as strings?

How to deal with GPS lat/lon data, e.g. for station location?

What about translations? Completions? Note that these are for interactive use in
commands and forms, and as such are orthogonal to formatting and parsing.

From what information do we create forms? Perhaps this is another place where a declarative
specification would be useful.

For formatting and parsing field values, for dealing with observations both as
text and with forms, associate default formatters and parsers with field types.
Allow specification of custom formatters and parsers, though.

Field value format should have optional format hint associated with it,
like 'mm/dd/yy' for a date format or 'hh:mm:ss' for a time format. When
available, these hints should be displayed in form text field labels,
e.g. 'Date (mm/dd/yy)' or 'Time (hh:mm:ss)'.

What about form tooltips?

class
numDateTimeFields = [
    TextField('Observation Number', 'num'),
    TextField('Date (mm/dd/yy)', 'date'),
    TextField('Time (hh:mm:ss)', 'time', TimeFormat)
]
    
def _ndtFields(*args):
    return numDateTimeFields + args
    
    
forms = {

    'Fix': _ndtFields(
        TextField('Declination (ddd:mm:ss)', 'declination'),
        TextField('Azimuth (ddd:mm:ss)', 'azimuth'),
        TextField('Object Type', 'objectType'),
        TextField('Object ID', 'objectId'))
    
    'Sighting': _ndtFields(
        TextField('Observer ID', 'observerId'),
        TextField('Object Type', 'objectType'),
        TextField('Object ID', 'objectId'),
        TextField('Behavioral State', 'behavioralState'))
        
}

"forms": {

    "NumDateTime": [
        ["TextField", "num", "Observation number"],
        ["TextField", "date", "Date (mm/dd/yy)"],
        ["TextField", "time", "Time (hh:mm:ss)"]
    ]
        
    "Fix": [
        "NumDateTime",
        ["TextField", "declination", "Declination (ddd:mm:ss)"],
        ["TextField", "azimuth", "Azimuth (ddd:mm:ss)"],
        ["TextField", "object_type", "Object Type"],
        {"type": "TextField", "field": "object_id", "label": "Object ID"}
'''


# TODO: Use metaclasses to simplify field class definitions?
#
# I'd like to be able to say something like:
#
#    class Azimuth(Float):
#        min = 0
#        max = 360
#        maxInclusive = False
#
# Note that the specified values must override those of the `Float` class.
#
# A custom metaclass might collect all class attributes (including those of
# superclasses, with appropriate overriding behavior) whose names do not start
# with an underscore into a dictionary called `DEFAULT_PARAMETER_VALUES`. These
# could be combined with initializer keyword arguments (values specified via keyword
# arguments would override default parameter values) to arrive at field parameters.


class Angle(Float):
    pass


# TODO: Max declination value should probably be 180, but some files have larger values. Why?
class Declination(Float):
    
    # TODO: Allow default field property values (like default, doc, min, max, ...) to be
    # specified with lower case names. Right now we can't do that since the names would
    # collide with the names of the corresponding Python properties. Perhaps something
    # like the following could work? Perhaps `FieldProperty` could be a descriptor, so
    # that the Python properties would not be necessary? Would overriding work?
    # After figuring this out, revisit observations and their fields. Might it be
    # possible to unify our treatment of observations and fields?
#    min = FieldProperty(0)
#    max = FieldProperty(360)
#    maxInclusive = FieldProperty(False)

    UNITS = 'degrees below zenith'
    MIN = 0
    MAX = 360
    MAX_INCLUSIVE = False
        
        
class Azimuth(Float):
    UNITS = 'degrees clockwise from magnetic north'
    MIN = 0
    MAX = 360
    MAX_INCLUSIVE = False
        
        
class Visibility(Integer):
    MIN = 0
    MAX = 6
        
        
class Beaufort(Integer):
    MIN = 0
    MAX = 6
        
        
class SwellHeight(Decimal):
    UNITS = 'meters'
    MIN = '0'
    
    
class Orientation_(Integer):
    UNITS = 'degrees clockwise from magnetic north'
    MIN = 0
    MAX = 359
    
    
class Speed(Integer):
    MIN = 0
    MAX = 3
        
        
'''  
TObserver: Role.observer
TRole: Role.role
TObjectType: {BinocularFix, Fix, Sighting, ClosestApproach}.objectType
TIndividual: Behavior.individualId
TBehavioralState: {BinocularFix, Fix, Sighting}.behavioralState, BehavioralState.state
TBehavior: Behavior.behavior
'''


class ObserverInitials(String):
    TRANSLATIONS = {
        'Adam': 'asf',
        'adam': 'asf',
        'Chris': 'cmg',
        'chris': 'cmg',
        'Yin': 'sey',
        'yin': 'sey',
        'Susan': 'shr',
        'susan': 'shr'
    }
    
    
class Role_(String):
    TRANSLATIONS = {
        'o': 'Observer',
        't': 'Theodolite operator',
        'c': 'Computer operator',
        'n': 'Notetaker',
        'm': 'Map reticle person'
    }
    
    
class ObjectType(String):
    TRANSLATIONS = {
        'p': 'Pod',
        'v': 'Vessel',
        's': 'Spinner pod',
        'b': 'Tursiops Pod',    # "Pod" was capitalized in Aardvark grammar
        't': 'Turtle Pod',      # "Pod" was capitalized in Aardvark grammar
        'r': 'Reference',
        'o': 'Other'
    }
    
    
class Individual(String):
    
    TRANSLATIONS = {
        
        '1': 'Adult',
        '2': 'Mom',
        '3': 'Calf',
        '4': 'Escort',
        
        'a': 'Adult',
        'm': 'Mom',
        'c': 'Calf',
        'e': 'Escort'
    
    }
    
    
class BehavioralState_(String):
    
    TRANSLATIONS = {
        
        '1': 'rest',
        '2': 'mill',
        '3': 'trav',
        '4': 'stat',
        '5': 'sact',
        '6': 'unkn',
        '7': 'wwatch',
        
        'r': 'rest',
        'm': 'mill',
        't': 'trav',
        's': 'stat',
        'a': 'sact',
        'u': 'unkn',
        'w': 'wwatch'
    
    }
    
    
class Behavior_(String):
    
    TRANSLATIONS = {
                    
        # respiration
        'fs': 'First surface with no blow',
        'f':  'First surface blow',
        'nf': 'Not first surfacing',
        'b':  'Blow',
        'n':  'No blow rise',
        'm':  'Missed blow(s)?',
        
        # submergence
        's':  'Slip under',
        'a':  'Peduncle arch',
        'd':  'Fluke down dive',
        'u':  'Fluke up dive',
        'sq': 'Unidentified submergence',
        
        # non-respiratory markers
        'nr': 'Missed non-respiratory behavior(s)?',
        'ub': 'Unidentified behavior',
        'ms': 'Missed surfacing',
    
        # subsurface exhalations    
        'nr': 'Bubble cloud',
        'bt': 'Linear bubble trail',
        
        # whale vocalizations
        'tb': 'Trumpet blow',
        'sr': 'Singing reported',
        'ss': 'Sideslap',
        
        # head and leaping behaviors
        'hr': 'Head rise',
        'hl': 'Head lunge',
        'mb': 'Motor boating',
        'hs': 'Head slap',
        'br': 'Breach',
        'us': 'Unidentified large splash',
        'oh': 'Other head Behavior',    # "Behavior" was capitalized in Aardvark grammar
        'ap': 'Airplane',
        'h':  'Helicopter',
        
        # tail behaviors
        'te': 'Tail extension',
        'ts': 'Tail slap',
        'ls': 'Lateral tail slap',
        'sw': 'Tail swish',
        'lt': 'Lateral tail display',
        'ot': 'Other tail behavior',
        
        # pectoral fin behaviors
        'pe': 'Pec extension',
        'ps': 'Pec slap',
        'rp': 'Rolling pec slap',
        'op': 'Other pec behavior',
        
        # body contact
        'sb': 'Strike with body part',
        'wc': 'Whale body contact'
        
    }
        
        
class Station(Observation):
    id = Integer
    name = String
    latitudeDegrees = Integer(units='degrees north of equator', min=-90, max=90)
    latitudeMinutes = Decimal(units='minutes', min='0', max='60', maxInclusive=False)
    longitudeDegrees = Integer(units='degrees east', min=-180, max=180)
    longitudeMinutes = Decimal(units='minutes', min='0', max='60', maxInclusive=False)
    elevation = Decimal(units='meters above sea level')
    magneticDeclination = Angle(units='degrees clockwise from geographic north')
    
    
class Observer(Observation):
    initials = ObserverInitials
    name = String
    
    
class Theodolite(Observation):
    id = Integer
    name = String
    azimuthOffset = Angle(units='degrees')
    declinationOffset = Angle(units='degrees')
    
    
class Reference(Observation):
    id = Integer
    name = String
    azimuth = Azimuth(units='degrees clockwise from magnetic north')
    
    
class _Numbered(Observation):
    observationNum = Integer(doc='the number of this observation')
    
    
class _TimeStamped(Observation):
    date = Date(doc='the date of this observation')
    time = Time(doc='the time of this observation')
   
    
class _Ndt(_Numbered, _TimeStamped):
    pass


class Role(_Ndt):
    observer = ObserverInitials
    role = Role_
    
    
class Start(_Ndt):
    pass


class End(_Ndt):
    pass


class Comment(_Ndt):
    id = Integer
    text = String
    
    
class Pod(Observation):
    id = Integer
    numWhales = Integer
    numCalves = Integer
    numSingers = Integer
    
    
class Vessel(_Ndt):
    id = Integer
    type = Integer
    
    
class Environment(_Ndt):
    visibility = Visibility
    beaufort = Beaufort
    swellHeight = SwellHeight


class StartScan(Environment):
    scanId = Integer
    numVessels = Integer
    numPods = Integer
    
    
class StartWhaleScan(_Ndt):
    pass


class EndScan(_Ndt):
    pass


class StartVesselScan(_Ndt):
    pass


class EndVesselScan(_Ndt):
    pass


class Orientation(_Ndt):
    orientation = Orientation_
    speed = Speed
    
    
class StartFocalSession(Environment, Orientation):
    sessionId = Integer
    podId = Integer
    numVessels = Integer(units='number of vessels in arena')
    aircraftDisturbance = Integer(units='number of CPAs')
    playbackType = Integer(min=0, max=1)
    
    
class StartPlayback(_Ndt):
    pass

   
class EndPlayback(_Ndt):
    pass

   
class EndFocalSession(_Ndt):
    pass

   
class Confidence(_Ndt):
    confidence = Integer(min=1, max=6)
    
    
class BinocularFix(_Ndt):
    objectType = ObjectType
    objectId = Integer
    reticle = Decimal
    azimuth = Decimal(units='degrees clockwise from magnetic north', min='0', max='360', maxInclusive=False)
    behavioralState = BehavioralState_
    
    
class TheoData(_Ndt):
    declination = Declination
    azimuth = Azimuth
    
    
class Fix(_Ndt):
    declination = Declination    
    azimuth = Azimuth
    objectType = ObjectType
    objectId = Integer
    behavioralState = BehavioralState_


class Sighting(_Ndt):
    observerId = String
    objectType = ObjectType
    objectId = Integer
    behavioralState = BehavioralState_
    
    
class Behavior(_Ndt):
    code = String
    behavior = Behavior_
    podId = Integer
    individualId = Individual
    
    
class BehavioralState(_Ndt):
    state = BehavioralState_
    podId = Integer
    
    
class BehaviorsSynchronous(_Ndt):
    pass


class BehaviorsAsynchronous(_Ndt):
    numSurfaceWhales = Integer
    
    
class PodEvent(_Ndt):
    code = String
    event = String
    podId = Integer
    
    
class VesselEvent(_Ndt):
    code = String
    event = String
    vesselId = Integer
    
    
class Affiliation(_Ndt):
    oldPodId1 = Integer
    oldPodId2 = Integer
    newPodId = Integer
    
    
class Disaffiliation(_Ndt):
    oldPodId = Integer
    newPodId1 = Integer
    newPodId2 = Integer
    
    
class SuspectedAffiliation(_Ndt):
    pass


class SuspectedDisaffiliation(_Ndt):
    pass


class FocalPodLost(_Ndt):
    pass


class Lag(_Ndt):
    lag = Decimal(units='seconds', default='3')
    
    
class DeleteLastEntry(_Ndt):
    pass


class DeleteLastSequence(_Ndt):
    pass


class EyepieceHeight(_Ndt):
    height = Decimal(units='inches', min='0')
    
    
class BubbleCheck(_Ndt):
    pass


class Rebalance(_Ndt):
    pass


class TideHeight(_Ndt):
    height = Decimal(units='meters')
    
    
class ClosestApproach(_Ndt):
    objectType = ObjectType
    objectId = Integer
    podId = Integer
    
    
class SurfacingNumber(_Ndt):
    surfacingNum = Integer
    
    
class MmrpDocument101(object):
    
    
    extensionName = 'MMRP Document 1.01'
    
    observationClasses = frozenset([
        Station, Theodolite, Reference, Observer, Pod, Vessel, Start, End, Comment,
        EyepieceHeight, BubbleCheck, Rebalance, Role, TheoData, Fix, BinocularFix,
        StartScan, StartWhaleScan, EndScan, StartVesselScan, EndVesselScan,
        StartFocalSession, EndFocalSession, StartPlayback, EndPlayback,
        Orientation, Environment, Behavior, PodEvent, Lag, DeleteLastEntry])
    
    observationClasses = frozenset([
        Station, Observer, Theodolite, Reference, Role, Start, End, Comment, Pod, Vessel,
        Environment, StartScan, StartWhaleScan, EndScan, StartVesselScan, EndVesselScan,
        Orientation, StartFocalSession, StartPlayback, EndPlayback, EndFocalSession, Confidence,
        BinocularFix, TheoData, Fix, Sighting, Behavior, BehavioralState, BehaviorsSynchronous,
        BehaviorsAsynchronous, PodEvent, VesselEvent, Affiliation, Disaffiliation,
        SuspectedAffiliation, SuspectedDisaffiliation, FocalPodLost, Lag, DeleteLastEntry,
        DeleteLastSequence, EyepieceHeight, BubbleCheck, Rebalance, TideHeight, ClosestApproach,
        SurfacingNumber])
    
    fieldClasses = frozenset([
        Azimuth, Date, Declination, Decimal, Integer, String, ObjectType, Time])
    
    
    def __init__(self, observations=None, filePath=None, fileFormat=None):
        
        self.observations = [] if observations is None else observations
        self.filePath = filePath
        self.fileFormat = fileFormat

'''
Note that we could support the specification of field and observation types using JSON,
which is programming language independent. Such a specification might look something like
the following:

{

    "field types": {
    
        "Azimuth": {
            "super": "Float",
            "min": 0,
            "max": 360,
            "max inclusive": false
        },
        
        "Declination": {
            "super": "Float",
            "min": 0,
            "max": 180
        }
        
        "ObjectType": {
            "super": "String",
            "values": ["Pod", "Vessel"]
        }
        
    }
    
    "observation types": {
    
        "Numbered": {
            "super": "Observation",
            "fields": [
                "num", {
                    "type": "Integer",
                    "doc": "the number of this observation"
                }
            ]
        }
        
        "TimeStamped": {
            "super": "Observation",
            "fields": [
                "date_time", {
                    "type": "DateTime",
                    "doc": "the date and time of this observation"
                }
            ]
        }
        
        "Fix": {
            "supers": ["Numbered", "TimeStamped"]
            "fields": [
                "declination", {
                    "type": "Declination",
                    "doc": "the declination of this fix, in the range [0, 180] of degrees from the zenith"
                },
                "azimuth", {
                    "type": "Azimuth",
                    "doc": "the azimuth of this fix, in the range [0, 360) of degrees clockwise"
                },
                "object_type", {
                    "type": "ObjectType",
                    "doc": "the type of the object of this fix"
                },
                "object_id", {
                    "type": "ObjectID",
                    "doc": "the ID of the object of this fix."
                }
            ]
        }
        
    }
            
}

This will be important if Maka field and observation types are to be implemented
for programming languages other than Python. However, it is not very important to
support JSON field and observation type specifications in the initial Python Maka
implementation. It should follow the initial Python implementation soon, though.

I *do* think it's important to support export of observations (as opposed to observation
types) as JSON, since that will make it easy for users and third parties to process
observations using non-Python software.
'''
