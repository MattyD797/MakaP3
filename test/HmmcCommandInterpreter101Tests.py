from maka.hmmc.HmmcCommandInterpreter101 import HmmcCommandInterpreter101, _tokenizeCommand

from MakaTests import TestCase

    
class HmmcCommandInterpreter101Tests(TestCase):
    
    
    def testCommandTokenization(self):
        
        cases = [
            ('', []),
            (' ', []),
            ('a', ['a']),
            ('  a  ', ['a']),
            ('a bc d', ['a', 'bc', 'd']),
            ('a 12 34', ['a', '12', '34']),
            ('a1', ['a', '1']),
            ('a12', ['a', '12']),
            ('a12 34', ['a', '12', '34']),
            ('12 34', ['12', '34']),
            ('a1b 23', ['a1b', '23']),
            ('c "One"', ['c', '"One"']),
            ('c "One Two"', ['c', '"One Two"']),
            ('c 12 "One Two" 34', ['c', '12', '"One Two"', '34']),
#            (r'c "String containing \\ and \""', ['c', '"String containing \\ and ""'])
        ]
        
        for command, tokens in cases:
            self.assertEqual(_tokenizeCommand(command), tokens)
