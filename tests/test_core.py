import io
import unittest

from pyme import base, interop, ports, types, write

class TestCore(unittest.TestCase):

    def test_pair(self):
        pair = base.cons(1, 2)
        self.assertTrue(base.pairp(pair))
        self.assertEqual(pair.car, 1)
        self.assertEqual(pair.cdr, 2)
        pair.car = "hello"
        self.assertEqual(pair.car, "hello")

    def test_symbol_unique(self):
        store = types.SymbolTable()
        a = store['qwe']
        b = store['qwe']
        self.assertEqual(a, b)

    def test_scheme_list(self):
        x = interop.scheme_list([1, 2])
        self.assertTrue(base.pairp(x))
        self.assertEqual(x.car, 1)
        self.assertTrue(base.pairp(x.cdr))
        self.assertEqual(x.cdr.car, 2)
        self.assertIsNone(x.cdr.cdr)


class TestWrite(unittest.TestCase):

    def setUp(self):
        self.stream = io.StringIO()
        self.port = ports.TextStreamPort(self.stream)

    def test_write_pair(self):
        pair = base.cons(1, "qqq")
        write.write_to(pair, self.port)
        self.assertEqual(self.stream.getvalue(), '(1 . "qqq")')

    def test_display_pair(self):
        pair = base.cons(1, "qqq")
        write.display_to(pair, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 . qqq)")

    def test_write_list(self):
        obj = interop.scheme_list([1, 2, 3])
        write.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3)")

    def test_display_list(self):
        obj = interop.scheme_list([1, 2, 3])
        write.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3)")

    def test_write_improper_list(self):
        obj = interop.scheme_list([1, 2, 3], 4)
        write.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3 . 4)")

    def test_display_improper_list(self):
        obj = interop.scheme_list([1, 2, 3], 4)
        write.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "(1 2 3 . 4)")

    def test_write_empty_list(self):
        obj = interop.scheme_list([])
        write.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_display_empty_list(self):
        obj = interop.scheme_list([])
        write.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "()")

    def test_write_quote_list(self):
        obj = interop.scheme_list([
            types.Symbol("quote"),
            interop.scheme_list([1, 2], 3)
        ])
        write.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'(1 2 . 3)")

    def test_display_quote_list(self):
        obj = interop.scheme_list([
            types.Symbol("quote"),
            interop.scheme_list([1, 2], 3)
        ])
        write.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'(1 2 . 3)")

    def test_write_quote_string(self):
        obj = interop.scheme_list([
            types.Symbol("quote"),
            "abc",
        ])
        write.write_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'\"abc\"")

    def test_display_quote_string(self):
        obj = interop.scheme_list([
            types.Symbol("quote"),
            "abc"
        ])
        write.display_to(obj, self.port)
        self.assertEqual(self.stream.getvalue(), "'abc")
