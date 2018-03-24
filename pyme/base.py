import numbers

from pyme import types


def pairp(obj):
    return isinstance(obj, types.Pair)


def nullp(obj):
    return obj is None


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


def plus(*objs):
    return sum(objs)


def cons(x, y):
    return types.Pair(x, y)
