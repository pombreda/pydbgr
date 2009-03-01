# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.
import sys

# Our local modules
from import_relative import import_relative

import_relative('lib', '...', 'pydbg')
Mbase_cmd  = import_relative('base_cmd', top_name='pydbg')
Mcmdfns    = import_relative('cmdfns', top_name='pydbg')
Mfile      = import_relative('lib.file', '...', 'pydbg')
Mmisc      = import_relative('misc', '...', 'pydbg')
Mpp        = import_relative('pp', '...lib', 'pydbg')

class RetvalCommand(Mbase_cmd.DebuggerCommand):
    """retval 

Show the value that is to be returned from a function.  This command
is useful after a 'finish' command or stepping just after a 'return'
statement."""

    category      = 'data'
    min_args      = 0
    max_args      = 0
    name_aliases  = ('retval', 'rv')
    need_stack    = True
    short_help    = 'Show function return value'

    def run(self, args):
        # Not sure if this __return__ stuff works. 
#         if '__return__' in self.proc.curframe.f_locals:
#             val = self.proc.curframe.f_locals['__return__']
#             Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg)
#         elif self.proc.event == 'return':
        if self.proc.event in ['return', 'exception']:
            val = self.proc.event_arg
            Mpp.pp(val, self.settings['width'], self.msg_nocr, self.msg)
        else:
            self.errmsg("Must be in a 'return' or 'exception' event rather than a %s event."
                        % self.proc.event)
            pass
        return

if __name__ == '__main__':
    Mdebugger = import_relative('debugger', '...')
    d = Mdebugger.Debugger()
    command = RetvalCommand(d.core.processor)
    command.proc.frame = sys._getframe()
    command.proc.setup()
    command.run(['retval'])
    pass