import numbers
import weakref


def write(obj):
    if '__write__' in dir(obj):
        return obj.__write__()
    elif isinstance(obj, numbers.Integral):
        return repr(obj)
    elif isinstance(obj, str):
        return '"{}"'.format(obj)
    else:
        return "#<Python: {!r}>".format(obj)


def display(obj):
    if '__display__' in dir(obj):
        return obj.__display__()
    elif isinstance(obj, numbers.Integral):
        return str(obj)
    elif isinstance(obj, str):
        return str(obj)
    else:
        return write(obj)


class Pair:

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __write__(self):
        return "({} . {})".format(write(self.car), write(self.cdr))

    def __display__(self):
        return "({} . {})".format(display(self.car), display(self.cdr))


class SymbolStore:

    def __init__(self):
        self._symbols = weakref.WeakValueDictionary()

    def __getitem__(self, key):
        result = self._symbols.get(key)
        if result is None:
            result = Symbol(key)
            self._symbols[key] = result
        return result


class Symbol:

    def __init__(self, name):
        self.name = name

    def __write__(self):
        return self.name

    def __display__(self):
        return self.name
