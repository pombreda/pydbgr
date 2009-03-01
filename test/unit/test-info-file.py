#!/usr/bin/env python
'Unit test for pydbg.clifns'
import inspect, os, sys, unittest
from import_relative import *

debugger  = import_relative('debugger', '...pydbg', 'pydbg')
Minfo     = import_relative('pydbg.processor.command.info', '...')
MinfoFile = import_relative('pydbg.processor.command.infosub.file', '...')
Mdebugger = import_relative('debugger', '...pydbg')

from cmdhelper import dbg_setup

class TestInfoFile(unittest.TestCase):

    def setUp(self):
        self.msgs = []
        return

    def msg_nocr(self, msg):
        if len(self.msgs) > 0:
            self.msgs[-1] += msg
        else:
            self.msgs += msg
            pass
        return
    def msg(self, msg):
        self.msgs += [msg]
        return

    def test_info_file(self):
        d = Mdebugger.Debugger()
        d, cp = dbg_setup(d)
        command = Minfo.InfoCommand(cp, 'info')
        sub = MinfoFile.InfoFile(command)
        sub.run([])
        self.assertEqual([], self.msgs)
        cp.curframe = inspect.currentframe()
        for width in (80, 200):
            # sub.settings['width'] = width
            sub.run(['test-info-file.py', 'lines'])
            print sub.run([])
            pass
        pass
        
if __name__ == '__main__':
    unittest.main()