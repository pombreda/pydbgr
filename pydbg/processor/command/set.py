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
base_submgr  = import_relative('base_submgr', top_name='pydbg')

class SetCommand(base_submgr.SubcommandMgr):
    """Modifies parts of the debugger environment.

You can give unique prefix of the name of a subcommand to get
information about just that subcommand.

Type "set" for a list of 'set" subcommands and what they do.
Type "help set *" for just the list of "set" subcommands.
"""

    category      = 'data'
    min_args      = 0
    max_args      = None
    name_aliases  = ('set',)
    need_stack    = False
    short_help    = 'Modify parts of the debugger environment'

if __name__ == '__main__':
    mock = import_relative('mock')
    d, cp = mock.dbg_setup()
    command = SetCommand(cp, 'set')
    command.run(['set'])
    pass