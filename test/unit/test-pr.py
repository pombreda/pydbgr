#!/usr/bin/env python
'Unit test for trepan.processor.command.pr'
import unittest

from import_relative import import_relative

Mp = import_relative('processor.command.pr', '...trepan')

class TestP(unittest.TestCase):
    """Tests PCommand class"""

    def setUp(self):
        self.errors = []
        self.msgs = []
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def msg(self, msg):
        self.msgs.append(msg)
        return

    def test_pr(self):
        import inspect
        debugger    = import_relative('debugger', '...trepan', 'trepan')
        d           = debugger.Debugger()
        cp          = d.core.processor
        cp.curframe = inspect.currentframe()
        cmd         = Mp.PrCommand(cp)
        cmd.msg     = self.msg
        cmd.errmsg  = self.errmsg
        me = 10
        cmd.run([cmd.name, 'me'])
        self.assertEqual('10', self.msgs[-1])
        cmd.run([cmd.name, '/x', 'me'])
        self.assertEqual("'0xa'", self.msgs[-1])
        cmd.run([cmd.name, '/o', 'me'])
        self.assertEqual("'012'", self.msgs[-1])
        return

if __name__ == '__main__':
    unittest.main()
