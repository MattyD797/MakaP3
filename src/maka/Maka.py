'''Maka application.'''


from PySide.QtGui import QApplication
import os
import sys
    
from maka.ui.MainWindow import MainWindow
from maka.util.Preferences import preferences as prefs
import maka.util.ExtensionManager as ExtensionManager


def _main():
    
    ExtensionManager.initialize()
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    _openDefaultDocument(window)
    
    window.raise_()
    window.activateWindow()
    
    app.exec_()
    
    sys.exit()


def _openDefaultDocument(window):
    path = prefs.get('defaultDocumentFilePath')
    if path is not None and os.path.exists(path):
        window.openDocumentFile(path)
    
    
if __name__ == '__main__':
    _main()
