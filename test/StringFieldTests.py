from maka.data.Field import String
from maka.data.Observation import Observation

from FieldTests import FieldTests, fieldTestClass

    
@fieldTestClass
class StringFieldTests(FieldTests):
    
    
    fieldClass = String
    validValue = 'bobo'
    invalidValue = 0
    defaultTypeName = 'string'
    
    
    def testStringFieldWithRestrictedValues(self):
        
        class Obs(Observation):
            s = String(values=['One', 'Two'])
            
        self.assertEqual(Obs.s.range, '{"One", "Two"}')
            
        obs = Obs()
        
        self.assertIsNone(obs.s)
        
        obs.s = 'One'
        self.assertEqual(obs.s, 'One')
        
        self._assertRaises(ValueError, setattr, obs, 's', 'Three')
        
        
    def testValueTypeError(self):
        self._assertRaises(TypeError, String, **{'values': ['One', 2]})
        
        
    def testDefaultTypeError(self):
        self._assertRaises(ValueError, String, **{'values': ['One', 'Two'], 'default': 'Three'})
