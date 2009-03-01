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
from import_relative import import_relative

# Our local modules
Mbase_cmd  = import_relative('base_cmd', top_name='pydbg')
import signal

class KillCommand(Mbase_cmd.DebuggerCommand):

    category      = 'running'
    min_args      = 0
    max_args      = 1
    name_aliases  = ('kill',)
    need_stack    = False
    short_help    = 'Send this process a POSIX signal ("9" for "kill -9")'

    def run(self, args):
        """kill [unconditionally]

Kill execution of program being debugged.

Equivalent of kill -KILL <pid> where <pid> is os.getpid(), the current
debugged process. This is an unmaskable signal. When all else fails, e.g. in
thread code, use this.

If 'unconditionally' is given, no questions are asked. Otherwise, if
we are in interactive mode, we'll prompt to make sure.
"""

        signo =  signal.SIGKILL
        confirmed = False
        if len(args) <= 1:
            confirmed = self.confirm('Really do a hard kill', False)
        elif 'unconditionally'.startswith(args[1]):
            confirmed = True
        else:
            try:
                signo = int(args[1])
                confirmed = True
            except ValueError, TypeError:
                pass
            pass

        if confirmed: 
            import os
            os.kill(os.getpid(), signo)
            pass
        return False # Possibly not reached
    pass

if __name__ == '__main__':
    def handle(*args):
        print 'signal received'
        pass
    signal.signal(28, handle)

    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = KillCommand(cp)
    command.run(['kill', 'wrong', 'number', 'of', 'args'])
    command.run(['kill', '28'])
    command.run(['kill'])

