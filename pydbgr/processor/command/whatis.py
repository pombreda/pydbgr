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
import inspect, sys, types
from import_relative import import_relative

# Our local modules
Mbase_cmd = import_relative('base_cmd', top_name='pydbgr')
Mstack    = import_relative('stack', '...lib', 'pydbgr')
Mcmdfns   = import_relative('cmdfns', top_name='pydbgr')

class WhatisCommand(Mbase_cmd.DebuggerCommand):
    '''whatis arg
    Prints the type of the argument which can be a Python expression.'''
    category      = 'data'
    min_args      = 0
    max_args      = None
    name_aliases  = ('whatis',)
    need_stack    = True
    short_help   = 'Print data type of expression EXP'

    def run(self, args):
        arg = ' '.join(args[1:])
        try:
            if not self.proc.curframe:
                # ?? Should we have set up a dummy globals
                # to have persistence?
                value = eval(arg, None, None)
            else:
                value = eval(arg, self.proc.curframe.f_globals,
                             self.proc.curframe.f_locals)
        except:
            t, v = sys.exc_info()[:2]
            if type(t) == types.StringType:
                exc_type_name = t
            else: exc_type_name = t.__name__
            if exc_type_name == 'NameError':
                self.errmsg("Name Error: %s" % arg)
            else:
                self.errmsg("%s: %s" % (exc_type_name, self.proc._saferepr(v)))
            return False
        if inspect.ismethod(value):
            self.msg('method %s%s' %
                     (value.func_code.co_name,
                       inspect.formatargspec(inspect.getargspec(value))))
            if inspect.getdoc(value):
                self.msg('%s:\n%s' %
                         (value, inspect.getdoc(value)))
            return False
        elif inspect.isfunction(value):
            self.msg('function %s%s' %
                     (value.func_code.co_name,
                       inspect.formatargspec(inspect.getargspec(value))))
            if inspect.getdoc(value):
                self.msg('%s:\n%s' %
                         (value, inspect.getdoc(value)))
            return False
        # None of the above...
        self.msg(type(value))
        return False

    pass

if __name__ == '__main__':
    cmdproc      = import_relative('cmdproc', '..')
    debugger     = import_relative('debugger', '...')
    d            = debugger.Debugger()
    cp           = d.core.processor
    command      = WhatisCommand(cp)
    cp.curframe = inspect.currentframe()
    cp.stack, cp.curindex = cmdproc.get_stack(cp.curframe, None, None,
                                              cp)
    command.run(['whatis', 'cp'])
    command.run(['whatis', '5'])
    pass
