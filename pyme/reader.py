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

    def __init__(self, *, symbol_table, keyword_table):
        if symbol_table is None:
            raise ValueError("symbol_table is required, got None")
        if keyword_table is None:
            raise ValueError("keyword_table is required, got None")
        self._symbol_table = symbol_table
        self._keyword_table = keyword_table

    def _read_list(self, stream):
        result = []
        while True:
            item = self._read(stream)
            if isinstance(item, _RightBracket):
                return interop.scheme_list(result)
            elif base.eofp(item):
                raise ReaderError('Unexpected end of file.')
            else:
                result.append(item)

    def _read_string(self, stream):
        result = ""
        while True:
            item = stream.read(1)
            if item == "":
                raise ReaderError('Unexpected end of file.')
            elif item == '"':
                return result
            else:
                result += item

    def _slice_symbol_or_number(self, char, stream):
        result = char
        while True:
            position = stream.tell()
            item = stream.read(1)
            if item == "":
                return result
            elif not is_symbol_char(item):
                stream.seek(position)
                return result
            else:
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

    def _read_quoted(self, stream):
        quoted = self._read(stream)
        check_legal_object(quoted)
        if base.eofp(quoted):
            raise ReaderError('Unexpected end of file.')
        return interop.scheme_list([self._symbol_table["quote"], quoted])

    def _read_special(self, stream):
        char = stream.read(1)
        position = stream.tell()
        if char == "":
            raise ReaderError('Unexpected end of file.')
        elif char == 't':
            next_char = stream.read(1)
            if next_char != "" and is_symbol_char(next_char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char + next_char)
            stream.seek(position)
            return True
        elif char == 'f':
            next_char = stream.read(1)
            if next_char != "" and is_symbol_char(next_char):
                raise ReaderError("Invalid hash syntax: #"
                                  + char + next_char)
            stream.seek(position)
            return False
        else:
            raise ReaderError("Invalid hash syntax: #" + char)

    def _read(self, stream):
        while True:
            char = stream.read(1)
            if char == "":
                return base.eof()
            elif is_white(char):
                continue
            elif char == ";":
                stream.readline()
            elif char == "(":
                return self._read_list(stream)
            elif char == ")":
                return _RightBracket.instance
            elif char == '"':
                return self._read_string(stream)
            elif char == "'":
                return self._read_quoted(stream)
            elif char == "#":
                return self._read_special(stream)
            elif is_symbol_start_char(char):
                string = self._slice_symbol_or_number(char, stream)
                return self._get_symbol_or_number(string)
            else:
                raise ReaderError(f"Unexpected char: {char}.")

    def read(self, stream):
        result = self._read(stream)
        check_legal_object(result)
        return result
