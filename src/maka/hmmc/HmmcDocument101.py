'''HMMC Maka field and observation classes.'''


from __future__ import print_function

from maka.data.Field import Date, Decimal, Float, Integer, String, Time
from maka.data.Observation import Observation
    

'''
How to specify string formatting and parsing?

I like the idea of using format strings somewhat like those of Python 3:

'Fix': '{num:05d} {date} {time} Fix Dec {declination} Az {azimuth} {subject_type} {subject_id}'

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
        TextField('Subject Type', 'subjectType'),
        TextField('Subject ID', 'subjectId'))
    
    'Sighting': _ndtFields(
        TextField('Observer ID', 'observerId'),
        TextField('Subject Type', 'subjectType'),
        TextField('Subject ID', 'subjectId'),
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
        ["TextField", "subject_type", "Subject Type"],
        {"type": "TextField", "field": "subject_id", "label": "Subject ID"}
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


# TODO: Complete field and observation definitions to include everything in old grammar.
# TODO: Check units of all fields.


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
        
        
# TODO: What should reticle range be?
class Reticle(Decimal):
    UNITS = 'reticle number'
    MIN = '0'
        
      
'''  
observerTranslations = {
    'Adam': 'asf',
    'adam': 'asf',
    'Chris': 'cmg',
    'chris': 'cmg',
    'Yin': 'sey',
    'yin': 'sey',
    'Susan': 'shr',
    'susan': 'shr'
}


TObserver: Role.observer
TRole: Role.role
TObjectType: {BinocularFix, Fix, Sighting, ClosestApproach}.objectType
TIndividual: Behavior.individualId
TBehavioralState: {BinocularFix, Fix, Sighting}.behavioralState, BehavioralState.state
TBehavior: Behavior.behavior
'''


# TODO: Should values be restricted? Most in 2013 data are 'Pod', 'Vessel', 'Reference',
# or 'Buoy', but there are others like 'P' and 'z' as well.
class SubjectType(String):
    pass
        
        
class Id(Integer):
    MIN = 0
        
        
class Count(Integer):
    MIN = 0
        
        
class Visibility(Integer):
    MIN = 0
    MAX = 6
        
        
class Beaufort(Integer):
    MIN = 0
    MAX = 6
        
        
class SwellHeight(Decimal):
    UNITS = 'meters'
    MIN = '0'
        
        
# TODO: Restrict values?
class BehavioralState(String):
    pass
        
        
class Numbered(Observation):
    observationNum = Integer(doc='the number of this observation')
    
    
class TimeStamped(Observation):
    date = Date(doc = 'the date of this observation')
    time = Time(doc = 'the time of this observation')
   
    
class Ndt(Numbered, TimeStamped):
    pass


class Station(Observation):
    id = Id
    name = String
    latitudeDegrees = Integer(units='degrees north of equator', min=-90, max=90)
    latitudeMinutes = Decimal(units='minutes', min='0', max='60', maxInclusive=False)
    longitudeDegrees = Integer(units='degrees east', min=-180, max=180)
    longitudeMinutes = Decimal(units='minutes', min='0', max='60', maxInclusive=False)
    elevation = Decimal(units='meters above sea level')
    magneticDeclination = Angle(units='degrees clockwise from geographic north')
    
    
class Theodolite(Observation):
    id = Id
    name = String
    azimuthOffset = Angle(units='degrees')
    declinationOffset = Angle(units='degrees')
    
    
class Reference(Observation):
    id = Id
    name = String
    azimuth = Azimuth
    
    
class Observer(Observation):
    initials = String
    name = String
    
    
class Pod(Observation):
    id = Id
    numWhales = Count
    numCalves = Count
    numSingers = Count
    
    
# TODO: Why are vessel observations Ndts?
class Vessel(Ndt):
    id = Id
    type = String
    
    
class Start(Ndt):
    pass


class End(Ndt):
    pass


class Comment(Ndt):
    id = Id
    text = String
    
    
# TODO: Is eyepiece height in centimeters or inches?
class EyepieceHeight(Ndt):
    eyepieceHeight = Decimal(units='centimeters', min='0')
    
    
class BubbleCheck(Ndt):
    pass


class Rebalance(Ndt):
    pass


class Role(Ndt):
    observer = String
    role = String         # TODO: Restrict values?
    
    
class TheoData(Ndt):
    declination = Declination
    azimuth = Azimuth
    
    
class Fix(Ndt):
    
    declination = Declination(
        doc='the declination of this fix in degrees from the zenith, in the range [0, 180]')
              
    azimuth = Azimuth(
        doc='the azimuth of this fix in degrees clockwise from zero, in the range [0, 360)')
              
    subjectType = SubjectType(doc='the type of the subject of this fix')
        
    subjectId = Id(doc='the ID of the subject of this fix')
    
    subjectState = String(doc='the behavioral state of the subject of this fix')


# TODO: What are azimuth units here?
class BinocularFix(Ndt):
    subjectType = SubjectType
    subjectId = Id
    reticle = Reticle
    azimuth = Decimal(units='degrees clockwise from magnetic north', min='0', max='360', maxInclusive=False)
    behavioralState = BehavioralState
    
    
class StartScan(Ndt):
    id = Id
    visibility = Visibility
    beaufort = Beaufort
    swellHeight = SwellHeight
    numVessels = Count
    numPods = Count
    
    
class EndScan(Ndt):
    pass


class StartVesselScan(Ndt):
    pass


class EndVesselScan(Ndt):
    pass


class StartFocalSession(Ndt):
    sessionId = Id
    podId = Id
    orientation = Integer(min=0, max=359)
    speed = Integer(min=0, max=3)
    visibility = Visibility
    beaufort = Beaufort
    swellHeight = SwellHeight
    numVessels = Count
    aircraftDisturbance = Count
    playbackType = Integer(min=0, max=1)
    
    
class EndFocalSession(Ndt):
    pass


class StartPlayback(Ndt):
    pass


class EndPlayback(Ndt):
    pass


class Environment(Ndt):
    visibility = Visibility
    beaufort = Beaufort
    swellHeight = SwellHeight
    

# TODO: Restrict values of code, behavior, and individual_id.
class Behavior(Ndt):
    code = String
    behavior = String
    podId = Id
    individualId = String
    
    
# TODO: Restrict values of code and event?
class PodEvent(Ndt):
    code = String
    event = String
    podId = Id
    

class Lag(Ndt):
    lag = Decimal(default='3')


class DeleteLastEntry(Ndt):
    pass


class HmmcDocument101(object):
    
    
    extensionName = 'HMMC Document 1.01'
    
    observationClasses = frozenset([
        Station, Theodolite, Reference, Observer, Pod, Vessel, Start, End, Comment,
        EyepieceHeight, BubbleCheck, Rebalance, Role, TheoData, Fix, BinocularFix,
        StartScan, EndScan, StartVesselScan, EndVesselScan,
        StartFocalSession, EndFocalSession, StartPlayback, EndPlayback,
        Environment, Behavior, PodEvent, Lag, DeleteLastEntry])
    
    fieldClasses = frozenset([
        Azimuth, Count, Date, Declination, Decimal, Id, Integer, String, SubjectType, Time])
    
    
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
        
        "SubjectType": {
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
                "subject_type", {
                    "type": "SubjectType",
                    "doc": "the type of the subject of this fix"
                },
                "subject_id", {
                    "type": "SubjectID",
                    "doc": "the ID of the subject of this fix."
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
