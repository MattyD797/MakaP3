from maka.data.Observation import Observation

from MakaTests import TestCase

    
# TODO: Try to figure out a better way to allow field test classes to inherit tests.
# Using the `fieldTestClass` class decorator seems to work fine when test classes are
# run individually from within Eclipse, but it does not work with nosetests, which
# does not see any of the tests that I want to be inherited from `FieldTests`.
# The simplest thing would be to dispense with the class decorator and somehow have
# the `FieldTests` test methods run as members of each of the `FieldTests` subclasses,
# but not for `FieldTests` itself.


def fieldTestClass(cls):
    
    '''
    Class decorator that renames certain `FieldTests` methods in a `FieldTests` subclass
    so that the unit test framework will recognize them as tests. We do not give the
    methods test method names in the first place because then the unit test framework
    would try to run them as tests for the `FieldTests` class. We want them to be run
    as tests *only* for `FieldTests` subclasses.
    '''
    
    names = [
        'testDefaultTypeName',
        'testTypeNameInit',
        'testDefaultUnits',
        'testUnitsInit',
        'testDefaultRange',
        'testRangeInit',
        # TODO: Numeric field range tests.
        'testDefaultDoc',
        'testDocInit',
        'testBasicFieldAssignments',
        'testDefaultFieldValue',
        'testDefaultFieldValueTypeError',
        'testFieldAssignmentTypeError'
    ]
    
    for name in names:
        setattr(cls, name, getattr(FieldTests, '_' + name))
        
    return cls
            
            
class FieldTests(TestCase):
    
    
    # Override these in subclasses.
    fieldClass = None
    validValue = None
    invalidValue = None
    defaultTypeName = None
    
    
    def _testDefaultTypeName(self):
        self._testDefaultFieldAttributeValue(self.fieldClass, 'typeName', self.defaultTypeName)
        
        
    def _testDefaultFieldAttributeValue(self, fieldClass, attributeName, value):
        
        class Obs(Observation):
            v = fieldClass()
            
        self.assertEqual(getattr(Obs.v, attributeName), value)
        
        
    def _testTypeNameInit(self):
        self._testFieldAttributeInit(self.fieldClass, 'typeName', 'bobo')
        
        
    def _testFieldAttributeInit(self, fieldClass, attributeName, value):
        
        class Obs(Observation):
            v = fieldClass(**{attributeName: value})
             
        self.assertEqual(getattr(Obs.v, attributeName), value)
         
         
    def _testDefaultUnits(self):
        self._testDefaultFieldAttributeValue(self.fieldClass, 'units', None)
        
        
    def _testUnitsInit(self):
        self._testFieldAttributeInit(self.fieldClass, 'units', 'bobo')
        
        
    def _testDefaultRange(self):
        self._testDefaultFieldAttributeValue(self.fieldClass, 'range', None)
        
        
    def _testRangeInit(self):
        self._testFieldAttributeInit(self.fieldClass, 'range', 'bobo')
        
        
    def _testDefaultDoc(self):
        self._testDefaultFieldAttributeValue(self.fieldClass, 'doc', None)
        
        
    def _testDocInit(self):
        self._testFieldAttributeInit(self.fieldClass, 'doc', 'bobo')
         
         
    def _testBasicFieldAssignments(self):
         
        class Obs(Observation):
            v = self.fieldClass
             
        obs = Obs()
         
        self.assertIsNone(obs.v)
         
        obs.v = self.validValue
        self.assertEqual(obs.v, self.validValue)
         
        obs.v = None
        self.assertIsNone(obs.v)
         
         
    def _testDefaultFieldValue(self):
         
        class Obs(Observation):
            v = self.fieldClass(default=self.validValue)
             
        obs = Obs()
         
        self.assertEqual(obs.v, self.validValue)
         
         
    def _testDefaultFieldValueTypeError(self):
        self._assertRaises(TypeError, self.fieldClass, **{'default': self.invalidValue})            
             
             
    def _testFieldAssignmentTypeError(self):
         
        class Obs(Observation):
            v = self.fieldClass
             
        obs = Obs()
         
        self._assertRaises(TypeError, setattr, obs, 'v', self.invalidValue)
