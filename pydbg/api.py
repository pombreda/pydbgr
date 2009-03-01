# -*- coding: utf-8 -*-
#   Copyright (C) 2008, 2009 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''Some singleton debugger methods that can be called without first
creating a debugger object -- these methods will create a debugger object, 
if necessary, first.
'''

# The following routines could be done via something like the following
# untested code:
# def _build_standalone(methodname, docstring=None):
#     def function(arg, arg2=None, globals=None, locals=None):
#         Debugger().getattr(methodname)(arg, arg2, globals, locals)
#        return 
#    function.__name__ = methodname
#    function.__doc__ = docstring
#    return function
#
# But this a bit cumbersome and perhaps overkill for the 2 or so
# functions below.  (It also doesn't work once we add the exception handling
# we see below. So for now, we'll live with the code duplication.

from import_relative import import_relative

Mdebugger    = import_relative('debugger', top_name='pydbg')
Mpost_mortem = import_relative('post_mortem', top_name='pydbg')

def debugger_on_post_mortem():
    '''Call debugger on an exeception that terminates a program'''
    return sys.excepthook(Mpost_mortem.post_mortem_excepthook)

def run_eval(expression, debug_opts=None, start_opts=None, globals_=None, 
             locals_=None):

    """Evaluate the expression (given as a string) under debugger
    control starting with the statement subsequent to the place that
    this appears in your program.

    This is a wrapper to Debugger.run_eval(), so see that.

    When run_eval() returns, it returns the value of the expression.
    Otherwise this function is similar to run()."""

    
    dbg = Mdebugger.Debugger(opts=debug_opts)
    try:
        return dbg.run_eval(expression, start_opts=start_opts, 
                            globals_=globals_, locals_=locals_)
    except:
        Mpost_mortem.uncaught_exception(dbg)
        pass
    return

def run_call(func, debug_opts=None, start_opts=None, *args, **kwds):

    """Call the function (a function or method object, not a string)
    with the given arguments starting with the statement subsequent to
    the place that this appears in your program.

    When run_call() returns, it returns whatever the function call
    returned.  The debugger prompt appears as soon as the function is
    entered."""

    dbg = Mdebugger.Debugger(opts=debug_opts) 
    try:
        return dbg.run_call(func, start_opts=start_opts, *args, **kwds)
    except:
        Mpost_mortem.uncaught_exception(dbg)
        pass
    return

def run_exec(statement, debug_opts=None, start_opts=None, globals_=None, 
             locals_=None):

    """Execute the statement (given as a string) under debugger
    control starting with the statement subsequent to the place that
    this run_call appears in your program.

    This is a wrapper to Debugger.run_exec(), so see that.

    The debugger prompt appears before any code is executed;
    you can set breakpoints and type 'continue', or you can step
    through the statement using 'step' or 'next'

    The optional globals_ and locals_ arguments specify the environment
    in which the code is executed; by default the dictionary of the
    module __main__ is used."""

    dbg = Mdebugger.Debugger(opts=debug_opts) 
    try:
        return dbg.run_exec(statement, start_opts=start_opts, 
                            globals_=globals_, locals_=locals_)
    except:
        Mpost_mortem.uncaught_exception(dbg)
        pass
    return

def debug(dbg_opts=None, start_opts=None):
    """ 
Enter the debugger. Use like this:

    ... # Some python code
    import pydbg; pydbg.api.debug() # This also works well inside an `if' stmt
    # Below is code you want to use the debugger to do things.
    ....  # more Python code
    # If you get to a place in the program where you aren't going 
    # want to debug any more, but want to remove debugger trace overhead:
    pydbg.stop() 

Module variable pydbg.debugger.debugger_obj is used as the debugger
instance and it can be subsequenly used to change settings or alter
behavior. It should be of type pydbg.Debugger. If not it will get
reset.

If however you want your own separate debugger instance use
pydbg.Debugger() to create an new Debugger instance.instead of the
variable pydbg.debugger.debugger_obj.

`dbg_opts' is an optional "options" dictionary that gets fed
pydbg.Debugger(); `start_opts' are the optional "options"
dictionary that gets fed to pydbg.Debugger.core.start().
"""
    if Mdebugger.Debugger != type(Mdebugger.debugger_obj):
        Mdebugger.debugger_obj = Mdebugger.Debugger(dbg_opts)
        Mdebugger.debugger_obj.core.add_ignore(debug, stop)
        pass
    if not Mdebugger.debugger_obj.core.is_started():
        Mdebugger.debugger_obj.core.start(start_opts)
        pass
    Mdebugger.debugger_obj.core.step_ignore = 0;
    return 

def stop(opts=None):
    if Mdebugger.Debugger == type(Mdebugger.debugger_obj):
        return Mdebugger.debugger_obj.stop(opts)
    return None

# Demo it
if __name__=='__main__':
    import sys, tracer
    def foo():
        y = 2
        for i in range(2):
            print i
            pass
        return 3
    Mdefault = import_relative('default', 'lib', 'pydbg')
    settings = dict(Mdefault.DEBUGGER_SETTINGS)
    settings.update({'trace': True, 'printset': tracer.ALL_EVENTS})
    debug_opts={'step_ignore': -1, 'settings': settings}
    print 'Issuing: run_eval("1+2")'
    print run_eval('1+2', debug_opts=debug_opts)
    print 'Issuing: run_exec("x=1; y=2")'
    run_exec('x=1; y=2', debug_opts=debug_opts)
    print 'Issuing: run_call(foo)'
    run_call(foo, debug_opts=debug_opts)
    if len(sys.argv) > 1:
        # FIXME: should this work better?
        # print 'Issuing interactive: run_exec(x=1; y=2)'
        # run_exec('x=1; y=2')
        print 'Issuing interactive: run_call(foo)'
        run_call(foo)
    pass
 