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
from import_relative import import_relative

# Our local modules
Mbase_cmd  = import_relative('base_cmd', top_name='pydbgr')
Mstack    = import_relative('stack', '...lib', 'pydbgr')
Mcmdfns   = import_relative('cmdfns', top_name='pydbgr')

class FinishCommand(Mbase_cmd.DebuggerCommand):

    category      = 'running'
    execution_set = ['Running']
    min_args      = 0
    max_args      = 1
    name_aliases  = ('finish',)
    need_stack    = True
    short_help   = 'Execute until selected stack frame returns'

    def run(self, args):
        """finish [levels|fn]

Continue execution until leaving the current function. When `level' is
specified, that many frame levels need to be popped. Note that 'yield'
and exceptions raised my reduce the number of stack frames. Also, if a
thread is switched, we stop ignoring levels.

If fn is given, that's a short-hand way of looking up how many levels
until that frame. However the same provisions regarding stopping,
exceptions, 'yeild'ing and so on still apply.

See the break command if you want to stop at a particular point in a
program."""

        if self.proc.stack is None: return False
        if len(args) <= 1:
            levels = 1
        else:
            max_levels = len(self.proc.stack)
            try:
                levels = Mcmdfns.get_pos_int(self.errmsg, args[1], default=1,
                                             at_most = max_levels, 
                                             cmdname='finish')
            except ValueError:
                return False
            pass

        self.core.step_events      = ['return']
        self.core.stop_on_finish   = True
        self.core.stop_level       = Mstack.count_frames(self.proc.frame)-levels+1
        self.core.last_frame       = self.proc.frame
        self.proc.continue_running = True # Break out of command read loop
        return True
    pass

if __name__ == '__main__':
    from mock import MockDebugger
    d = MockDebugger()
    cmd = FinishCommand(d.core.processor)
    # Need to have a subroutine to get at least one frame f_back.
    def demo_finish(cmd):
        for c in (['finish', '1'],
                  ['finish', 'wrong', 'number', 'of', 'args'],
                  ['finish', '5'],
                  ['finish', '0*5+1']):
            cmd.continue_running = False
            cmd.proc.stack = [(sys._getframe(0), 14,)]
            result = cmd.run(c)
            print 'Execute result: %s' % result
            print 'stop_frame %s, continue_running: %s' % (
                cmd.core.stop_frame,
                cmd.continue_running,)
            pass
        return
    demo_finish(cmd)
    pass