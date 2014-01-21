'''Module containing `CommandInterpreter` class.'''


class CommandInterpreter(object):
    
    '''Abstract command interpreter.'''
    
    
    extensionName = None
    '''the extension name of this command interpreter, of type `str`.'''
    
    documentFormatNames = None
    '''set of `str` extension names of the document formats supported by this interpreter.'''


    def interpretCommand(self, commandText):
        
        '''
        Interprets the specified command text to create a new observation.
        
        :Parameters:
            commandText : `str`
                the command text to be interpreted.
                
        :Returns:
            a new `Observation` created from the command text.
        '''
        
        raise NotImplementedError()
