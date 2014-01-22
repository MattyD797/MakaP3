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
        
        
    def testTranslations(self):
        
        class TranslatedString(String):
            TRANSLATIONS = {'1': 'one', '2': 'two'}
            
        class Obs(Observation):
            s = String(translations={'0': 'zero', '1': 'one'})
            t = TranslatedString
            
        obs = Obs()
        
        obs.s = '0'
        self.assertEqual(obs.s, 'zero')
        
        obs.s = '1'
        self.assertEqual(obs.s, 'one')
        
        obs.s = '2'
        self.assertEqual(obs.s, '2')
        
        obs.t = '0'
        self.assertEqual(obs.t, '0')
 
        obs.t = '1'
        self.assertEqual(obs.t, 'one')
        
        obs.t = '2'
        self.assertEqual(obs.t, 'two')
        
        obs = Obs(s='0', t='0')
        self.assertEqual(obs.s, 'zero')
        self.assertEqual(obs.t, '0')
        
        
    def testTranslationValueError(self):
        self._assertRaises(ValueError, String, **{'values': ['One'], 'translations': {'2': 'Two'}})
        