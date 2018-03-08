from pyme import core, exceptions, interop


class _RightBracket:
    pass


_RightBracket.instance = _RightBracket()


def is_white(char):
    return char in " \n\r\t"


def is_symbol_char(char):
    return not char in "'\"(); \n\r\t"


def _read_list(port):
    result = []
    while True:
        item = _read(port)
        if isinstance(item, _RightBracket):
            return interop.scheme_list(result)
        elif core.is_eof(item):
            raise exceptions.ReaderError('Unexpected end of file.')
        else:
            result.append(item)


def _read_string(port):
    result = ""
    while True:
        item = port.peek_char()
        if core.is_eof(item):
            raise exceptions.ReaderError('Unexpected end of file.')
        elif item == '"':
            port.read(1)
            return result
        else:
            port.read(1)
            result += item


def _read_symbol(port):
    result = ""
    while True:
        item = port.peek_char()
        if core.is_eof(item) or not is_symbol_char(item):
            return core.Symbol(result)
        else:
            port.read(1)
            result += item


def _read_quoted(port):
    quoted = _read(port)
    if isinstance(quoted, _RightBracket):
        raise exceptions.ReaderError('Unexpected ")".')
    if isinstance(quoted, core.Eof):
        raise exceptions.ReaderError('Unexpected end of file.')
    return interop.scheme_list([core.Symbol("quote"), quoted])


def _read_special(port):
    char = port.peek_char()
    if isinstance(char, core.Eof):
        raise exceptions.ReaderError('Unexpected end of file.')
    elif char == 't':
        port.read(1)
        next_char = port.peek_char()
        if not core.is_eof(next_char) and is_symbol_char(next_char):
            raise exceptions.ReaderError("Invalid hash syntax: #"
                                         + char + next_char)
        return True
    elif char == 'f':
        port.read(1)
        next_char = port.peek_char()
        if not core.is_eof(next_char) and is_symbol_char(next_char):
            raise exceptions.ReaderError("Invalid hash syntax: #"
                                         + char + next_char)
        return False
    else:
        raise exceptions.ReaderError("Invalid hash syntax: #" + char)


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
            return _read_quoted(port)
        elif char == "#":
            port.read(1)
            return _read_special(port)
        else:
            return _read_symbol(port)


def read(port):
    result = _read(port)
    if isinstance(result, _RightBracket):
        raise exceptions.ReaderError('Unexpected ")".')
    return result
