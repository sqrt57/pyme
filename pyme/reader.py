from pyme import base
from pyme import interop
from pyme.exceptions import ReaderError


class _RightBracket:
    pass


_RightBracket.instance = _RightBracket()


class _Dot:
    pass


_Dot.instance = _Dot()


def is_white(char):
    return char in " \n\r\t"


symbol_special_start_chars = frozenset("!$%&*+-./:<=>?@^_~")


symbol_special_chars = symbol_special_start_chars.union("#")


def is_symbol_start_char(char):
    return char.isalnum() or char in symbol_special_start_chars


def is_symbol_char(char):
    return char.isalnum() or char in symbol_special_chars


char_to_decimal_digit = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
}


char_to_hex_digit = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
    '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
}


def to_decimal_digit(char):
    return char_to_decimal_digit.get(char)


def to_hex_digit(char):
    return char_to_hex_digit.get(char)


def check_legal_object(obj):
    if isinstance(obj, _RightBracket):
        raise ReaderError('Unexpected ")".')
    if isinstance(obj, _Dot):
        raise ReaderError("Illegal use of `.'")


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
            elif isinstance(item, _Dot):
                cdr = self._read(port)
                check_legal_object(cdr)
                right_bracket = self._read(port)
                if not isinstance(right_bracket, _RightBracket):
                    raise ReaderError('")" expected')
                return interop.scheme_list(result, cdr=cdr)
            elif base.eofp(item):
                raise ReaderError('Unexpected end of file.')
            else:
                result.append(item)

    def _read_string(self, port):
        result = ""
        while True:
            item = port.peek_char()
            if base.eofp(item):
                raise ReaderError('Unexpected end of file.')
            elif item.char == '"':
                port.read_char()
                return result
            else:
                port.read_char()
                result += item.char

    def _slice_symbol_or_number(self, port):
        result = ""
        while True:
            item = port.peek_char()
            if base.eofp(item) or not is_symbol_char(item.char):
                return result
            else:
                port.read_char()
                result += item.char

    def _parse_integer(self, string):
        sign = 1
        base = 10
        to_digit = to_decimal_digit

        if string[0] == "+":
            string = string[1:]
        elif string[0] == "-":
            sign = -1
            string = string[1:]

        if string[:2] == "0x" or string[:2] == "0X":
            to_digit = to_hex_digit
            base = 16
            string = string[2:]

        if len(string) == 0:
            return None

        result = 0
        for char in string:
            digit = to_digit(char)
            if digit is None:
                return None
            result = result * base + digit

        return sign * result

    def _get_symbol_or_number(self, string):
        if string == ".":
            return _Dot.instance
        as_integer = self._parse_integer(string)
        if as_integer is not None:
            return as_integer
        return self._symbol_table[string]

    def _read_quoted(self, port):
        quoted = self._read(port)
        check_legal_object(quoted)
        if base.eofp(quoted):
            raise ReaderError('Unexpected end of file.')
        return interop.scheme_list([self._symbol_table["quote"], quoted])

    def _read_special(self, port):
        char = port.peek_char()
        if base.eofp(char):
            raise ReaderError('Unexpected end of file.')
        elif char.char == 't':
            port.read_char()
            next_char = port.peek_char()
            if not base.eofp(next_char) and is_symbol_char(next_char.char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char.char + next_char.char)
            return True
        elif char.char == 'f':
            port.read_char()
            next_char = port.peek_char()
            if not base.eofp(next_char) and is_symbol_char(next_char.char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char.char + next_char.char)
            return False
        else:
            raise ReaderError("Invalid hash syntax: #" + char.char)

    def _read(self, port):
        while True:
            char = port.peek_char()
            if base.eofp(char):
                return char
            elif is_white(char.char):
                port.read_char()
            elif char.char == ";":
                port.readline()
            elif char.char == "(":
                port.read_char()
                return self._read_list(port)
            elif char.char == ")":
                port.read_char()
                return _RightBracket.instance
            elif char.char == '"':
                port.read_char()
                return self._read_string(port)
            elif char.char == "'":
                port.read_char()
                return self._read_quoted(port)
            elif char.char == "#":
                port.read_char()
                return self._read_special(port)
            elif is_symbol_start_char(char.char):
                string = self._slice_symbol_or_number(port)
                return self._get_symbol_or_number(string)
            else:
                port.read_char()
                raise ReaderError(f"Unexpected char: {char.char}.")

    def read(self, port):
        result = self._read(port)
        check_legal_object(result)
        return result
