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
import columnize

# Our local modules
from import_relative import import_relative

import_relative('processor', '...', 'pydbg') 

Mbase_cmd  = import_relative('base_cmd', top_name='pydbg')
Mcmdproc   = import_relative('cmdproc', '..', 'pydbg')
Mmisc      = import_relative('misc', '...', 'pydbg')

categories = {
    'breakpoints' : 'Making the program stop at certain points',
    'data'        : 'Examining data',
    'running'     : 'Running the program', 
    'status'      : 'Status inquiries',
    'support'     : 'Support facilities',
    'stack'       : 'Examining the call stack'
    }

class HelpCommand(Mbase_cmd.DebuggerCommand):

    category      = 'support'
    min_args      = 0
    max_args      = None
    name_aliases  = ('help', '?',)
    need_stack    = False
    short_help    = 'Print commands or give help for command(s)'

    def run(self, args):
        """help [command [subcommand]|expression]

Without argument, print the list of available debugger commands.

When an argument is given, it is first checked to see if it is command
name. 'help exec' gives help on the ! command.

With the argument is an expression or object name, you get the same
help that you would get inside a Python shell running the built-in
help() command.

If the environment variable $PAGER is defined, the file is
piped through that command.  You'll notice this only for long help
output.

Some commands like 'info', 'set', and 'show' can accept an
additional subcommand to give help just about that particular
subcommand. For example 'help info line' give help about the
info line command.

See also 'examine' an 'whatis'.
"""

        # It does not make much sense to repeat the last help
        # command. Also, given that 'help' uses PAGER, the you may
        # enter an extra CR which would rerun the (long) help command.
        self.proc.last_cmd='' 
        
        if len(args) > 1:
            if args[1] == '*':
                self.msg("List of all debugger commands:")
                self.columnize_all_commands()
                return
            elif args[1] in categories.keys():
                self.show_category(args[1:])
                return

            command_name = Mcmdproc.resolve_name(self.proc, args[1])
            if command_name:
                instance = self.proc.name2cmd[command_name]
                if hasattr(instance, 'help'):
                    return instance.help(args)
                else:
                    doc = instance.__doc__ or instance.run.__doc__
                    self.msg(doc.rstrip("\n"))
                    aliases = [key for key in self.proc.alias2name 
                               if command_name == self.proc.alias2name[key]]
                    if len(aliases) > 0:
                        self.msg('')
                        msg = Mmisc.wrapped_lines('Aliases:', 
                                                  ', '.join(aliases) + '.',
                                                  self.settings['width'])
                        self.msg(msg)
                        pass
                    pass
            else:
                self.errmsg('Undefined command: "%s".  Try "help".' % 
                            args[1])
                pass
            return
        else:
            self.list_categories()
            pass

        return False

    def columnize_all_commands(self):
        """List all commands arranged in an aligned columns"""
        commands = self.proc.name2cmd.keys()
        commands.sort()
        self.msg(columnize.columnize(commands, lineprefix='    '))
        return

    def list_categories(self):
        """List the command categories and a short description of each."""
        self.msg("Classes of commands:\n")
        cats = categories.keys()
        cats.sort()
        for cat in cats:  # Foo! iteritems() doesn't do sorting
            self.msg("%-13s -- %s" % (cat, categories[cat]))
            pass
        final_msg = """
Type "help" followed by a class name for a list of commands in that class.
Type "help *" for the list of all commands.
Type "help CLASS *" for the list of all commands in class CLASS.
Type "help" followed by command name for full documentation.
"""
        self.msg(final_msg)
        return

    def show_category(self, args):
        """Show short help for all commands in `category'."""
        category = args[0]
        n2cmd = self.proc.name2cmd
        names = n2cmd.keys()
        if len(args) == 2 and args[1] == '*':
            self.msg("Commands in class %s:" % category)
            cmds = [cmd for cmd in names if category == n2cmd[cmd].category]
            cmds.sort()
            self.msg(columnize.columnize(cmds, lineprefix='    '))
            return
        
        self.msg("%s." % categories[category])
        self.msg("List of commands:\n")
        names.sort()
        for name in names: # Foo! iteritems() doesn't do sorting
            if category != n2cmd[name].category: continue
            self.msg("%-13s -- %s" % (name, n2cmd[name].short_help,))
            pass
        return
        
    pass

if __name__ == '__main__':
    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = HelpCommand(cp)
    print '-' * 20
    command.run(['help'])
    print '-' * 20
    command.run(['help', '*'])
    print '-' * 20
    command.run(['help', 'quit'])
    print '-' * 20
    command.run(['help', 'stack'])
    command.run(['help', 'breakpoints'])
    command.run(['help', 'breakpoints', '*'])
    pass