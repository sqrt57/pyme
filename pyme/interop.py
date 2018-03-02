from pyme import core

def scheme_list(lst, cdr=None):
    result = cdr
    for item in reversed(lst):
        result = core.Pair(item, result)
    return result
