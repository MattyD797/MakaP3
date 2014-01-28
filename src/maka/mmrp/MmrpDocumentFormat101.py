'''MMRP field and observation formats.'''


from maka.mmrp.MmrpDocument101 import MmrpDocument101
from maka.format.SimpleDocumentFormat import (
    AngleFormat, DateFormat, DecimalFormat, FloatFormat, IntegerFormat, SimpleDocumentFormat,
    StringFormat, TimeFormat)



def _createSep(affix):
    return ' ' if len(affix) > 0 else ''


def _createFormatKeyValuePair(prefix, name, suffix=''):
    prefixSep = _createSep(prefix)
    suffixSep = _createSep(suffix)
    return (name, prefix + prefixSep + name + '*' + suffixSep + suffix)


_ENVIRONMENT = 'Visibility {visibility} Beaufort {beaufort} Swell {swellHeight}'
_POD = 'Pod {podId}'
_DEC_AZ = 'Dec {declination} Az {azimuth}'
_OBJECT = '{objectType} {objectId}'
_BEHAVIORAL_STATE = 'State {behavioralState}'
_EVENT = '{code} {event}'


_observationFormats = dict([_createFormatKeyValuePair('', *f) for f in [
                                 
    # formats for observation types without observation number, date, and time                        
    ('Station',
         '{id} {name} '
         'Lat {latitudeDegrees} {latitudeMinutes} '
         'Lon {longitudeDegrees} {longitudeMinutes} '
         'El {elevation} MagDec {magneticDeclination}'),
    ('Observer', '{initials} {name}'),
    ('Theodolite', '{id} {name} AzOffset {azimuthOffset} DecOffset {declinationOffset}'),
    ('Reference', '{id} {name} Azimuth {azimuth}'),
    ('Pod', '{id} Whales {numWhales} Calves {numCalves} Singers {numSingers}')
    
]] + [_createFormatKeyValuePair('{observationNum:05d} {date} {time}', *f) for f in [
                     
    # formats for observation types with observation number, date, and time             
    ('Role', '{observer} {role}'),
    ('Start',),
    ('End',),
    ('Comment', '{id} {text}'),
    ('Vessel', '{id} Type {type}'),
    ('StartScan', '{scanId} ' + _ENVIRONMENT + ' Vessels {numVessels} Pods {numPods}'),
    ('StartWhaleScan',),
    ('EndScan',),
    ('StartVesselScan',),
    ('EndVesselScan',),
    ('StartFocalSession',
        '{sessionId} ' + _POD + ' '
        'Or {orientation} {speed} '
        'Env {visibility} {beaufort} {swellHeight} '
        'Dist {numVessels} {aircraftDisturbance} {playbackType}'),
    ('StartPlayback',),
    ('EndPlayback',),
    ('EndFocalSession',),
    ('Orientation', '{orientation} Speed {speed}'),
    ('Environment', _ENVIRONMENT),
    ('Confidence', '{confidence}'),
    ('BinocularFix', _OBJECT + ' Ret {reticle} Az {azimuth} ' + _BEHAVIORAL_STATE),
    ('TheoData', _DEC_AZ),
    ('Fix', _DEC_AZ + ' ' + _OBJECT + ' ' + _BEHAVIORAL_STATE),
    ('Sighting', 'Observer {observerId} ' + _OBJECT + ' ' + _BEHAVIORAL_STATE),   
    ('Behavior', '{code} {behavior} ' + _POD + ' {individualId}'),
    ('BehavioralState', '{state} ' + _POD),
    ('BehaviorsSynchronous',),
    ('BehaviorsAsynchronous', '{numSurfaceWhales}'),
    ('PodEvent', _EVENT + ' ' + _POD),
    ('VesselEvent', _EVENT + ' Vessel {vesselId}'),
    ('Affiliation', 'First {oldPodId1} Second {oldPodId2} New {newPodId}'),
    ('Disaffiliation', 'Old {oldPodId} First {newPodId1} Second {newPodId2}'),
    ('SuspectedAffiliation',),
    ('SuspectedDisaffiliation',),
    ('FocalPodLost',),
    ('Lag', '{lag}'),
    ('DeleteLastEntry',),
    ('DeleteLastSequence',),
    ('EyepieceHeight', '{height}'),
    ('BubbleCheck',),
    ('Rebalance',),
    ('TideHeight', '{height}'),
    ('ClosestApproach', _OBJECT + ' ' + _POD),
    ('SurfacingNumber', '{surfacingNum}')
    
]])


_fieldFormats = {
    'String': StringFormat,
    'Decimal': DecimalFormat,
    'Integer': IntegerFormat,
    'Float': FloatFormat,
    'Angle': AngleFormat,
    'Declination': AngleFormat,
    'Azimuth': AngleFormat,
    'Date': DateFormat,
    'Time': TimeFormat
}


class MmrpDocumentFormat101(SimpleDocumentFormat):
    extensionName = "'96 MMRP Grammar 1.01"
    documentClass = MmrpDocument101
    observationFormats = _observationFormats
    fieldFormats = _fieldFormats
    