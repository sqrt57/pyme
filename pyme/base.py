import numbers

from pyme.registry import builtin
from pyme import types


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


@builtin("cons")
def cons(x, y):
    return types.Pair(x, y)
