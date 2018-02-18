from .core import Pair

def scheme_list(lst, cdr=None):
    result = cdr
    for item in reversed(lst):
        result = Pair(item, result)
    return result
