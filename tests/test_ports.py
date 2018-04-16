import io
import unittest

from pyme import base, ports


class TestReadPorts(unittest.TestCase):

    def test_read(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefgh"))
        result1 = port.read(3)
        result2 = port.read()
        result3 = port.read()
        self.assertEqual(result1, "abc")
        self.assertEqual(result2, "defgh")
        self.assertTrue(base.eofp(result3))

    def test_readline(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abc\n\ndef"))
        result1 = port.readline()
        result2 = port.readline()
        result3 = port.readline()
        result4 = port.readline()
        self.assertEqual(result1, "abc\n")
        self.assertEqual(result2, "\n")
        self.assertEqual(result3, "def")
        self.assertTrue(base.eofp(result4))

    def test_peek_read_n(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefg"))
        result1 = port.peek_char()
        result2 = port.read(3)
        self.assertEqual(result1, "a")
        self.assertEqual(result2, "abc")

    def test_peek_read_all(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefg"))
        result1 = port.peek_char()
        result2 = port.read()
        self.assertEqual(result1, "a")
        self.assertEqual(result2, "abcdefg")

    def test_peek_read_eof(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefg"))
        port.read()
        result1 = port.peek_char()
        result2 = port.read()
        self.assertTrue(base.eofp(result1))
        self.assertTrue(base.eofp(result2))

    def test_peek_read_read(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefg"))
        result1 = port.peek_char()
        result2 = port.read(3)
        result3 = port.read(3)
        self.assertEqual(result1, "a")
        self.assertEqual(result2, "abc")
        self.assertEqual(result3, "def")

    def test_peek_read_peak_read(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abcdefg"))
        result1 = port.peek_char()
        result2 = port.read(3)
        result3 = port.peek_char()
        result4 = port.read(3)
        self.assertEqual(result1, "a")
        self.assertEqual(result2, "abc")
        self.assertEqual(result3, "d")
        self.assertEqual(result4, "def")

    def test_peek_readline(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("abc\ndef\ngh"))
        result1 = port.peek_char()
        result2 = port.readline()
        result3 = port.readline()
        self.assertEqual(result1, "a")
        self.assertEqual(result2, "abc\n")
        self.assertEqual(result3, "def\n")

    def test_peek_readline_empty(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("\nabc\ndef\ngh"))
        result1 = port.peek_char()
        result2 = port.readline()
        result3 = port.readline()
        self.assertEqual(result1, "\n")
        self.assertEqual(result2, "\n")
        self.assertEqual(result3, "abc\n")

    def test_readline_peek_readline_eof(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("\nabc\ndef\ngh"))
        port.read()
        result1 = port.readline()
        result2 = port.peek_char()
        result3 = port.readline()
        self.assertTrue(base.eofp(result1))
        self.assertTrue(base.eofp(result2))
        self.assertTrue(base.eofp(result3))

    def test_peek_readline_peek_eof(self):
        port = ports.TextStreamPort.from_stream(io.StringIO("\nabc\ndef\ngh"))
        port.read()
        result1 = port.peek_char()
        result2 = port.readline()
        result3 = port.peek_char()
        self.assertTrue(base.eofp(result1))
        self.assertTrue(base.eofp(result2))
        self.assertTrue(base.eofp(result3))


class TestWritePorts(unittest.TestCase):

    def test_write(self):
        stream = io.StringIO()
        port = ports.TextStreamPort.from_stream(stream)
        port.write("abc")
        self.assertEqual(stream.getvalue(), "abc")

    def test_newline(self):
        stream = io.StringIO()
        port = ports.TextStreamPort.from_stream(stream)
        port.newline()
        self.assertEqual(stream.getvalue(), "\n")
