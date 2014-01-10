from maka.util.Preferences import preferences as prefs
import maka.util.ExtensionManager as ExtensionManager


_DEVICES_PREFERENCE_NAME = 'devices'
_DEVICE_TYPE_KEY = 'deviceType'
_DEVICE_CONFIG_KEY = 'deviceConfig'


_deviceClasses = None
'''mapping from device types (i.e. extension names) to device classes (i.e. extensions).'''

_devices = {}
'''mapping from device names to device instances.'''


def getDevice(name):
    
    try:
        return _devices[name]
    
    except KeyError:
        # device not yet created
        
        return _createDevice(name)
    
    
def _createDevice(name):
    
    try:
        devices = prefs[_DEVICES_PREFERENCE_NAME]
    except KeyError:
        raise ValueError('No "{:s}" preference found.'.format(_DEVICES_PREFERENCE_NAME))
    
    try:
        deviceInfo = devices[name]
    except KeyError:
        raise ValueError(
            'Device "{:s}" not found in "{:s}" preference.'.format(name, _DEVICES_PREFERENCE_NAME))
        
    if not isinstance(deviceInfo, dict):
        raise ValueError(
            'Information provided for {:s} is not a JSON object.'.format(_deviceString(name)))

    try:
        deviceClassName = deviceInfo[_DEVICE_TYPE_KEY]
    except KeyError:
        raise ValueError(
            'Information provided for {:s} does not include "{:s}" name/value pair.').format(
                _deviceString(name), deviceClassName)
                
    try:         
        deviceClass = _getDeviceClass(deviceClassName)
    except KeyError:
        raise ValueError(
            'Unrecognized device type "{:s}" specified for {:s}.'.format(
                deviceClassName, _deviceString(name)))
        
    deviceConfig = deviceInfo.get(_DEVICE_CONFIG_KEY, {})
    
    device = deviceClass(**deviceConfig)
    
    _devices[name] = device
    
    return device
    
    
def _deviceString(deviceName):
    return 'device "{:s}" in preference "{:s}"'.format(deviceName, _DEVICES_PREFERENCE_NAME)


def _getDeviceClass(name):
    
    global _deviceClasses
    
    if _deviceClasses is None:
        _deviceClasses = dict(
            (c.extensionName, c) for c in ExtensionManager.getExtensions('Device'))
        
    return _deviceClasses[name]
