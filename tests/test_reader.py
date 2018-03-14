import io
import unittest

from pyme import core, exceptions, ports, reader


class TestReader(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort(self.stream)
        self.reader = reader.Reader()

    def test_empty(self):
        in_port = ports.TextStreamPort(io.StringIO(""))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_whitespace(self):
        in_port = ports.TextStreamPort(io.StringIO("\t \n"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_comment(self):
        in_port = ports.TextStreamPort(io.StringIO(" ;hello\n"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_empty_list(self):
        in_port = ports.TextStreamPort(io.StringIO("()"))
        core.write_to(self.reader.read(in_port), self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_string(self):
        in_port = ports.TextStreamPort(io.StringIO('"abc"'))
        result = self.reader.read(in_port)
        self.assertEqual(result, "abc")

    def test_symbol(self):
        in_port = ports.TextStreamPort(io.StringIO("abc"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_space(self):
        in_port = ports.TextStreamPort(io.StringIO(" abc "))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_left_bracket(self):
        in_port = ports.TextStreamPort(io.StringIO("abc("))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_right_bracket(self):
        in_port = ports.TextStreamPort(io.StringIO("abc)"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_quote(self):
        in_port = ports.TextStreamPort(io.StringIO("abc'"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_double_quote(self):
        in_port = ports.TextStreamPort(io.StringIO('abc"'))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_symbol_semicolon(self):
        in_port = ports.TextStreamPort(io.StringIO("abc;"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "abc")

    def test_quote(self):
        in_port = ports.TextStreamPort(io.StringIO("' ( a b c )"))
        core.write_to(self.reader.read(in_port), self.port)
        self.assertEqual(self.stream.getvalue(), "'(a b c)")

    def test_true(self):
        in_port = ports.TextStreamPort(io.StringIO("#t"))
        result = self.reader.read(in_port)
        self.assertIs(result, True)

    def test_false(self):
        in_port = ports.TextStreamPort(io.StringIO("#f()"))
        result = self.reader.read(in_port)
        self.assertIs(result, False)

    def test_symbol_with_digits(self):
        in_port = ports.TextStreamPort(io.StringIO("123abc"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "123abc")

    def test_num(self):
        in_port = ports.TextStreamPort(io.StringIO("123"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 123)

    def test_plus_num(self):
        in_port = ports.TextStreamPort(io.StringIO("+45"))
        result = self.reader.read(in_port)
        self.assertEqual(result, 45)

    def test_minus_num(self):
        in_port = ports.TextStreamPort(io.StringIO("-23"))
        result = self.reader.read(in_port)
        self.assertEqual(result, -23)

    def test_zero_num(self):
        in_port = ports.TextStreamPort(io.StringIO('0'))
        result = self.reader.read(in_port)
        self.assertEqual(result, 0)

    def test_plus(self):
        in_port = ports.TextStreamPort(io.StringIO("+"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "+")

    def test_minus(self):
        in_port = ports.TextStreamPort(io.StringIO("-"))
        result = self.reader.read(in_port)
        self.assertIsInstance(result, core.Symbol)
        self.assertEqual(result.name, "-")


class TestReaderError(unittest.TestCase):

    def setUp(self):
        self.reader = reader.Reader()

    def test_broken_list(self):
        in_port = ports.TextStreamPort(io.StringIO("("))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_broken_string(self):
        in_port = ports.TextStreamPort(io.StringIO('"q'))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)

    def test_right_bracket(self):
        in_port = ports.TextStreamPort(io.StringIO(")"))
        with self.assertRaises(exceptions.ReaderError):
            self.reader.read(in_port)
