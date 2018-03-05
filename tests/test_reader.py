import io
import unittest

from pyme import core, ports, reader


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
