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
        char = port.read(1)
        if char == '':
            return core.Eof()
        elif is_white(char):
            pass
        elif char == ';':
            port.readline()
        elif char == '(':
            return _read_list(port)
        elif char == ')':
            return _RightBracket.instance
        elif char == '"':
            return _read_string(port)
        elif char == "'":
            pass
        elif char == "#":
            pass
        else:
            return _read_symbol(port)


def read(port):
    result = _read(port)
    if result is _RightBracket:
        raise exceptions.ReaderError('Unexpected ")"')
    return result
