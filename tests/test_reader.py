import io
import unittest

from pyme import core, reader


class TestReader(unittest.TestCase):

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
        result = core.write(reader.read(io.StringIO(s)))
        self.assertEqual(result, "()")
