import numbers

from pyme import base, exceptions, interop


def eval(expr, env):
    if isinstance(expr, numbers.Integral):
        return expr
    elif isinstance(expr, str):
        return expr
    elif base.symbolp(expr):
        return env[expr]
    elif base.pairp(expr):
        args, rest = interop.from_scheme_list(expr.cdr)
        if not base.nullp(rest):
            raise exceptions.EvalError("Expected proper list in procedure application")
        proc = eval(expr.car, env)
        args = [eval(x, env) for x in args]
        return apply(proc, args)
    else:
        raise TypeError("Cannot eval type " + type(expr).__name__)


def apply(proc, args):
    return proc(*args)
