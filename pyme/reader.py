from pyme import core, exceptions, interop


class _RightBracket:
    pass


_RightBracket.instance = _RightBracket()


def is_white(char):
    return char in ' \n\r\t'


def _read_list(port):
    result = []
    while True:
        item = _read(port)
        if isinstance(item, _RightBracket):
            return interop.scheme_list(result)
        elif isinstance(item, core.Eof):
            raise ReaderException('Unexpected end of file')
        else:
            result.append(item)


def _read(port):
    while True:
        char = port.peek_char()
        if isinstance(char, core.Eof):
            return char
        elif is_white(char):
            port.read(1)
        elif char == ';':
            port.readline()
        elif char == '(':
            port.read(1)
            return _read_list(port)
        elif char == ')':
            port.read(1)
            return _RightBracket.instance
        elif char == '"':
            port.read(1)
            return _read_string(port)
        elif char == "'":
            port.read(1)
            pass
        elif char == "#":
            port.read(1)
            pass
        else:
            return _read_symbol(port)


def read(port):
    result = _read(port)
    if result is _RightBracket:
        raise exceptions.ReaderError('Unexpected ")"')
    return result
