import maka.text.TokenUtils as TokenUtils

from MakaTests import TestCase

    
class TokenUtilsTests(TestCase):
    
    
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
            tokens = TokenUtils.tokenizeString(input)
            self.assertEqual(tokens, expected)
            
            
    def testTokenizationErrors(self):
        
        cases = [
            'one "two ',            # unterminated string
            '"',                    # unterminated string
            '"\\"',                 # unterminated string
            'one "two \\ three"',   # single backslash
            '"one \\n two"',        # unrecognized escape
            '"\\t"',                # unrecognized escape
            '"one"two',             # unseparated tokens
            '"one""two"',           # unseparated tokens
            ' "one""two" '          # unseparated tokens
        ]
        
        for case in cases:
            self._assertRaises(ValueError, TokenUtils.tokenizeString, case)
