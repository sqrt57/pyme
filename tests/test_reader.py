import io
import unittest

from pyme import base
from pyme import exceptions
from pyme import interop
from pyme import ports
from pyme import reader
from pyme import types
from pyme import write


class TestReader(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort.from_stream(self.stream)
        self.reader = reader.Reader(symbol_table=types.symbol_table(),
                                    keyword_table=types.keyword_table())

    def test_empty(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(""))
        result = self.reader.read(in_port)
        self.assertTrue(base.eofp(result))

    def test_whitespace(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("\t \n"))
        result = self.reader.read(in_port)
        self.assertTrue(base.eofp(result))

    def test_comment(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(" ;hello\n"))
        result = self.reader.read(in_port)
        self.assertTrue(base.eofp(result))

    def test_empty_list(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("()"))
        write.write_to(self.reader.read(in_port), self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_string(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO('"abc"'))
        result = self.reader.read(in_port)
        self.assertEqual(result, "abc")

    def test_symbol(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_keyword(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(":abc"))
        result = self.reader.read(in_port)
        self.assertTrue(base.keywordp(result))
        self.assertEqual(result.name, ":abc")

    def test_symbol_space(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(" abc "))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_left_bracket(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc("))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_right_bracket(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc)"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_quote(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc'"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_double_quote(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO('abc"'))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_semicolon(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc;"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_quote(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("' ( a b c )"))
        write.write_to(self.reader.read(in_port), self.port)
        self.assertEqual(self.stream.getvalue(), "'(a b c)")

    def test_true(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("#t"))
        result = self.reader.read(in_port)
        self.assertIs(result, True)

    def test_false(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("#f()"))
        result = self.reader.read(in_port)
        self.assertIs(result, False)

    def test_symbol_with_digits(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("123abc"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "123abc")

    def test_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("123"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 123)

    def test_plus_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("+45"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 45)

    def test_minus_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("-23"))
        result = self.reader.read(in_port)
        self.assertEqual(result, -23)

    def test_hex_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("0x1aB"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 0x1ab)

    def test_upper_hex_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("0X1aB"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 0x1ab)

    def test_plus_hex_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("+0x1aB"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 0x1aB)

    def test_minus_hex_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("-0x1aB"))
        result = self.reader.read(in_port)
        self.assertEqual(result, -0x1aB)

    def test_zero_num(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO('0'))
        result = self.reader.read(in_port)
        self.assertEqual(result, 0)

    def test_plus(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("+"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "+")

    def test_minus(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("-"))
        result = self.reader.read(in_port)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "-")

    def test_symbols_eq(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("abc abc"))
        result1 = self.reader.read(in_port)
        result2 = self.reader.read(in_port)
        self.assertIs(result1, result2)

    def test_quote_eq(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("quote 'abc"))
        result1 = self.reader.read(in_port)
        result2 = self.reader.read(in_port)
        self.assertIs(result1, result2.car)

    def test_dot_list(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("(1 . 2)"))
        result = self.reader.read(in_port)
        self.assertEqual(interop.from_scheme_list(result), ([1], 2))

    def test_empty_dot_list(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("(. 3)"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 3)

    def test_list_dot_list(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("((1 . 2))"))
        result = self.reader.read(in_port)
        inner, rest = interop.from_scheme_list(result)
        self.assertEqual(len(inner), 1)
        # import pdb; pdb.set_trace()
        # self.assertTrue(base.listp(inner[0]))
        self.assertTrue(base.nullp(rest))
        self.assertEqual(interop.from_scheme_list(inner[0]), ([1], 2))


class TestReaderError(unittest.TestCase):

    def setUp(self):
        self.reader = reader.Reader(symbol_table=types.symbol_table(),
                                    keyword_table=types.keyword_table())

    def test_broken_list(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("("))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_broken_string(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO('"q'))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_right_bracket(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(")"))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_dot(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("."))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_quote_dot(self):
        in_port = ports.TextStreamPort.from_stream(io.StringIO("'."))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)
