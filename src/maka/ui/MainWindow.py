'''Module containing `MainWindow` class.'''


from __future__ import print_function

import os.path

from PySide.QtCore import SIGNAL
from PySide.QtGui import (
    QAbstractItemView, QAction, QApplication, QDialog, QFileDialog, QHBoxLayout,
    QItemSelection, QItemSelectionModel, QLabel, QLineEdit, QListWidget, QMainWindow,
    QMenuBar, QMessageBox, QVBoxLayout, QWidget)

from maka.command.CommandInterpreterError import CommandInterpreterError
from maka.data.Document import Document
from maka.ui.ObservationDialog import ObservationDialog
from maka.util.Preferences import preferences as prefs
import maka.format.DocumentFileFormat as DocumentFileFormat
import maka.util.ExtensionManager as ExtensionManager
 
 
'''
RESUME

* Open and save as dialog paths: preference for default, remember last.
* Auto-save
* Reminders
* Reduction
* Find/Replace
* Multiple documents.
'''


# TODO: Construct the whole menu bar from a schema?


_FILE_MENU_SCHEMA = '''
    New
    Open
    
    Save
    Save As
'''


_EDIT_MENU_SCHEMA = '''
    Undo
    Redo
    
    Cut
    Copy
    Paste
    Paste After
    Paste Before
    
    Delete
    Select All
    Deselect All
'''


class MainWindow(QMainWindow):
    
    
    def __init__(self):
        
        super(MainWindow, self).__init__()
        
        self._createUi()
        
        self.statusBar()
        
        width = prefs.get('mainWindow.width', 600)
        height = prefs.get('mainWindow.height', 500)
        self.resize(width, height)
        
        self._setDocument(_createNewDocument())
        
        
    def _createUi(self):
        
        self._createActions()
        self._createMenus()
        
        commandLine = self._createCommandLine()
        obsList = self._createObsList()
        
        box = QVBoxLayout()
        box.addWidget(commandLine)
        box.addWidget(obsList)
        
        widget = QWidget()
        widget.setLayout(box)
        
        self.setCentralWidget(widget)


    def _createActions(self):
        
        actions = (
                   
            ('New', self._onNew, 'Ctrl+N', 'New document'),
            ('Open...', self._onOpen, 'Ctrl+O', 'Open file'),
            
            ('Save', self._onSave, 'Ctrl+S', 'Save document to file'),
            ('Save As...', self._onSaveAs, None, 'Save document to new file'),
            
            ('Undo', self._onUndo, 'Ctrl+Z', 'Undo'),
            ('Redo', self._onRedo, 'Shift+Ctrl+Z', 'Redo'),
            
            ('Cut', self._onCut, 'Ctrl+X', 'Cut selected observations'),
            ('Copy', self._onCopy, 'Ctrl+C', 'Copy selected observations'),
            ('Paste', self._onPaste, 'Ctrl+V', 'Paste observations over selection'),
            ('Paste After', self._onPasteAfter, 'Shift+Ctrl+V', 'Paste observations after selection'),
            ('Paste Before', self._onPasteBefore, 'Alt+Ctrl+V', 'Paste observations before selection'),
            ('Delete', self._onDelete, 'Backspace', 'Delete selected observations'),
            
            ('Select All', self._onSelectAll, 'Ctrl+A', 'Select all observations'),
            ('Deselect All', self._onDeselectAll, 'Shift+Ctrl+A', 'Deselect all observations')
            
        )
        
        self._actions = {}
        for action in actions:
            self._createAction(*action)
        
        
    def _createAction(self, name, slot, shortcut=None, statusTip=None):
        
        action = QAction(name, self)
        action.triggered.connect(slot)
        
        if shortcut is not None:
            action.setShortcut(shortcut)
            
        if statusTip is not None:
            action.setStatusTip(statusTip)
            
        key = _stripEllipsis(name)
        self._actions[key] = action
        
        return action
    
            
    def _createMenus(self):
        
        # We assume here that we are on Mac OS X, and create a menu bar with no parent
        # so it will be shared by all application windows. I do not yet know what this
        # will do on Windows.
        menuBar = QMenuBar()
        
        self._createMenu(menuBar, '&File', _FILE_MENU_SCHEMA)
        self._createMenu(menuBar, '&Edit', _EDIT_MENU_SCHEMA)
        
        self.setMenuBar(menuBar)
         
        
    def _createMenu(self, menuBar, menuName, schema):
        
        menu = menuBar.addMenu(menuName)
        
        for actionName in _parseMenuSchema(schema):
            
            if actionName == '':
                menu.addSeparator()
                
            else:
                menu.addAction(self._actions[actionName])
                
        
    def _createCommandLine(self):
        
        self._commandLine = QLineEdit()
        self._commandLine.returnPressed.connect(self._onCommandLineReturnPressed)
        
        box = QHBoxLayout()
        box.addWidget(QLabel('Command:'))
        box.addWidget(self._commandLine)
        
        widget = QWidget()
        widget.setLayout(box)
        
        return widget
        
        
    # TODO: When observation list has keyboard focus and the user pressed a non-control
    # key, shift focus to command line and deliver key press event to it.
    
    
    def _onCommandLineReturnPressed(self):
        
        command = self._commandLine.text()
        
        try:
            obs = self._commandInterpreter.interpretCommand(command)
            
        except CommandInterpreterError as e:
            QMessageBox.critical(self, '', str(e))
        
        else:
            
            editName = 'Append ' + obs.__class__.__name__
            index = self._obsList.count()
            self.document.edit(editName, index, index, [obs])
            
            self._commandLine.clear()
            self._obsList.scrollToItem(self._obsList.item(index))
        
        
    def _createObsList(self):
        
        obsList = ObservationListWidget(self)
        obsList.setAlternatingRowColors(True)
        obsList.setSelectionMode(QAbstractItemView.ContiguousSelection)
        
        signal = SIGNAL('itemDoubleClicked(QListWidgetItem *)')
        self.connect(obsList, signal, self._onItemDoubleClick)
    
        self._obsList = obsList
        
        return obsList
    
    
    def _onItemDoubleClick(self, item):
        
        document = self.document
        index = self._obsList.indexFromItem(item).row()
        obs = document.observations[index]
        dialog = ObservationDialog(self, obs, document.documentFormat)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            
            changes = dialog.getChanges()
            
            if len(changes) != 0:
                
                # TODO: Is this the best way to get the name of an observation type?
                editName = 'Edit ' + obs.__class__.__name__
                
                document.edit(editName, index, index + 1, [obs.copy(**changes)])
                
                # TODO: Review handling of selections with undo/redo.
                # Note that currently if one edits an observation and then undoes
                # and redoes the edit the observation winds up unselected, which
                # may not be what we want.
                self._selectObservations(index, index + 1)
        
        
    @property
    def document(self):
        return self._document
    
    
    def _setDocument(self, doc):
        
        if hasattr(self, '_document'):
            self._document.removeEditListener(self._onDocumentEdit)
        self._document = doc
        self._document.addEditListener(self._onDocumentEdit)
        
        self._obsList.clear()
        self._insertObservations(0, len(self._document.observations))
        
        self._commandInterpreter = _getCommandInterpreter(self._document)
        
        self._updateUi()
        
                
    def _onDocumentEdit(self, edit):
        self._deleteObservations(edit.startIndex, edit.endIndex)
        self._insertObservations(edit.startIndex, len(edit.newObservations))
        self._updateUi()
        
        
    def _deleteObservations(self, startIndex, endIndex):
        for _ in xrange(endIndex - startIndex):
            self._obsList.takeItem(startIndex)
            
        
    def _insertObservations(self, startIndex, numObservations):
        doc = self.document
        format = doc.documentFormat
        obses = doc.observations
        endIndex = startIndex + numObservations
        labels = [format.formatObservation(obses[i]) for i in xrange(startIndex, endIndex)]
        self._obsList.insertItems(startIndex, labels)
            

    def _updateUi(self):
        self._updateWindowTitle()
        self._updateMenuItemStates()

        
    def _updateWindowTitle(self):
        
        doc = self.document
        
        if doc is None:
            suffix = ''
            
        else:
            name = 'Untitled' if doc.filePath is None else os.path.basename(doc.filePath)
            modified = '' if doc.saved else '*'
            suffix = ': ' + name + modified
        
        self.setWindowTitle('Maka' + suffix)
            
        
    def _updateMenuItemStates(self):
        
        actions = self._actions
        doc = self.document
        
        save = actions['Save']
        save.setEnabled(doc.filePath is None or not doc.saved)
        
        if not self._obsList.hasFocus():
            
            undo = actions['Undo']
            undo.setText('Undo')
            undo.setEnabled(False)
            
            redo = actions['Redo']
            redo.setText('Redo')
            redo.setEnabled(False)
            
            for name in ('Cut', 'Copy', 'Paste', 'Paste Before', 'Paste After', 'Delete',
                         'Select All', 'Deselect All'):
                
                actions[name].setEnabled(False)
            
        else:
            # observation list has focus
            
            name = doc.undoName
            text = 'Undo' if name is None else 'Undo ' + name
            undo = actions['Undo']
            undo.setText(text)
            undo.setStatusTip(text)
            undo.setEnabled(name is not None)
            
            name = doc.redoName
            text = 'Redo' if name is None else 'Redo ' + name
            redo = actions['Redo']
            redo.setText(text)
            redo.setStatusTip(text)
            redo.setEnabled(name is not None)
                
            items = self._obsList.selectedItems()
            itemsSelected = len(items) != 0
            for name in ('Cut', 'Copy', 'Paste', 'Paste Before', 'Paste After', 'Delete'):
                actions[name].setEnabled(itemsSelected)
                
            actions['Select All'].setEnabled(True)
            actions['Deselect All'].setEnabled(True)
            
        
    def _onNew(self):
        if self._isCloseOk():
            self._setDocument(_createNewDocument())
        
        
    def _onOpen(self):
        
        if self._isCloseOk():
            
            filePath, _ = \
                QFileDialog.getOpenFileName(self, 'Open File', '/Users/Harold/Desktop/Maka')
                
            if filePath != '':
                self.openDocumentFile(filePath)
            
            
    def openDocumentFile(self, filePath):
        
        try:
            # TODO: Improve error messages, e.g. to include line numbers.
            doc = DocumentFileFormat.readDocument(filePath)
            
        except Exception, e:
            message = 'File open failed.\n\n' + str(e)
            QMessageBox.critical(self, '', message)
            
        else:
            self._setDocument(doc)

    
    def _onSave(self):
            
        doc = self.document
        
        if doc.filePath is None:
            return self._onSaveAs()
            
        else:
            return self._writeDocumentFile(doc.filePath)
            
            
    def _writeDocumentFile(self, filePath):
        
        doc = self.document
        
        try:
            doc.fileFormat.writeDocument(doc, filePath, doc.documentFormat)
            
        except Exception, e:
            message = 'File save failed.\n\n' + str(e)
            QMessageBox.critical(self, '', message)
            return False
            
        else:
            doc.filePath = filePath
            doc.markSaved()
            self._updateUi()
            return True
        
        
    def _onSaveAs(self):
        
        if self.document.filePath is not None:
            dirPath = os.path.dirname(self.document.filePath)
        else:
            dirPath = ''
            
        filePath, _ = QFileDialog.getSaveFileName(self, 'Save Document', dirPath)
            
        if filePath == '':
            return False
        else:
            return self._writeDocumentFile(filePath)
        
        
    def _onUndo(self):
        edit = self.document.undo()
        n = len(edit.newObservations)
        if n > 0:
            i = edit.startIndex
            self._selectObservations(i, i + n)
            self._obsList.scrollToItem(self._obsList.item(i))
        
        
    def _selectObservations(self, startIndex, endIndex):
        startIndex = self._getModelIndex(startIndex)
        endIndex = self._getModelIndex(endIndex - 1)
        selection = QItemSelection(startIndex, endIndex)
        flags = QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows
        self._obsList.selectionModel().select(selection, flags)
        
        
    def _getModelIndex(self, i):
        selectionModel = self._obsList.selectionModel()
        itemModel = selectionModel.model()
        return itemModel.createIndex(i, 0)
        
        
    def _onRedo(self):
        self.document.redo()
        
        
    def _onCut(self):
        self._copySelectionToClipboard()
        self._deleteSelection('Cut')
        
        
    def _copySelectionToClipboard(self):
        text = self._obsList.selectedText
        QApplication.clipboard().setText(text)
        
        
    def _deleteSelection(self, editName):
        (startIndex, endIndex) = self._obsList.selectedRange;
        self.document.edit(editName, startIndex, endIndex, [])
        
        
    def _onCopy(self):
        self._copySelectionToClipboard()
        
        
    def _onPaste(self):
        observations = self._getClipboardObservations()
        if observations is not None:
            (startIndex, endIndex) = self._obsList.selectedRange;
            self.document.edit('Paste', startIndex, endIndex, observations)
        
        
    def _getClipboardObservations(self):
        
        text = QApplication.clipboard().text()
        
        docFormat = self.document.documentFormat
        
        if docFormat is None:
            self._handleEditError(
                'Paste', 'Document has no format with which to parse clipboard text.')
            return None
        
        try:
            lines = text.strip().splitlines()
            return docFormat.parseDocument(lines)
        except ValueError, e:
            self._handleEditError(
                'Paste',
                'Attempt to parse clipboard text yielded the following error message:\n\n' + str(e))
            return None
        
        
    def _handleEditError(self, editName, message):
        message = '{:s} operation failed.\n\n{:s}'.format(editName, message)
        QMessageBox.critical(self, '', message)
        
        
    def _onPasteAfter(self):
        observations = self._getClipboardObservations()
        if observations is not None:
            (_, endIndex) = self._obsList.selectedRange;
            self.document.edit('Paste After', endIndex, endIndex, observations)
        
        
    def _onPasteBefore(self):
        observations = self._getClipboardObservations()
        if observations is not None:
            (startIndex, _) = self._obsList.selectedRange;
            self.document.edit('Paste Before', startIndex, startIndex, observations)
        
        
    def _onDelete(self):
        self._deleteSelection('Delete')
        
        
    def _onSelectAll(self):
        self._obsList.selectAll()
        
        
    def _onDeselectAll(self):
        self._obsList.clearSelection()
        
        
    def closeEvent(self, event):
        if not self._isCloseOk():
            event.ignore()
            
            
    def _isCloseOk(self):
        
        doc = self.document
        
        if doc.saved:
            return True
        
        else:
            # current document has unsaved changes
            
            if doc.filePath is None:
                prefix = 'This document'
            else:
                fileName = os.path.basename(doc.filePath)
                prefix = 'The document "{:s}"'.format(fileName)
                
            box = QMessageBox()
            box.setText(prefix + ' has unsaved changes.')
            box.setInformativeText('Would you like to save them before closing?')
            box.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            box.setDefaultButton(QMessageBox.Save)
            
            result = box.exec_()
            
            if result == QMessageBox.Save:
                return self._onSave()
            
            elif result == QMessageBox.Cancel:
                return False
            
            else:
                return True

        
def _stripEllipsis(s):
    return s if not s.endswith('...') else s[:-3]
    
     
def _parseMenuSchema(s):
    return [i.strip() for i in s.strip().split('\n')]

    
def _createNewDocument():
    docFormat = _getDefaultDocumentFormat()
    docFileFormat = _getDefaultDocumentFileFormat()
    return Document(documentFormat=docFormat, fileFormat=docFileFormat)
    

# TODO: Don't hard code default document format name.
def _getDefaultDocumentFormat():
    return ExtensionManager.getExtension('DocumentFormat', "'96 MMRP Grammar 1.01")()


# TODO: Don't hard code default document file format name.
def _getDefaultDocumentFileFormat():
    return ExtensionManager.getExtension('DocumentFileFormat', 'Maka Document File Format')()


def _getCommandInterpreter(doc):
    docFormatName = doc.documentFormat.extensionName
    for interpreterClass in ExtensionManager.getExtensions('CommandInterpreter'):
        if docFormatName in interpreterClass.documentFormatNames:
            return interpreterClass(doc)
    raise ValueError(
        'Command interpreter not found for document format "{:s}".'.format(docFormatName))


class ObservationListWidget(QListWidget):
    

    def __init__(self, mainWindow, *args, **kwds):
        super(ObservationListWidget, self).__init__(*args, **kwds)
        self._mainWindow = mainWindow
        
        
    def selectionChanged(self, selected, deselected):
        super(ObservationListWidget, self).selectionChanged(selected, deselected)
        self._mainWindow._updateMenuItemStates()
        
        
    @property
    def selectedRange(self):
        
        if self.count() == 0:
            return None
        
        else:
            indices = [self.indexFromItem(i).row() for i in self.selectedItems()]
            return (min(indices), max(indices) + 1)
        
        
    @property
    def selectedText(self):
        items = self.selectedItems()
        items.sort(key=lambda i: self.indexFromItem(i).row())
        return ''.join(i.text() + '\n' for i in items)


    def focusInEvent(self, event):
        super(ObservationListWidget, self).focusInEvent(event)
        self._mainWindow._updateMenuItemStates()
        
        
    def focusOutEvent(self, event):
        super(ObservationListWidget, self).focusOutEvent(event)
        self._mainWindow._updateMenuItemStates()
    