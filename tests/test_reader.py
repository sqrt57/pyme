import io
import unittest

from pyme import core, ports, reader


class TestReader(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort(self.stream)

    def test_empty(self):
        port = io.StringIO("")
        result = reader.read(port)
        self.assertIsInstance(result, core.Eof)

    def test_whitespace(self):
        port = io.StringIO("\t \n")
        result = reader.read(port)
        self.assertIsInstance(result, core.Eof)

    def test_comment(self):
        port = io.StringIO(" ;hello\n")
        result = reader.read(port)
        self.assertIsInstance(result, core.Eof)

    def test_empty_list(self):
        s = "()"
        core.write_to(reader.read(io.StringIO(s)), self.port)
        self.assertEqual(self.stream.getvalue(), "()")
