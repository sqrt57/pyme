import numbers
import operator
import sys

from pyme import exceptions
from pyme import types
from pyme.registry import builtin, builtin_with_interpreter
from pyme.interop import scheme_list


@builtin("pair?")
def pairp(obj):
    return isinstance(obj, types.Pair)


@builtin("null?")
def nullp(obj):
    return isinstance(obj, types.EmptyList)


def null():
    return types.EmptyList.instance


@builtin("list?")
def listp(obj):
    while pairp(obj):
        obj = obj.cdr
    return nullp(obj)


@builtin("eof?")
def eofp(obj):
    return isinstance(obj, types.Eof)


@builtin("symbol?")
def symbolp(obj):
    return isinstance(obj, types.Symbol)


@builtin("number?")
def numberp(obj):
    return isinstance(obj, numbers.Integral)


@builtin("string?")
def stringp(obj):
    return isinstance(obj, str)


@builtin("boolean?")
def booleanp(obj):
    return isinstance(obj, bool)


@builtin("not")
def is_false(obj):
    return obj is False


def is_true(obj):
    return obj is not False


@builtin("+")
def plus(*objs):
    return sum(objs)


@builtin("-")
def minus(z, *zs):
    if zs:
        return z - sum(zs)
    else:
        return -z


@builtin("*")
def multiply(*objs):
    result = 1
    for num in objs:
        result *= num
    return result


@builtin("/")
def divide(z, *zs):
    if zs:
        return z / multiply(*zs)
    else:
        return 1 / z


@builtin("<")
def lt(x, *rest):
    if len(rest) < 1:
        raise exceptions.EvalError("<: expected at least 2 arguments")
    for y in rest:
        if not x < y:
            return False
        x = y
    return True


@builtin(">")
def gt(x, *rest):
    if len(rest) < 1:
        raise exceptions.EvalError(">: expected at least 2 arguments")
    for y in rest:
        if not x > y:
            return False
        x = y
    return True


@builtin("<=")
def le(x, *rest):
    if len(rest) < 1:
        raise exceptions.EvalError("<=: expected at least 2 arguments")
    for y in rest:
        if not x <= y:
            return False
        x = y
    return True


@builtin(">=")
def ge(x, *rest):
    if len(rest) < 1:
        raise exceptions.EvalError(">=: expected at least 2 arguments")
    for y in rest:
        if not x >= y:
            return False
        x = y
    return True


@builtin("=")
def arithmetic_eq(x, *rest):
    if len(rest) < 1:
        raise exceptions.EvalError("=: expected at least 2 arguments")
    for y in rest:
        if x != y:
            return False
        x = y
    return True


@builtin("cons")
def cons(x, y):
    return types.Pair(x, y)


@builtin("car")
def car(pair):
    return pair.car


@builtin("cdr")
def cdr(pair):
    return pair.cdr


@builtin("list")
def list_(*args):
    return scheme_list(args)


builtin("eq?")(operator.is_)


@builtin("error")
def error(obj):
    raise exceptions.SchemeError(obj)


@builtin_with_interpreter("load")
def load(interpreter):
    def load(filename, env=None):
        interpreter.eval_file(filename, env)
    return load


builtin("exit")(sys.exit)
