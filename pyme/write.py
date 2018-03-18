import numbers


def write_to(obj, port):
    if 'write_to' in dir(obj):
        obj.write_to(port)
    elif obj is None:
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
    elif obj is None:
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
