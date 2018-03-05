from abc import ABC, abstractmethod
import numbers
import weakref


def write(obj):
    if '__write__' in dir(obj):
        return obj.__write__()
    elif obj is None:
        return "()"
    elif isinstance(obj, numbers.Integral):
        return repr(obj)
    elif isinstance(obj, str):
        return '"{}"'.format(obj)
    else:
        return "#<Python: {!r}>".format(obj)


def display(obj):
    if '__display__' in dir(obj):
        return obj.__display__()
    elif obj is None:
        return "()"
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
        if (isinstance(self.car, Symbol) and self.car.name == "quote"
                and isinstance(self.cdr, Pair) and self.cdr.cdr is None):
            return "'" + write(self.cdr.car)
        else:
            result = ["(", write(self.car)]
            cur = self.cdr
            while isinstance(cur, Pair):
                result.append(" ")
                result.append(write(cur.car))
                cur = cur.cdr
            if cur is not None:
                result.append(" . ")
                result.append(write(cur))
            result.append(")")
            return "".join(result)

    def __display__(self):
        if (isinstance(self.car, Symbol) and self.car.name == "quote"
                and isinstance(self.cdr, Pair) and self.cdr.cdr is None):
            return "'" + display(self.cdr.car)
        else:
            result = ["(", display(self.car)]
            cur = self.cdr
            while isinstance(cur, Pair):
                result.append(" ")
                result.append(display(cur.car))
                cur = cur.cdr
            if cur is not None:
                result.append(" . ")
                result.append(display(cur))
            result.append(")")
            return "".join(result)


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


class Eof:
    pass


class PortBase(ABC):

    @abstractmethod
    def readable(self):
        pass

    @abstractmethod
    def writable(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def close_input(self):
        pass

    @abstractmethod
    def close_output(self):
        pass

    @abstractmethod
    def is_input_open(self):
        pass

    @abstractmethod
    def is_output_open(self):
        pass


class TextualPortBase(PortBase):

    @abstractmethod
    def read(self, size=1):
        pass

    @abstractmethod
    def peek_char(self):
        pass

    @abstractmethod
    def readline(self):
        pass

    @abstractmethod
    def is_char_ready(self):
        pass

    @abstractmethod
    def write(self, string):
        pass

    @abstractmethod
    def newline(self):
        pass

    @abstractmethod
    def flush_output(self):
        pass
