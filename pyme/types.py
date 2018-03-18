from abc import ABC, abstractmethod
import weakref

from pyme import exceptions, write


class Pair:

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def write_to(self, port):
        if (isinstance(self.car, Symbol) and self.car.name == "quote"
                and isinstance(self.cdr, Pair) and self.cdr.cdr is None):
            port.write("'")
            write.write_to(self.cdr.car, port)
        else:
            port.write("(")
            write.write_to(self.car, port)
            cur = self.cdr
            while isinstance(cur, Pair):
                port.write(" ")
                write.write_to(cur.car, port)
                cur = cur.cdr
            if cur is not None:
                port.write(" . ")
                write.write_to(cur, port)
            port.write(")")

    def display_to(self, port):
        if (isinstance(self.car, Symbol) and self.car.name == "quote"
                and isinstance(self.cdr, Pair) and self.cdr.cdr is None):
            port.write("'")
            write.display_to(self.cdr.car, port)
        else:
            port.write("(")
            write.display_to(self.car, port)
            cur = self.cdr
            while isinstance(cur, Pair):
                port.write(" ")
                write.display_to(cur.car, port)
                cur = cur.cdr
            if cur is not None:
                port.write(" . ")
                write.display_to(cur, port)
            port.write(")")


class SymbolTable:

    def __init__(self):
        self._symbols = weakref.WeakValueDictionary()

    def __getitem__(self, key):
        result = self._symbols.get(key)
        if result is None:
            result = Symbol(key)
            self._symbols[key] = result
        return result


class Symbol:

    __slots__ = ["__weakref__", "_name"]

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def write_to(self, port):
        port.write(self.name)


class Environment:

    __slots__ = ["parent", "bindings"]

    def __init__(self, *, parent=None, bindings=None):
        self.parent = parent
        self.bindings = {} if bindings is None else bindings

    def __getitem__(self, index):
        if index in self.bindings:
            return self.bindings[index]
        else:
            raise exceptions.IdentifierNotBoundError(str(index))


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
