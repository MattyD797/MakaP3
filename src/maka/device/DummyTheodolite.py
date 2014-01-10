class DummyTheodolite(object):
    
    '''Dummy theodolite that always returns vertical and horizontal angles of zero.'''
    
    extensionName = 'Dummy Theodolite'
    
    def readAngles(self):
        return (0., 0.)
    