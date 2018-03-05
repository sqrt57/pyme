import io
import unittest

from pyme import core, exceptions, ports, reader


class TestReader(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort(self.stream)

    def test_empty(self):
        in_port = ports.TextStreamPort(io.StringIO(""))
        result = reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_whitespace(self):
        in_port = ports.TextStreamPort(io.StringIO("\t \n"))
        result = reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_comment(self):
        in_port = ports.TextStreamPort(io.StringIO(" ;hello\n"))
        result = reader.read(in_port)
        self.assertIsInstance(result, core.Eof)

    def test_empty_list(self):
        in_port = ports.TextStreamPort(io.StringIO("()"))
        core.write_to(reader.read(in_port), self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_string(self):
        in_port = ports.TextStreamPort(io.StringIO('"abc"'))
        result = reader.read(in_port)
        self.assertEqual(result, "abc")


class TestReaderError(unittest.TestCase):

    def test_broken_list(self):
        in_port = ports.TextStreamPort(io.StringIO("("))
        with self.assertRaises(exceptions.ReaderError):
            reader.read(in_port)

    def test_broken_string(self):
        in_port = ports.TextStreamPort(io.StringIO('"q'))
        with self.assertRaises(exceptions.ReaderError):
            reader.read(in_port)

    def test_right_bracket(self):
        in_port = ports.TextStreamPort(io.StringIO(")"))
        with self.assertRaises(exceptions.ReaderError):
            reader.read(in_port)
