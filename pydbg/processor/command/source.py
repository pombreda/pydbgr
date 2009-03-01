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
import os, sys
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='pydbg')
Mdebugger = import_relative('debugger', '...', 'pydbg')
Mfile     = import_relative('file', '...lib', 'pydbg')
Mscript   = import_relative('script', '...interface', 'pydbg')

class SourceCommand(Mbase_cmd.DebuggerCommand):
    """source [-v][-Y|-N][-c] FILE

    Read debugger commands from a file named FILE.  Optional -v switch
    (before the filename) causes each command in FILE to be echoed as
    it is executed.  Option -Y sets the default value in any
    confirmation command to be 'yes' and -N sets the default value to 'no'.

    Note that the command startup file '.pydbgrc' is read
    automatically via a source command the debugger is started.
    
    An error in any command terminates execution of the command
    file unless option -c is given."""

    category      = 'support'
    min_args      = 1
    max_args      = None
    name_aliases  = ('source',)
    need_stack    = True
    short_help    = "Read and run debugger commands from a file"


    def run(self, args):
        verbose=False
        parms = args[1:-1]
        opts = {}
        for arg in parms:
            if arg == '-v': opts['verbose'] = True
            elif arg == '-Y': opts['confirm_val'] = True
            elif arg == '-N': opts['confirm_val'] = False
            elif arg == '-c': opts['abort_on_error'] = False
            pass
        filename = args[-1]

        expanded_file = os.path.expanduser(filename)            
        if not Mfile.readable(expanded_file):
            self.errmsg("Debugger command file '%s' is not a readable file"
                        % filename)
            return False

        # Push a new intf.
        script_intf = Mscript.ScriptInterface(expanded_file, opts=opts)
        self.debugger.intf.append(script_intf)
        return False

# Demo it
if __name__ == '__main__':
    Mmock = import_relative('mock')
    d, cp = Mmock.dbg_setup()
    command = SourceCommand(cp)
    if len(sys.argv) > 1:
        command.run([sys.argv[1]])
    pass