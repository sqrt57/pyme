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

    def reader(self, stream):
        return reader.Reader(
            stream,
            symbol_table=types.symbol_table(),
                                    keyword_table=types.keyword_table())

    def test_empty(self):
        stream = io.StringIO("")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.eofp(result))

    def test_whitespace(self):
        stream = io.StringIO("\t \n")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.eofp(result))

    def test_comment(self):
        stream = io.StringIO(" ;hello\n")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.eofp(result))

    def test_empty_list(self):
        stream = io.StringIO("()")
        result = self.reader(stream).read(stream)
        write.write_to(result, self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_string(self):
        stream = io.StringIO('"abc"')
        result = self.reader(stream).read(stream)
        self.assertEqual(result, "abc")

    def test_symbol(self):
        stream = io.StringIO("abc")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_keyword(self):
        stream = io.StringIO(":abc")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.keywordp(result))
        self.assertEqual(result.name, ":abc")

    def test_symbol_space(self):
        stream = io.StringIO(" abc ")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_left_bracket(self):
        stream = io.StringIO("abc(")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_right_bracket(self):
        stream = io.StringIO("abc)")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_quote(self):
        stream = io.StringIO("abc'")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_double_quote(self):
        stream = io.StringIO('abc"')
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_symbol_semicolon(self):
        stream = io.StringIO("abc;")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "abc")

    def test_quote(self):
        stream = io.StringIO("' ( a b c )")
        result = self.reader(stream).read(stream)
        write.write_to(result, self.port)
        self.assertEqual(self.stream.getvalue(), "'(a b c)")

    def test_true(self):
        stream = io.StringIO("#t")
        result = self.reader(stream).read(stream)
        self.assertIs(result, True)

    def test_false(self):
        stream = io.StringIO("#f()")
        result = self.reader(stream).read(stream)
        self.assertIs(result, False)

    def test_symbol_with_digits(self):
        stream = io.StringIO("123abc")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "123abc")

    def test_num(self):
        stream = io.StringIO("123")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 123)

    def test_plus_num(self):
        stream = io.StringIO("+45")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 45)

    def test_minus_num(self):
        stream = io.StringIO("-23")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, -23)

    def test_hex_num(self):
        stream = io.StringIO("0x1aB")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 0x1ab)

    def test_upper_hex_num(self):
        stream = io.StringIO("0X1aB")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 0x1ab)

    def test_plus_hex_num(self):
        stream = io.StringIO("+0x1aB")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 0x1aB)

    def test_minus_hex_num(self):
        stream = io.StringIO("-0x1aB")
        result = self.reader(stream).read(stream)
        self.assertEqual(result, -0x1aB)

    def test_zero_num(self):
        stream = io.StringIO('0')
        result = self.reader(stream).read(stream)
        self.assertEqual(result, 0)

    def test_plus(self):
        stream = io.StringIO("+")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "+")

    def test_minus(self):
        stream = io.StringIO("-")
        result = self.reader(stream).read(stream)
        self.assertTrue(base.symbolp(result))
        self.assertEqual(result.name, "-")

    def test_symbols_eq(self):
        stream = io.StringIO("abc abc")
        stream_reader = self.reader(stream)
        result1 = stream_reader.read(stream)
        result2 = stream_reader.read(stream)
        self.assertIs(result1, result2)

    def test_quote_eq(self):
        stream = io.StringIO("quote 'abc")
        stream_reader = self.reader(stream)
        result1 = stream_reader.read(stream)
        result2 = stream_reader.read(stream)
        self.assertIs(result1, result2.car)


class TestReaderError(unittest.TestCase):

    def reader(self, stream):
        return reader.Reader(
            stream,
            symbol_table=types.symbol_table(),
                                    keyword_table=types.keyword_table())

    def test_broken_list(self):
        stream = io.StringIO("(")
        with self.assertRaises(exceptions.ReaderError):
            self.reader(stream).read(stream)

    def test_broken_string(self):
        stream = io.StringIO('"q')
        with self.assertRaises(exceptions.ReaderError):
            self.reader(stream).read(stream)

    def test_right_bracket(self):
        stream = io.StringIO(")")
        with self.assertRaises(exceptions.ReaderError):
            self.reader(stream).read(stream)
