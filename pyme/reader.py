from pyme import core, exceptions, interop


class _RightBracket:
    pass


_RightBracket.instance = _RightBracket()


def is_white(char):
    return char in " \n\r\t"


def is_symbol_char(char):
    return not char in "'\"(); \n\r\t"


char_to_digit = {
    '0': 0,
    '1': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
}


def to_digit(char):
    return char_to_digit.get(char)


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


def _slice_symbol_or_number(port):
    result = ""
    while True:
        item = port.peek_char()
        if core.is_eof(item) or not is_symbol_char(item):
            return result
        else:
            port.read(1)
            result += item


def  _parse_integer(string):
    sign = 1
    if string[0] == "+":
        string = string[1:]
    elif string[0] == "-":
        sign = -1
        string = string[1:]
    if len(string) == 0: return None
    result = 0
    for char in string:
        digit = to_digit(char)
        if digit is None: return None
        result = result*10 + digit
    return sign * result


def _get_symbol_or_number(string):
    if string == ".":
        raise exceptions.ReaderError("Illegal use of `.'")
    as_integer = _parse_integer(string)
    if as_integer is not None:
        return as_integer
    return core.Symbol(string)


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
            string = _slice_symbol_or_number(port)
            return _get_symbol_or_number(string)


def read(port):
    result = _read(port)
    if isinstance(result, _RightBracket):
        raise exceptions.ReaderError('Unexpected ")".')
    return result
