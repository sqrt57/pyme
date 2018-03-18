from pyme import core


def pairp(obj):
    return isinstance(obj, core.Pair)


def nullp(obj):
    return obj is None


def listp(obj):
    while pairp(obj):
        obj = obj.cdr
    return nullp(obj)


def plus(*objs):
    return sum(objs)
