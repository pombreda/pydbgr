#!/usr/bin/env python
'Unit test for trepan.lib.print'
import unittest
from import_relative import import_relative

Mprint = import_relative('lib.print', '...trepan')

class TestLibPrint(unittest.TestCase):

    def test_lib_printf(self):
        self.assertEqual('037', Mprint.printf(31, "/o"))
        self.assertEqual('00011111', Mprint.printf(31, "/t"))
        self.assertEqual('!', Mprint.printf(33, "/c"))
        self.assertEqual('0x21', Mprint.printf(33, "/x"))
        return

    def test_lib_argspec(self):
        self.assertEqual('test_lib_argspec(self)',
                         Mprint.print_argspec(self.test_lib_argspec,
                                              'test_lib_argspec'))
        self.assertFalse(Mprint.print_argspec(None, 'invalid_fn'))
        return
    pass

if __name__ == '__main__':
    unittest.main()
