import io

from pyme import core


class TextStreamPort(core.TextualPortBase):

    def __init__(self, stream, *, readable=True, writable=True):
        self._stream = stream
        self._readable = readable
        self._writable = writable
        self._peeked = None
        if readable and not stream.readable():
            raise ValueError("Stream must be readable if readable=True")
        if writable and not stream.writable():
            raise ValueError("Stream must be writable if writable=True")

    def readable(self):
        return self._readable

    def writable(self):
        return self._writable

    def close(self):
        return self._stream.close()

    def close_input(self):
        if self._readable:
            return self._stream.close()

    def close_output(self):
        if self._writable:
            return self._stream.close()

    def is_input_open(self):
        return self._readable and not self._stream.closed()

    def is_output_open(self):
        return self._writable and not self._stream.closed()

    def read(self, size=-1):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        elif size == 0:
            return ""
        elif self._peeked is None:
            result = self._stream.read(size)
            if result == "":
                self._peeked = ""
                return core.Eof()
            else:
                return result
        elif self._peeked == '':
            return core.Eof()
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

    def peek_char(self):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        if self._peeked is None:
            self._peeked = self._stream.read(1)
        if self._peeked == "":
            return core.Eof()
        else:
            return self._peeked

    def readline(self):
        if not self._readable:
            raise io.UnsupportedOperation("not readable")
        if self._peeked is None:
            result = self._stream.readline()
            if result == "":
                self._peeked = ""
                return core.Eof()
            else:
                return result
        elif self._peeked == '':
            return core.Eof()
        elif self._peeked == '\n':
            self._peeked = None
            return '\n'
        else:
            result = self._peeked + self._stream.readline()
            self._peeked = None
            return result

    def is_char_ready(self):
        raise NotImplementedError()

    def write_string(self, string):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        return self._stream.write(string)

    def newline(self):
        if not self._writable:
            raise io.UnsupportedOperation("not writable")
        return self._stream.write("\n")

    def flush_output(self):
        self._stream.flush()
