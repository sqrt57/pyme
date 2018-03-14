import io
import unittest

from pyme import core, interop, ports

class TestCore(unittest.TestCase):

    def test_pair(self):
        pair = core.Pair(1, 2)
        self.assertEqual(pair.car, 1)
        self.assertEqual(pair.cdr, 2)
        pair.car = "hello"
        self.assertEqual(pair.car, "hello")

    def test_symbol_unique(self):
        store = core.SymbolTable()
        a = store['qwe']
        b = store['qwe']
        self.assertEqual(a, b)

    def test_scheme_list(self):
        x = interop.scheme_list([1, 2])
        self.assertIsInstance(x, core.Pair)
        self.assertEqual(x.car, 1)
        self.assertIsInstance(x.cdr, core.Pair)
        self.assertEqual(x.cdr.car, 2)
        self.assertIsNone(x.cdr.cdr)


class TestWrite(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort(self.stream)

    def test_write_pair(self):
        pair = core.Pair(1, "qqq")
        core.write_to(pair, self.port)
        self.assertEqual(self.stream.getvalue(), '(1 . "qqq")')

    def test_display_pair(self):
        pair = core.Pair(1, "qqq")
        core.display_to(pair, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 . qqq)")

    def test_write_list(self):
        obj = interop.scheme_list([1, 2, 3])
        core.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3)")

    def test_display_list(self):
        obj = interop.scheme_list([1, 2, 3])
        core.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3)")

    def test_write_improper_list(self):
        obj = interop.scheme_list([1, 2, 3], 4)
        core.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3 . 4)")

    def test_display_improper_list(self):
        obj = interop.scheme_list([1, 2, 3], 4)
        core.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3 . 4)")

    def test_write_empty_list(self):
        obj = interop.scheme_list([])
        core.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_display_empty_list(self):
        obj = interop.scheme_list([])
        core.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_write_quote_list(self):
        obj = interop.scheme_list([
            core.Symbol("quote"),
            interop.scheme_list([1, 2], 3)
        ])
        core.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'(1 2 . 3)")

    def test_display_quote_list(self):
        obj = interop.scheme_list([
            core.Symbol("quote"),
            interop.scheme_list([1, 2], 3)
        ])
        core.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'(1 2 . 3)")

    def test_write_quote_string(self):
        obj = interop.scheme_list([
            core.Symbol("quote"),
            "abc",
        ])
        core.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'\"abc\"")

    def test_display_quote_string(self):
        obj = interop.scheme_list([
            core.Symbol("quote"),
            "abc"
        ])
        core.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'abc")
