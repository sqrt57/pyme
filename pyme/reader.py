from pyme import base
from pyme import interop
from pyme.exceptions import ReaderError


class _RightBracket:
    pass


_RightBracket.instance = _RightBracket()


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


class Reader:

    def __init__(self, stream, *, symbol_table, keyword_table):
        if symbol_table is None:
            raise ValueError("symbol_table is required, got None")
        if keyword_table is None:
            raise ValueError("keyword_table is required, got None")
        self._stream = stream
        self._symbol_table = symbol_table
        self._keyword_table = keyword_table
        self._peeked = None

    def read_char(self):
        if self._peeked is None:
            return self._stream.read(1)
        else:
            result = self._peeked
            self._peeked = None
            return result

    def peek_char(self):
        if self._peeked is None:
            self._peeked = self._stream.read(1)
            return self._peeked
        else:
            return self._peeked

    def readline(self):
        peeked = self._peeked
        self._peeked = None
        if peeked is None:
            return self._stream.readline()
        elif peeked == "\n":
            return peeked
        else:
            return peeked + self._stream.readline()

    def _read_list(self):
        result = []
        while True:
            item = self._read()
            if isinstance(item, _RightBracket):
                return interop.scheme_list(result)
            elif base.eofp(item):
                raise ReaderError('Unexpected end of file.')
            else:
                result.append(item)

    def _read_string(self):
        result = ""
        while True:
            item = self.read_char()
            if item == "":
                raise ReaderError('Unexpected end of file.')
            elif item == '"':
                return result
            else:
                result += item

    def _slice_symbol_or_number(self, char):
        result = char
        while True:
            item = self.peek_char()
            if item == "":
                return result
            elif not is_symbol_char(item):
                return result
            else:
                self.read_char()
                result += item

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
        as_integer = self._parse_integer(string)
        if as_integer is not None:
            return as_integer
        if string[0] == ":":
            return self._keyword_table[string]
        return self._symbol_table[string]

    def _read_quoted(self):
        quoted = self._read()
        check_legal_object(quoted)
        if base.eofp(quoted):
            raise ReaderError('Unexpected end of file.')
        return interop.scheme_list([self._symbol_table["quote"], quoted])

    def _read_special(self):
        char = self.read_char()
        if char == "":
            raise ReaderError('Unexpected end of file.')
        elif char == 't':
            next_char = self.peek_char()
            if next_char != "" and is_symbol_char(next_char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char + next_char)
            return True
        elif char == 'f':
            next_char = self.peek_char()
            if next_char != "" and is_symbol_char(next_char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char + next_char)
            return False
        else:
            raise ReaderError("Invalid hash syntax: #" + char)

    def _read(self):
        while True:
            char = self.read_char()
            if char == "":
                return base.eof()
            elif is_white(char):
                continue
            elif char == ";":
                self.readline()
            elif char == "(":
                return self._read_list()
            elif char == ")":
                return _RightBracket.instance
            elif char == '"':
                return self._read_string()
            elif char == "'":
                return self._read_quoted()
            elif char == "#":
                return self._read_special()
            elif is_symbol_start_char(char):
                string = self._slice_symbol_or_number(char)
                return self._get_symbol_or_number(string)
            else:
                raise ReaderError(f"Unexpected char: {char}.")

    def read(self, stream=None):
        result = self._read()
        check_legal_object(result)
        return result
