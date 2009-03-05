# -*- coding: utf-8 -*-
#   Copyright (C) 2009 Rocky Bernstein <rocky@gnu.org>
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
'''Bytecode instruction routines'''

import dis, re
from opcode import opname, HAVE_ARGUMENT

def op_at_code_loc(code, loc):
    try:
        op = ord(code[loc])
    except IndexError:
        return 'got IndexError'
    return opname[op]

def op_at_frame(frame, loc=None):
    code = frame.f_code.co_code
    if loc is None: loc = frame.f_lasti
    return op_at_code_loc(code, loc)

def next_opcode(code, offset):
    '''Return the next opcode and offset as a tuple. Tuple (-100,
    -1000) is returned when reaching the end.'''
    n = len(code)
    while offset < n:
        c = code[offset]
        op = ord(c)
        offset += 1
        if op >= HAVE_ARGUMENT:
            offset += 2
            pass
        yield op, offset
        pass
    yield -100, -1000
    pass

def next_linestart(co, offset, count=1):
    linestarts = dict(dis.findlinestarts(co))
    code = co.co_code
    n = len(code)
    contains_cond_jump = False
    for op, offset in next_opcode(code, offset):
        if offset in linestarts: 
            count -= 1
            if 0 == count:
                return linestarts[offset]
            pass
        pass
    return -1000

def stmt_contains_opcode(co, lineno, query_opcode):
    linestarts = dict(dis.findlinestarts(co))
    code = co.co_code
    found_start = False
    for offset, start_line in linestarts.items():
        if start_line == lineno: 
            found_start = True
            break
        pass
    if not found_start: 
        return False
    for op, offset in next_opcode(code, offset):
        if -1000 == offset or linestarts.get(offset): return False
        opcode = opname[op]
        ##debug: print opcode
        if query_opcode == opcode:
            return True
        pass
    return False

_re_def_str = r'^\s*def\s'
_re_def = re.compile(_re_def_str)
def is_def_stmt(line, frame):
    """Return True if we are looking at a def statement"""
    # Should really also check that operand of 'LOAD_CONST' is a code object
    return (_re_def.match(line) and op_at_frame(frame)=='LOAD_CONST'
            and stmt_contains_opcode(frame.f_code, frame.f_lineno,
                                          'MAKE_FUNCTION'))

_re_class_str = r'^\s*class\s'
_re_class = re.compile(_re_class_str)
def is_class_def(line, frame):
    """Return True if we are looking at a class definition statement"""
    return (_re_class.match(line) 
            and stmt_contains_opcode(frame.f_code, frame.f_lineno,
                                     'BUILD_CLASS'))

# Demo stuff above
if __name__=='__main__':
    import inspect
    def sqr(x):
        return x * x
    frame = inspect.currentframe()
    co = frame.f_code
    lineno = frame.f_lineno
    print 'contains MAKE_FUNCTION', stmt_contains_opcode(co, lineno-4, 
                                                         'MAKE_FUNCTION')
    print 'contains MAKE_FUNCTION', stmt_contains_opcode(co, lineno,
                                                         'MAKE_FUNCTION')

    print "op at frame: ", op_at_frame(frame)
    print "op at frame, position 2", op_at_frame(frame, 2)
    print "def statement: x=5?: ", is_def_stmt('x=5', frame)
    # Not a "def" statement because frame is wrong spot
    print is_def_stmt('def foo():', frame)

    class Foo:
        pass
    lineno = frame.f_lineno
    print 'contains BUILD_CLASS', stmt_contains_opcode(co, lineno-2,
                                                       'BUILD_CLASS')
    print 'contains BUILD_CLASS', stmt_contains_opcode(co, lineno,
                                                       'BUILD_CLASS')
    pass