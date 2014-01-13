class DummyTheodolite(object):
    
    '''Dummy theodolite that always returns vertical and horizontal angles of `None`.'''
    
    extensionName = 'Dummy Theodolite'
    
    def readAngles(self):
        return (None, None)
    