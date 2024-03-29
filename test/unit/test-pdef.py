#!/usr/bin/env python
'Unit test for trepan.processor.command.pdef'
import unittest

from import_relative import import_relative

Mp = import_relative('processor.command.pdef', '...trepan')

class TestPDef(unittest.TestCase):
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

    def test_pdef(self):
        import inspect
        debugger    = import_relative('debugger', '...trepan', 'trepan')
        d           = debugger.Debugger()
        cp          = d.core.processor
        cp.curframe = inspect.currentframe()
        cmd         = Mp.PrintDefCommand(cp)
        cmd.msg     = self.msg
        cmd.errmsg  = cp.errmsg = self.errmsg
        cmd.run(['pdef', 'self.test_pdef'])
        self.assertEqual('self.test_pdef(self)', self.msgs[-1])
        cmd.run(['pdef', 'TestPDef'])
        self.assertEqual("TestPDef(self, methodName='runTest')",
                         self.msgs[-1])
        self.assertEqual(0, len(self.errors))
        cmd.run(['pdef', 'FOO'])
        self.assertEqual(1, len(self.errors))
        return

if __name__ == '__main__':
    unittest.main()
