from pyme import core


def pairp(obj):
    return obj is core.Pair


def nullp(obj):
    return obj is None


def listp(obj):
    while pairp(obj):
        obj = obj.cdr
    return nullp(obj)
