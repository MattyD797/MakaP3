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
            
            
    def testRemoveComments(self):
        
        cases = [
            ('one\n#two\nthree\n', 'one\nthree\n'),
            ('\none\ntwo\n  #three\n#\n    five\n#six', '\none\ntwo\n    five\n')
        ]
        
        for s, r in cases:
            self.assertEqual(TextUtils.removeComments(s), r)
            
