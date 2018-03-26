import numbers

from pyme import types


def pairp(obj):
    return isinstance(obj, types.Pair)


def nullp(obj):
    return isinstance(obj, types.EmptyList)


def null():
    return types.EmptyList.instance


def listp(obj):
    while pairp(obj):
        obj = obj.cdr
    return nullp(obj)


def eofp(obj):
    return isinstance(obj, types.Eof)


def symbolp(obj):
    return isinstance(obj, types.Symbol)


def numberp(obj):
    return isinstance(obj, numbers.Integral)


def stringp(obj):
    return isinstance(obj, str)


def booleanp(obj):
    return isinstance(obj, bool)


def is_false(obj):
    return obj is False


def is_true(obj):
    return obj is not False


def plus(*objs):
    return sum(objs)


def minus(z, *zs):
    if zs:
        return z - sum(zs)
    else:
        return -z


def cons(x, y):
    return types.Pair(x, y)
