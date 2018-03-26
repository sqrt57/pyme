import numbers

from pyme import base


def write_to(obj, port):
    if 'write_to' in dir(obj):
        obj.write_to(port)
    elif base.nullp(obj):
        port.write("()")
    elif isinstance(obj, numbers.Integral):
        port.write(repr(obj))
    elif isinstance(obj, str):
        port.write('"')
        port.write(obj)
        port.write('"')
    else:
        port.write("#<Python: ")
        port.write(repr(obj))
        port.write(">")


def display_to(obj, port):
    if 'display_to' in dir(obj):
        obj.display_to(port)
    elif base.nullp(obj):
        port.write("()")
    elif isinstance(obj, numbers.Integral):
        port.write(str(obj))
    elif isinstance(obj, str):
        port.write(obj)
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
        if not base.nullp(cur):
            port.write(" . ")
            write_to(cur, port)
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
        if not base.nullp(cur):
            port.write(" . ")
            display_to(cur, port)
        port.write(")")
