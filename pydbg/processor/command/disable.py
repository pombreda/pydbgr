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

# Our local modules
from import_relative import import_relative

import_relative('lib', '...', 'pydbg')
Mbase_cmd  = import_relative('base_cmd', top_name='pydbg')
Mcmdfns    = import_relative('cmdfns', top_name='pydbg')
Mfile      = import_relative('lib.file', '...', 'pydbg')
Mmisc      = import_relative('misc', '...', 'pydbg')
Mbreak     = import_relative('break', '.', 'pydbg')

class DisableCommand(Mbase_cmd.DebuggerCommand):
    """disable [display] bpnumber [bpnumber ...]
    
Disables the breakpoints given as a space separated list of breakpoint
numbers. See also 'info break' to get a list.
"""

    category      = 'breakpoints'
    min_args      = 0
    max_args      = None
    name_aliases  = ('disable',)
    need_stack    = False
    short_help    = 'Disable some breakpoints'

    def run(self, args):
        if len(args) == 1:
            self.errmsg('No breakpoint number given.')
            return
#         if args[1] == 'display':
#             self.display_enable(args[2:], 0)
#             return
        for i in args[1:]:
            success, msg = self.core.bpmgr.en_disable_breakpoint_by_number(i, False)
            if not success:
                self.errmsg(msg)
            else:
                self.msg('Breakpoint %s disabled.' % i)
                pass
            pass
        return
        

if __name__ == '__main__':
    Mdebugger = import_relative('debugger', '...')
    d = Mdebugger.Debugger()
    command = DisableCommand(d.core.processor)
    pass