import io
import unittest

from pyme import core, ports


class TestPorts(unittest.TestCase):

    def test_read(self):
        port = ports.TextStreamPort(io.StringIO("abcdefgh"))
        result1 = port.read(3)
        result2 = port.read()
        result3 = port.read()
        self.assertEqual(result1, "abc")
        self.assertEqual(result2, "defgh")
        self.assertIsInstance(result3, core.Eof)

    def test_readline(self):
        port = ports.TextStreamPort(io.StringIO("abc\n\ndef"))
        result1 = port.readline()
        result2 = port.readline()
        result3 = port.readline()
        result4 = port.readline()
        self.assertEqual(result1, "abc\n")
        self.assertEqual(result2, "\n")
        self.assertEqual(result3, "def")
        self.assertIsInstance(result4, core.Eof)
