import io

from pyme import types
from pyme.registry import builtin


class TextStreamPort(types.TextualPortBase):

    def __init__(self, stream, *, readable, writable):
        self._stream = stream
        self._readable = readable
        self._writable = writable
        self._peeked = None
        if readable and not stream.readable():
            raise ValueError("Stream must be readable if readable=True")
        if writable and not stream.writable():
            raise ValueError("Stream must be writable if writable=True")

    @classmethod
    def from_stream(cls, stream):
        return cls(stream,
                   readable=stream.readable(),
                   writable=stream.writable())

    def readable(self):
        return self._readable

    def writable(self):
        return self._writable

    def close(self):
        return self._stream.close()

    def is_open(self):
        return not self._stream.closed

    def read(self, size=-1):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        elif size == 0:
            return ""
        elif self._peeked is None:
            result = self._stream.read(size)
            if result == "":
                self._peeked = ""
                return types.Eof.instance
            else:
                return result
        elif self._peeked == "":
            return types.Eof.instance
        elif size < 0:
            result = self._peeked + self._stream.read(size)
            self._peeked = None
            return result
        elif size > len(self._peeked):
            result = self._peeked \
                + self._stream.read(size - len(self._peeked))
            self._peeked = None
            return result
        elif size == len(self._peeked):
            result = self._peeked
            self._peeked = None
            return result
        else: # size < len(self._peeked):
            result = self._peeked[:size]
            self._peeked = self._peeked[size:]
            return result

    def read_char(self):
        result = self.read(1)
        return result if isinstance(result, types.Eof) else types.Char(result)

    def peek_char(self):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        if self._peeked is None:
            self._peeked = self._stream.read(1)
        if self._peeked == "":
            return types.Eof.instance
        else:
            return types.Char(self._peeked)

    def readline(self):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        if self._peeked is None:
            result = self._stream.readline()
            if result == "":
                self._peeked = ""
                return types.Eof.instance
            else:
                return result
        elif self._peeked == "":
            return types.Eof.instance
        elif self._peeked == '\n':
            self._peeked = None
            return '\n'
        else:
            result = self._peeked + self._stream.readline()
            self._peeked = None
            return result

    def is_char_ready(self):
        raise NotImplementedError()

    def write(self, string):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        return self._stream.write(string)

    def newline(self):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        return self._stream.write("\n")

    def flush_output(self):
        self._stream.flush()

    def write_to(self, port):
        port.write("#<textual port ")
        if self.readable(): port.write("r")
        if self.writable(): port.write("w")
        port.write(" ")
        port.write(str(self._stream))
        port.write(">")


class BinaryStreamPort(types.BinaryPortBase):

    def __init__(self, stream, *, readable, writable):
        self._stream = stream
        self._readable = readable
        self._writable = writable
        if readable and not stream.readable():
            raise ValueError("Stream must be readable if readable=True")
        if writable and not stream.writable():
            raise ValueError("Stream must be writable if writable=True")

    @classmethod
    def from_stream(cls, stream):
        return cls(stream,
                   readable=stream.readable(),
                   writable=stream.writable())

    def readable(self):
        return self._readable

    def writable(self):
        return self._writable

    def close(self):
        return self._stream.close()

    def is_open(self):
        return not self._stream.closed

    def flush_output(self):
        self._stream.flush()

    def read_u8(self):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        result = self._stream.read(1)
        return result[0] if len(result) > 0 else types.Eof.instance

    def peek_u8(self):
        raise NotImplementedError()

    def is_u8_ready(self):
        raise NotImplementedError()

    def read_bytevector(self, k):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        if k < 0:
            raise ValueError("number of bytes to read should be non-negative")
        if k == 0:
            return bytearray()
        result = self._stream.read(k)
        return bytearray(result) if len(result) > 0 else types.Eof.instance

    def read_bytevector_to(self, bytevector, start=None, end=None):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        view = memoryview(bytevector)[slice(start, end)]
        if len(view) == 0:
            return 0
        result = self._stream.readinto(view)
        return result if result > 0 else types.Eof.instance

    def write_u8(self, byte):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        return self._stream.write(bytes([byte]))

    def write_bytevector(self, bytevector, start=None, end=None):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        view = memoryview(bytevector)[slice(start, end)]
        return self._stream.write(view)

    def write_to(self, port):
        port.write("#<binary port ")
        if self.readable(): port.write("r")
        if self.writable(): port.write("w")
        port.write(" ")
        port.write(str(self._stream))
        port.write(">")


@builtin("port-open?")
def port_open_p(obj):
    return obj.is_open()


@builtin("open-input-file")
def open_input_file(string):
    return TextStreamPort.from_stream(open(string, "rt"))


@builtin("open-binary-input-file")
def open_binary_input_file(string):
    return BinaryStreamPort.from_stream(open(string, "rb"))


@builtin("open-output-file")
def open_output_file(string):
    return TextStreamPort.from_stream(open(string, "wt"))


@builtin("open-binary-output-file")
def open_binary_output_file(string):
    return BinaryStreamPort.from_stream(open(string, "wb"))


@builtin("close-port")
def close_port(port):
    port.close()
    return False


@builtin("read-char")
def read_char(port):
    return port.read_char()


@builtin("peek-char")
def peek_char(port):
    return port.peek_char()


@builtin("read-line")
def read_line(port):
    return port.readline()


@builtin("read-string")
def read_string(port, k):
    return port.read(k)


@builtin("eof-object")
def eof_object():
    return types.Eof.instance


@builtin("char-ready?")
def char_ready_p(port):
    return port.is_char_ready()


