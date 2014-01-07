'''Module containing Maka preferences.'''


# Copyright (C) 2013 Harold Mills. All rights reserved.


from __future__ import print_function
import json
        
            
def _loadPreferences():
    
    try:
        return json.loads('''
{
     "mainWindow.width": 600,
     "mainWindow.height": 500,
     "observationDialog.width": 400,
     "defaultDocumentFilePath": "/Users/Harold/Desktop/Maka/Test Document.txt"
}
''')
        
    except ValueError:
        print('Could not parse preferences file.')
        return {}


preferences = _loadPreferences()
