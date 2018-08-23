from abc import ABC, abstractmethod
import weakref

from pyme import exceptions, write


class EmptyList:
    pass


EmptyList.instance = EmptyList()


class Pair:

    def __init__(self, car, cdr):
        if not isinstance(cdr, Pair) and not isinstance(cdr, EmptyList):
            raise ValueError("cdr of pair should be a pair or empty list")
        self.car = car
        self.cdr = cdr

    def write_to(self, port):
        return write.write_pair_to(self, port)

    def display_to(self, port):
        return write.display_pair_to(self, port)


class Char:

    __slots__ = ["_char"]

    def __init__(self, char):
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("char should be a string of length 1")
        self._char = char

    @property
    def char(self):
        return self._char

    def write_to(self, port):
        port.write("#\\")
        port.write(self.char)

    def display_to(self, port):
        port.write(self.char)




class Symbol:

    __slots__ = ["__weakref__", "_name"]

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def write_to(self, port):
        port.write(self.name)

    def __repr__(self):
        return f"<Symbol {self.name}>"


class Keyword:

    __slots__ = ["__weakref__", "_name"]

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name

    def write_to(self, port):
        port.write(self.name)

    def __repr__(self):
        return f"<Keyword {self.name}>"


class SymbolTable:

    def __init__(self, constructor):
        self._symbols = weakref.WeakValueDictionary()
        self._constructor = constructor

    def __getitem__(self, key):
        result = self._symbols.get(key)
        if result is None:
            result = self._constructor(key)
            self._symbols[key] = result
        return result


def symbol_table():
    return SymbolTable(Symbol)


def keyword_table():
    return SymbolTable(Keyword)


class Environment:

    __slots__ = ["parent", "bindings"]

    def __init__(self, *, parent=None, bindings=None):
        self.parent = parent
        self.bindings = {} if bindings is None else bindings

    def __getitem__(self, index):
        env = self
        while env is not None:
            if index in env.bindings:
                return env.bindings[index]
            env = env.parent
        raise exceptions.IdentifierNotBoundError(str(index))

    def __contains__(self, index):
        env = self
        while env is not None:
            if index in env.bindings:
                return True
            env = env.parent
        return False

    def get(self, index, default=None):
        env = self
        while env is not None:
            if index in env.bindings:
                return env.bindings[index]
            env = env.parent
        return default

    def define(self, index, value):
        self.bindings[index] = value

    def set_(self, index, value):
        env = self
        while env is not None:
            if index in env.bindings:
                env.bindings[index] = value
                return
            env = env.parent
        raise exceptions.IdentifierNotBoundError(str(index))

    def write_to(self, port):
        port.write(f"#<environment:{id(self)}>")


class Eof:

    def write_to(self, port):
        port.write("#<eof>")


Eof.instance = Eof()


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
    def is_open(self):
        pass

    @abstractmethod
    def flush_output(self):
        pass


class TextualPortBase(PortBase):

    @abstractmethod
    def read(self, size=1):
        pass

    @abstractmethod
    def read_char(self):
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


class BinaryPortBase(PortBase):

    @abstractmethod
    def read_u8(self):
        pass

    @abstractmethod
    def peek_u8(self):
        pass

    @abstractmethod
    def is_u8_ready(self):
        pass

    @abstractmethod
    def read_bytevector(self, k):
        pass

    @abstractmethod
    def read_bytevector_to(self, bytevector, start=None, end=None):
        pass

    @abstractmethod
    def write_u8(self, byte):
        pass

    @abstractmethod
    def write_bytevector(self, bytevector, start=None, end=None):
        pass
