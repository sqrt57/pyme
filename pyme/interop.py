import io

from pyme import base
from pyme import eval
from pyme import ports
from pyme import reader
from pyme import types
from pyme import write


def scheme_list(list_, cdr=None):
    result = cdr if cdr is not None else base.null()
    for item in reversed(list_):
        result = base.cons(item, result)
    return result


def from_scheme_list(list_):
    result = []
    while base.pairp(list_):
        result.append(list_.car)
        list_ = list_.cdr
    return result, list_


def read_str(str_, *, symbol_table=None, keyword_table=None):
    if symbol_table is None:
        symbol_table = types.symbol_table()
    if keyword_table is None:
        keyword_table = types.keyword_table()
    in_port = ports.TextStreamPort.from_stream(io.StringIO(str_))
    reader_ = reader.Reader(symbol_table=symbol_table,
                            keyword_table=keyword_table)
    return reader_.read(in_port)


def write_str(obj):
    stream = io.StringIO()
    port = ports.TextStreamPort.from_stream(stream)
    write.write_to(obj, port)
    return stream.getvalue()


def display_str(obj):
    stream = io.StringIO()
    port = ports.TextStreamPort.from_stream(stream)
    write.display_to(obj, port)
    return stream.getvalue()


def str_bindings_to_env(str_bindings, *, symbol_table, parent=None):
    bindings = {
        symbol_table[name]: value
        for name, value in str_bindings.items()
    }
    return types.Environment(bindings=bindings, parent=parent)


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
    symbol_table = types.symbol_table()
    keyword_table = types.keyword_table()
    env = str_bindings_to_env(str_bindings, symbol_table=symbol_table)
    reader_ = reader.Reader(symbol_table=symbol_table,
                            keyword_table=keyword_table)
    in_port = ports.TextStreamPort.from_stream(io.StringIO(str_))
    result = False
    while True:
        expr = reader_.read(in_port)
        if base.eofp(expr):
            return result
        result = eval.eval(expr, env=env)


def get_config(config, path, default=None):
    """Get"""
    path = path.split(".")
    for key in path:
        if config is None: return default
        config = config.get(key)
    if config is None: return default
    return config
