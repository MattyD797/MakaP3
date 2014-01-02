import maka.util.TextUtils as TextUtils

from MakaTests import TestCase

    
class TextUtilsTests(TestCase):
    
    
    def testSplitCamelCaseString(self):
        
        cases = [
            ('', []),
            ('a', ['a']),
            ('ab', ['ab']),
            ('aB', ['a', 'B']),
            ('aBc', ['a', 'Bc']),
            ('oneTwoThree', ['one', 'Two', 'Three']),
            ('123', ['123']),
            ('hello123', ['hello123']),
            ('hello123FourFive', ['hello123', 'Four', 'Five'])
        ]
        
        for s, r in cases:
            self.assertEqual(TextUtils.splitCamelCaseString(s), r)
            
            
    def testTokenizeString(self):
        
        cases = [
            ('   one two three   ', ['one', 'two', 'three']),
            ('   "one"  two  "three"  ', ['"one"', 'two', '"three"']),
            ('"one" \\ two "three"', ['"one"', '\\', 'two', '"three"']),
            ('Station 1 "Old Ruins" Lat 20 4.925283850520 Lon -155 51.794984516976 El 65.6 MagDec 10:16:00',
             ['Station', '1', '"Old Ruins"', 'Lat', '20', '4.925283850520', 'Lon',
              '-155', '51.794984516976', 'El', '65.6', 'MagDec', '10:16:00'])
        ]
        
        for input, expected in cases:
            result = TextUtils.tokenizeString(input)
            self.assertEqual(result, expected)
            
            
    def testBadStringTokenErrors(self):
        
        cases = [
            'one "two ',            # unterminated string
            '"',                    # unterminated string
            '"\\"',                 # unterminated string
            'one "two \\ three"',   # single backslash
            '"one \\n two"',        # unrecognized escape
            '"\\t"'                 # unrecognized escape
        ]
        
        for case in cases:
            self._assertRaises(ValueError, TextUtils.tokenizeString, case)
            
            

