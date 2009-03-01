#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
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
''' The big and hairy command-line interface to the debugger.
'''

from optparse import OptionParser
import traceback
import tracer 

# Our local modules
from import_relative import *
Mdebugger = import_relative('debugger', top_name='pydbg')
Mclifns   = import_relative('clifns', top_name='pydbg')
Mserver   = import_relative('server', '.interface', 'pydbg')
Mfile     = import_relative('file', '.lib', 'pydbg')
Mmisc     = import_relative('misc', '.', 'pydbg')

# The name of the debugger we are currently going by.
__title__ = 'pydbg'

__version__ = '0.1.0'

def process_options(debugger_name, pkg_version, option_list=None):
    """Handle debugger options. Set `option_list' if you are writing
    another main program and want to extend the existing set of debugger
    options.

    The options dicionary from opt_parser is return. Global sys.argv is
    also updated."""
    usage_str="""%prog [debugger-options] [python-script [script-options...]]

       Runs the extended python debugger"""

    serverChoices = ('TCP','FIFO', None)


    optparser = OptionParser(usage=usage_str, option_list=option_list,
                             version="%%prog version %s" % pkg_version)

    optparser.add_option("-X", "--trace", dest="linetrace",
                         action="store_true", default=False, 
                         help="Show lines before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("-F", "--fntrace", dest="fntrace",
                         action="store_true", default=False, 
                         help="Show functions before executing them. " +
                         "This option also sets --batch")
    optparser.add_option("--basename", dest="basename",
                         action="store_true", default=False, 
                         help="Filenames strip off basename, (e.g. for regression tests)"
                         )
#     optparser.add_option("--batch", dest="noninteractive",
#                          action="store_true", default=False, 
#                          help="Don't run interactive commands shell on "+
#                          "stops.")
    optparser.add_option("-x", "--command", dest="command",
                         action="store", type='string', metavar='FILE',
                         help="Execute commands from FILE.")
    optparser.add_option("--cd", dest="cd",
                         action="store", type='string', metavar='DIR',
                         help="Change current directory to DIR.")
    optparser.add_option("--confirm", dest="confirm",
                         action="store_true", default=True,
                         help="Confirm potentially dangerous operations")
    optparser.add_option("--dbg_pydbg", dest="dbg_pydbg",
                         action="store_true", default=False, 
                         help="Debug the debugger")
    optparser.add_option("--different", dest="different",
                         action="store_true", default=True, 
                         help="Consecutive stops should have different positions")
#     optparser.add_option("--error", dest="errors", metavar='FILE',
#                          action="store", type='string',
#                          help="Write debugger's error output "
#                          + "(stderr) to FILE")
    optparser.add_option("-e", "--exec", dest="execute", type="string",
                         help="list of debugger commands to " +
                         "execute. Separate the commands with ;;")

    optparser.add_option("--private", dest="private",
                         action='store_true', default=False,
                         help="Don't register this as a global debugger")

    optparser.add_option("-n", "--nx", dest="noexecute",
                         action="store_true", default=False, 
                         help="Don't execute commands found in any " +
                         "initialization files")
#     optparser.add_option("-o", "--output", dest="output", metavar='FILE',
#                          action="store", type='string',
#                          help="Write debugger's output (stdout) "
#                          + "to FILE")
    optparser.add_option("-o", "--output", dest="output", metavar='FILE',
                         action="store", type='string',
                         help="Write debugger's output (stdout) "
                         + "to FILE")
#     optparser.add_option("-P", "--port", dest="port",
#                          action="store", type='int',
#                          help="Write debugger's output (stdout) "
#                          + "to FILE")
#     optparser.add_option("--server", dest="server",
#                          default='TCP', 
#                          help="Out-of-process server connection mode (" 
#                          + ', '.join(repr(s) for s in serverChoices)
#                          + ') [default: None]')
    optparser.add_option("--server", dest="server",
                         action='store_true',
                         help="Out-of-process server connection mode")
    optparser.add_option("--sigcheck", dest="sigcheck",
                         action="store_true", default=False, 
                         help="Set to watch for signal handler changes")
    optparser.add_option("-t", "--target", dest="target",
                         help="Specify a target to connect to. Arguments" \
                         + " should be of form, 'protocol address'."),

    # annotate option produces annotations, used in pydbg.el for a better emacs
    # integration. Annotations are similar in purpose to those of GDB (see
    # that manual for a description), although the syntax is different.
    # they have the following format:
    #
    # ^Z^Zannotname
    # <arbitrary text>
    # ^Z^Z
    #
    # where ^Z is the ctrl-Z character, and "annotname" is the name of the
    # annotation. A line with only two ^Z ends the annotation (no nesting
    # allowed). See pydbg.el for the usage
    optparser.add_option("--annotate", default=0, type="int",
                         help="Use annotations to work inside emacs")

    # Set up to stop on the first non-option because that's the name
    # of the script to be debugged on arguments following that are
    # that scripts options that should be left untouched.  We would
    # not want to interpret and option for the script, e.g. --help, as
    # one one of our own, e.g. --help.

    optparser.disable_interspersed_args()

    (opts, sys.argv) = optparser.parse_args()
    dbg_opts = {}

    # Handle debugger startup command files: --nx (-n) and --command.
    dbg_initfiles = []
    if not opts.noexecute:
        # Read debugger startup file(s), e.g. $HOME/.pydbgrc and ./.pydbgrc
        startup_file = ".%src" % debugger_name
        expanded_startup_file = Mclifns.path_expanduser_abs(startup_file)
        if 'HOME' in os.environ:
            startup_home_file = os.path.join(os.environ['HOME'], startup_file)
            expanded_startup_home = \
                Mclifns.path_expanduser_abs(startup_home_file)
            if Mfile.readable(expanded_startup_home):
                dbg_initfiles.append(startup_home_file)
                pass
            pass
        if Mfile.readable(expanded_startup_file) and \
                expanded_startup_file != expanded_startup_home:
            dbg_initfiles.append(debugger_startup)
            pass
        pass

    # As per gdb, first we execute user initialization files and then
    # we execute any file specified via --command.
    if opts.command:
        dbg_initfiles.append(opts.command)
        pass

    dbg_opts['proc_opts'] = {'initfile_list': dbg_initfiles}

    if opts.cd:
        os.chdir(opts.cd)
        pass

    if opts.server:
        intf = Mserver.ServerInterface()
        dbg_opts['interface'] = intf
        if 'FIFO' == intf.server_type:
            print('Starting FIFO server for process %s.' % os.getpid())
        elif 'TCP' == intf.server_type:
            print('Starting TCP server listening on port %s.' % intf.inout.PORT)
            pass
        pass
        
    return opts, dbg_opts

def _postprocess_options(dbg, opts):
    ''' Handle options (`opts') that feed into the debugger (`dbg')'''
    # Set dbg.settings['printset']
    print_events = []
    if opts.fntrace:   print_events = ['c_call', 'c_return', 'call', 'return']
    if opts.linetrace: print_events += ['line']
    if len(print_events): 
        dbg.settings['printset'] = frozenset(print_events)
        pass

    for setting in ('annotate', 'basename', 'different',): 
        dbg.settings[setting] = getattr(opts, setting)
        pass

    # Normally we want to set Mdebugger.debugger_obj so that one can
    # put pydbg.debugger breakpoints in a program and not have more
    # than one debugger running. More than one debugger may confuse
    # users, e.g. set different might stop at the same line once for
    # each debugger.
    if not opts.private:
        Mdebugger.debugger_obj = dbg
        pass

    # FIXME: shouldn't this feed into debugger creation options?
#     if opts.output:
#         try: 
#             dbg.stdout = open(opts.output, 'w')

#         except IOError, (errno, strerror):
#             print "I/O in opening debugger output file %s" % opts.output
#             print "error(%s): %s" % (errno, strerror)
#         except ValueError:
#             print "Could not convert data to an integer."
#         except:
#             print "Unexpected error in opening debugger output file %s" % \
#                   opts.output
#             print sys.exc_info()[0]
#             sys.exit(2)

#     if opts.errors:
#         try: 
#             dbg.stderr = open(opts.errors, 'w')
#         except IOError, (errno, strerror):
#             print "I/O in opening debugger output file %s" % opts.errors
#             print "error(%s): %s" % (errno, strerror)
#         except ValueError:
#             print "Could not convert data to an integer."
#         except:
#             print "Unexpected error in opening debugger output file %s" % \
#                   opts.errors
#             print sys.exc_info()[0]
#             sys.exit(2)

#     if opts.execute:
#         dbg.cmdqueue = list(opts.execute.split(';;'))

#     if opts.sigcheck:
#         dbg.cmdqueue.insert(0, "set sigcheck on")
#     else:
#         dbg.cmdqueue.insert(0, "set sigcheck off")

    
    return 

def main(dbg=None):
    """Routine which gets run if we were invoked directly"""
    global __title__

    # Save the original just for use in the restart that works via exec.
    orig_sys_argv = list(sys.argv)   
    opts, dbg_opts  = process_options(__title__, __version__)
    dbg_opts['orig_sys_argv'] = orig_sys_argv

    if dbg is None:
        dbg = Mdebugger.Debugger(dbg_opts)
        dbg.core.add_ignore(main)
        pass
    _postprocess_options(dbg, opts)

    # process_options has munged sys.argv to remove any options that
    # options that belong to this debugger. The original options to
    # invoke the debugger and script are in global sys_argv

    if len(sys.argv) == 0:
        # No program given to debug. Set to go into a command loop
        # anyway
        mainpyfile = None

    else:
        mainpyfile = sys.argv[0] # Get script filename.
        if not os.path.isfile(mainpyfile):
            mainpyfile=Mclifns.whence_file(mainpyfile)
            is_readable = Mfile.readable(mainpyfile)
            if is_readable is None:
                print("%s: Python script file '%s' does not exist" \
                      % (__title__, mainpyfile,))
                sys.exit(1)
            elif not is_readable:
                print("%s: Can't read Python script file '%s'" \
                    % (__title__, mainpyfile,))
                sys.exit(1)
                return

        # If mainpyfile is an optimized Python script try to find and
        # use non-optimized alternative.
        mainpyfile_noopt = Mfile.file_pyc2py(mainpyfile)
        if mainpyfile != mainpyfile_noopt \
               and Mfile.readable(mainpyfile_noopt):
            print("%s: Compiled Python script given and we can't use that." % __title__)
            print("%s: Substituting non-compiled name: %s" % (
                __title__, mainpyfile_noopt,))
            mainpyfile = mainpyfile_noopt
            pass

        # Replace pydbg's dir with script's dir in front of
        # module search path.
        sys.path[0] = dbg.main_dirname = os.path.dirname(mainpyfile)

    # XXX If a signal has been received we continue in the loop, otherwise
    # the loop exits for some reason.
    dbg.sig_received = False

    if not mainpyfile:
        print('For now, you need to specify a Python script name!')
        sys.exit(2)
        pass

    while True:

        # Run the debugged script over and over again until we get it
        # right.

        try:
            if dbg.program_sys_argv and mainpyfile:
                normal_termination = dbg.run_script(mainpyfile)
                if not normal_termination: break
            else:
                # dbg._wait_for_mainpyfile = True
                # dbg.processor.process_commands(None)
                pass

            dbg.core.execution_status = 'Terminated'
            dbg.intf[-1].msg("The program finished - quit or restart")
            dbg.core.processor.process_commands()
        except Mdebugger.DebuggerQuit:
            break
        except Mdebugger.DebuggerRestart:
            dbg.core.execution_status = 'Restart requested'
            if dbg.program_sys_argv:
                sys.argv = list(dbg.program_sys_argv)
                part1 = ('Restarting %s with arguments:' % 
                         dbg.core.filename(mainpyfile))
                args  = ' '.join(dbg.program_sys_argv[1:])
                dbg.intf[-1].msg(Mmisc.wrapped_lines(part1, args,
                                                     dbg.settings['width']))
            else: break
        except SystemExit:
            # In most cases SystemExit does not warrant a post-mortem session.
            break
        pass

    # Restore old sys.argv
    sys.argv = orig_sys_argv
    return

# When invoked as main program, invoke the debugger on a script
if __name__=='__main__':
    main()