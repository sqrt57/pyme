import io

from pyme import base
from pyme import eval
from pyme import ports
from pyme.reader import Reader
from pyme import types
from pyme import write


def scheme_list(list_, cdr=base.null()):
    result = cdr
    for item in reversed(list_):
        result = base.cons(item, result)
    return result


def from_scheme_list(list_):
    result = []
    while base.pairp(list_):
        result.append(list_.car)
        list_ = list_.cdr
    return result, list_


def read_str(str_, symbol_table=None):
    if symbol_table is None:
        symbol_table = types.SymbolTable()
    in_port = ports.TextStreamPort(io.StringIO(str_))
    reader = Reader(symbol_table=symbol_table)
    return reader.read(in_port)


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


def str_bindings_to_env(str_bindings, symbol_table):
    bindings = {
        symbol_table[name]: value
        for name, value in str_bindings.items()
    }
    return types.Environment(bindings=bindings)


def env_to_str_bindings(env):
    result = {}
    while env:
        for symbol, value in env.bindings.items():
            name = symbol.name
            if name not in result:
                result[name] = value
        env = env.parent
    return result


def eval_str(str_, str_bindings):
    symbol_table = types.SymbolTable()
    env = str_bindings_to_env(str_bindings, symbol_table)
    reader = Reader(symbol_table=symbol_table)
    in_port = ports.TextStreamPort(io.StringIO(str_))
    result = False
    while True:
        expr = reader.read(in_port)
        if base.eofp(expr):
            return result
        result = eval.eval(expr, env=env)
