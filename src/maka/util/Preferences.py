'''Module containing Maka preferences.'''


from __future__ import print_function
import json

import maka.util.TextUtils as TextUtils
        
            
def _loadPreferences():
    
    try:
        return json.loads(TextUtils.removeComments('''
{
    "mainWindow.width": 600,
    "mainWindow.height": 500,
    "observationDialog.width": 400,
#    "defaultDocumentFilePath": "/Users/Harold/Desktop/Stuff/Maka/Test Document.txt",
#    "openFileDialog.dirPath": "/Users/Harold/Desktop/Stuff/Maka",
#    "saveAsFileDialog.dirPath": "/Users/Harold/Desktop/Stuff/Maka",
    "devices": {
        "Theodolite": {
#            "deviceType": "Dummy Theodolite"
            "deviceType": "Sokkia DT500 Theodolite",
            "deviceConfig": { "serialPortName": "/dev/cu.usbserial" }
        }
    }
}
'''))
        
    except ValueError:
        print('Could not parse preferences file.')
        return {}


preferences = _loadPreferences()
