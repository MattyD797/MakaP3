'''Maka application.'''


from PySide.QtGui import QApplication
import sys
    
from maka.ui.MainWindow import MainWindow
import maka.util.ExtensionManager as ExtensionManager


def _main():
    
    ExtensionManager.initialize()
    
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    window.openDocumentFile('/Users/Harold/Desktop/Maka/Test Document.txt')
    
    window.raise_()
    window.activateWindow()
    
    app.exec_()
    
    sys.exit()


if __name__ == '__main__':
    _main()
