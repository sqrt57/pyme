import numbers

from pyme import base
from pyme.registry import builtin_with_interpreter


@builtin_with_interpreter("write")
def write(interpreter):
    def write(obj, port=None):
        if port is None:
            port = interpreter.stdout
        write_to(obj, port)
        return False
    return write


@builtin_with_interpreter("display")
def display(interpreter):
    def display(obj, port=None):
        if port is None:
            port = interpreter.stdout
        display_to(obj, port)
        return False
    return display


def write_to(obj, port):
    if 'write_to' in dir(obj):
        obj.write_to(port)
    elif base.nullp(obj):
        port.write("()")
    elif base.booleanp(obj):
        if base.is_true(obj):
            port.write("#t")
        else:
            port.write("#f")
    elif base.numberp(obj):
        port.write(repr(obj))
    elif base.stringp(obj):
        port.write('"')
        port.write(obj)
        port.write('"')
    elif base.bytevectorp(obj):
        port.write('#u8(')
        port.write(" ".join(str(b) for b in obj))
        port.write(')')
    else:
        port.write("#<Python: ")
        port.write(repr(obj))
        port.write(">")


def display_to(obj, port):
    if 'display_to' in dir(obj):
        obj.display_to(port)
    elif base.nullp(obj):
        port.write("()")
    elif base.booleanp(obj):
        if base.is_true(obj):
            port.write("#t")
        else:
            port.write("#f")
    elif base.numberp(obj):
        port.write(str(obj))
    elif base.stringp(obj):
        port.write(obj)
    elif base.bytevectorp(obj):
        port.write('#u8(')
        port.write(" ".join(str(b) for b in obj))
        port.write(')')
    elif 'write_to' in dir(obj):
        obj.write_to(port)
    else:
        port.write("#<Python: ")
        port.write(str(obj))
        port.write(">")


def write_pair_to(pair, port):
    if (base.symbolp(pair.car) and pair.car.name == "quote"
            and base.pairp(pair.cdr) and base.nullp(pair.cdr.cdr)):
        port.write("'")
        write_to(pair.cdr.car, port)
    else:
        port.write("(")
        write_to(pair.car, port)
        cur = pair.cdr
        while base.pairp(cur):
            port.write(" ")
            write_to(cur.car, port)
            cur = cur.cdr
        port.write(")")


def display_pair_to(pair, port):
    if (base.symbolp(pair.car) and pair.car.name == "quote"
            and base.pairp(pair.cdr) and base.nullp(pair.cdr.cdr)):
        port.write("'")
        display_to(pair.cdr.car, port)
    else:
        port.write("(")
        display_to(pair.car, port)
        cur = pair.cdr
        while base.pairp(cur):
            port.write(" ")
            display_to(cur.car, port)
            cur = cur.cdr
        port.write(")")
