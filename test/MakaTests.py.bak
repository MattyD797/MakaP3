from __future__ import print_function

import sys
import unittest


class TestCase(unittest.TestCase):
    

    def _assertRaises(self, cls, callable, *args, **kwds):
        
        with self.assertRaises(cls) as cm:
            callable(*args, **kwds)
            
        print(str(cm.exception), file=sys.stderr)
