# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2013 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', '.',  'trepan')
Mcmdfns   = import_relative('cmdfns',   '..', 'trepan')
Mcomplete = import_relative('complete', '...lib', 'trepan')

class UpCommand(Mbase_cmd.DebuggerCommand):

    signum        = 1
    category      = 'stack'
    min_args      = 0
    max_args      = 1
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = True
    short_help    = 'Move frame in the direction of the caller of the last-selected frame'

    #######################################################
    ## FIXME: put into frame processor function
    def frame_low_high(self, direction):
        stack_size = len(self.proc.stack) # - hide_level
        if direction is None:
            return [-stack_size, stack_size-1]
        else:
            frame_index = self.proc.curindex
            low, high = [ frame_index * -direction,
                          (stack_size - frame_index - 1) * direction ]
            if direction < 0: low, high = [high, low]
            return (low, high)
        return

    def frame_complete(self, prefix, direction):
        low, high = self.frame_low_high(direction)
        ary = [str(low+i) for i in range(high-low+1)]
        return Mcomplete.complete_token(ary, prefix)

    def complete(self, prefix):
        return self.frame_complete(prefix, self.signum)

    def adjust_relative(self, args, signum):
        if not self.proc.stack:
            self.errmsg("Program has no stack frame set.")
            return False
        if len(args) == 1:
            count = 1
        else:
            i_stack = len(self.proc.stack)
            count_str = args[1]
            low, high = self.frame_low_high(signum)
            count = Mcmdfns.get_an_int( self.errmsg, count_str,
                                        ("The '%s' command argument must eval to an" +
                                         " integer. Got: %s") % (self.name, count_str),
                                                                 low, high )
            if count is None: return
            pass

        self.proc.adjust_frame(pos=self.signum*count, absolute_pos=False)
        return
    ## FIXME: put above frame processor function
    #######################################################

    def run(self, args):
        """**up** [*count*]

Move the current frame up in the stack trace (to an older frame). 0 is
the most recent frame. If no count is given, move up 1.

See also `down` and `frame`."""
        self.adjust_relative(args, 1)
        return False


if __name__ == '__main__':
    Mcmdproc     = import_relative('cmdproc', '..')
    Mdebugger    = import_relative('debugger', '...')
    d            = Mdebugger.Debugger()
    cp           = d.core.processor
    command = UpCommand(cp)
    command.run(['up'])

    def nest_me(cp, command, i):
        import inspect
        if i > 1:
            cp.curframe = inspect.currentframe()
            cp.stack, cp.curindex = Mcmdproc.get_stack(cp.curframe, None, None,
                                                       cp)
            command.run(['up'])
            print '-' * 10
            command.run(['up', '-2'])
            print '-' * 10
            command.run(['up', '-3'])
            print '-' * 10
        else:
            nest_me(cp, command, i+1)
        return

    cp.forget()
    nest_me(cp, command, 1)
    pass
