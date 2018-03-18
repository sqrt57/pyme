import numbers

from pyme import core, scheme_base, exceptions, interop


def eval(expr, env):
    if isinstance(expr, numbers.Integral):
        return expr
    elif isinstance(expr, str):
        return expr
    elif isinstance(expr, core.Symbol):
        return env[expr]
    elif isinstance(expr, core.Pair):
        args, rest = interop.from_scheme_list(expr.cdr)
        if not scheme_base.nullp(rest):
            raise exceptions.EvalError("Expected proper list in procedure application")
        proc = eval(expr.car, env)
        args = [eval(x, env) for x in args]
        return apply(proc, args)
    else:
        raise TypeError("Cannot eval type " + type(expr).__name__)


def apply(proc, args):
    return proc(*args)
