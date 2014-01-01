'''HMMC Maka field and observation formats.'''


from maka.format.SimpleDocumentFormat import (
    AngleFormat, DateFormat, DecimalFormat, FloatFormat, IntegerFormat, SimpleDocumentFormat,
    StringFormat, TimeFormat)
from maka.hmmc.HmmcDocument101 import HmmcDocument101


def _ndt(s):
    return '{observationNum:05d} {date} {time} ' + s


_observationFormats = {

    'Station': ('Station* {id} {name} '
                'Lat {latitudeDegrees} {latitudeMinutes} '
                'Lon {longitudeDegrees} {longitudeMinutes} '
                'El {elevation} MagDec {magneticDeclination}'),
    'Theodolite': ('Theodolite* {id} {name} '
                   'AzOffset {azimuthOffset} DecOffset {declinationOffset}'),
    'Reference': 'Reference* {id} {name} Azimuth {azimuth}',
    'Observer': 'Observer* {initials} {name}',
    'Pod': 'Pod* {id} Whales {numWhales} Calves {numCalves} Singers {numSingers}',
    
    'Vessel': _ndt('Vessel* {id} Type {type}'),
    
    'Start': _ndt('Start*'),
    'End': _ndt('End*'),
    'Comment': _ndt('Comment* {id} {text}'),
    'EyepieceHeight': _ndt('EyepieceHeight* {eyepieceHeight}'),
    'BubbleCheck': _ndt('BubbleCheck*'),
    'Rebalance': _ndt('Rebalance*'),
    'Role': _ndt('Role* {observer} {role}'),
    'TheoData': _ndt('TheoData* Dec {declination} Az {azimuth}'),
    'Fix': _ndt('Fix* Dec {declination} Az {azimuth} {subjectType} {subjectId} '
                'State {subjectState}'),
    'BinocularFix': _ndt(
        'BinocularFix* {subjectType} {subjectId} Ret {reticle} Az {azimuth} State '
        '{behavioralState}'),
    'StartScan': _ndt('StartScan* {id} Visibility {visibility} Beaufort {beaufort} '
                      'Swell {swellHeight} Vessels {numVessels} Pods {numPods}'),
    'EndScan': _ndt('EndScan*'),
    'StartVesselScan': _ndt('StartVesselScan*'),
    'EndVesselScan': _ndt('EndVesselScan*'),
    'StartFocalSession': _ndt(
        'StartFocalSession* {sessionId} Pod {podId} Or {orientation} {speed} '
        'Env {visibility} {beaufort} {swellHeight} '
        'Dist {numVessels} {aircraftDisturbance} {playbackType}'),
    'EndFocalSession': _ndt('EndFocalSession*'),
    'StartPlayback': _ndt('StartPlayback*'),
    'EndPlayback': _ndt('EndPlayback*'),   
    'Environment': _ndt(
        'Environment* Visibility {visibility} Beaufort {beaufort} Swell {swellHeight}'),
    'Behavior': _ndt('Behavior* {code} {behavior} Pod {podId} {individualId}'),
    'PodEvent': _ndt('PodEvent* {code} {event} Pod {podId}'),
    'Lag': _ndt('Lag* {lag}'),
    'DeleteLastEntry': _ndt('DeleteLastEntry*'),

}


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


class HmmcDocumentFormat101(SimpleDocumentFormat):
    extensionName = 'HMMC Document Format 1.01'
    documentClass = HmmcDocument101
    observationFormats = _observationFormats
    fieldFormats = _fieldFormats


class MmrpDocumentFormat101(HmmcDocumentFormat101):
    extensionName = "'96 MMRP Grammar 1.01"
    