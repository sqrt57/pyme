import numbers

from pyme import core, scheme_base, exceptions, interop


def _eval_args(args, env):
    result = None
    while args is core.Pair:
        next = core.Pair(eval(args.car, env), None)
        if result is None:
            result = next
        else:
            result.cdr = next
    return result


def eval(expr, env):
    if isinstance(expr, numbers.Integral):
        return expr
    elif isinstance(expr, str):
        return expr
    elif isinstance(expr, core.Symbol):
        return env[expr]
    elif isinstance(expr, core.Pair):
        if not scheme_base.listp(expr):
            raise exceptions.EvalError("Expected proper list in procedure application")
        proc = eval(expr.car, env)
        args = _eval_args(expr.cdr, env)
        return apply(proc, args)
    else:
        raise TypeError("Cannot eval type " + type(expr).__name__)


def apply(proc, args):
    return proc(*args)
