import io

from pyme import base, ports, reader, types, write

def scheme_list(lst, cdr=None):
    result = cdr
    for item in reversed(lst):
        result = base.cons(item, result)
    return result


def from_scheme_list(lst):
    result = []
    while base.pairp(lst):
        result.append(lst.car)
        lst = lst.cdr
    return result, lst


def read_str(str, symbol_table=None):
    if symbol_table is None:
        symbol_table = types.SymbolTable()
    in_port = ports.TextStreamPort(io.StringIO(str))
    reader_ = reader.Reader(symbol_table=symbol_table)
    return reader_.read(in_port)


def write_str(obj):
    stream = io.StringIO()
    port = ports.TextStreamPort(stream)
    write.write_to(obj, port)
    return stream.getvalue()


def display_str(obj):
    stream = io.StringIO()
    port = ports.TextStreamPort(stream)
    write.display_to(obj, port)
    return stream.getvalue()
