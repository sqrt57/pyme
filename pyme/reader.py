from pyme import exceptions, interop, base


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


class Reader:

    def __init__(self, *, symbol_table):
        if symbol_table is None:
            raise TypeError("symbol_table is required, got None")
        self._symbol_table = symbol_table

    def _read_list(self, port):
        result = []
        while True:
            item = self._read(port)
            if isinstance(item, _RightBracket):
                return interop.scheme_list(result)
            elif base.eofp(item):
                raise exceptions.ReaderError('Unexpected end of file.')
            else:
                result.append(item)

    def _read_string(self, port):
        result = ""
        while True:
            item = port.peek_char()
            if base.eofp(item):
                raise exceptions.ReaderError('Unexpected end of file.')
            elif item == '"':
                port.read(1)
                return result
            else:
                port.read(1)
                result += item

    def _slice_symbol_or_number(self, port):
        result = ""
        while True:
            item = port.peek_char()
            if base.eofp(item) or not is_symbol_char(item):
                return result
            else:
                port.read(1)
                result += item

    def  _parse_integer(self, string):
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

    def _get_symbol_or_number(self, string):
        if string == ".":
            raise exceptions.ReaderError("Illegal use of `.'")
        as_integer = self._parse_integer(string)
        if as_integer is not None:
            return as_integer
        return self._symbol_table[string]

    def _read_quoted(self, port):
        quoted = self._read(port)
        if isinstance(quoted, _RightBracket):
            raise exceptions.ReaderError('Unexpected ")".')
        if base.eofp(quoted):
            raise exceptions.ReaderError('Unexpected end of file.')
        return interop.scheme_list([self._symbol_table["quote"], quoted])

    def _read_special(self, port):
        char = port.peek_char()
        if base.eofp(char):
            raise exceptions.ReaderError('Unexpected end of file.')
        elif char == 't':
            port.read(1)
            next_char = port.peek_char()
            if not base.eofp(next_char) and is_symbol_char(next_char):
                raise exceptions.ReaderError("Invalid hash syntax: #"
                                             + char + next_char)
            return True
        elif char == 'f':
            port.read(1)
            next_char = port.peek_char()
            if not base.eofp(next_char) and is_symbol_char(next_char):
                raise exceptions.ReaderError("Invalid hash syntax: #"
                                             + char + next_char)
            return False
        else:
            raise exceptions.ReaderError("Invalid hash syntax: #" + char)

    def _read(self, port):
        while True:
            char = port.peek_char()
            if base.eofp(char):
                return char
            elif is_white(char):
                port.read(1)
            elif char == ';':
                port.readline()
            elif char == '(':
                port.read(1)
                return self._read_list(port)
            elif char == ')':
                port.read(1)
                return _RightBracket.instance
            elif char == '"':
                port.read(1)
                return self._read_string(port)
            elif char == "'":
                port.read(1)
                return self._read_quoted(port)
            elif char == "#":
                port.read(1)
                return self._read_special(port)
            else:
                string = self._slice_symbol_or_number(port)
                return self._get_symbol_or_number(string)

    def read(self, port):
        result = self._read(port)
        if isinstance(result, _RightBracket):
            raise exceptions.ReaderError('Unexpected ")".')
        return result
