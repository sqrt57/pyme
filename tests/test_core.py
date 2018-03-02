import unittest

from pyme import core, interop

class TestCore(unittest.TestCase):

    def test_pair(self):
        pair = core.Pair(1, 2)
        self.assertEqual(pair.car, 1)
        self.assertEqual(pair.cdr, 2)
        pair.car = "hello"
        self.assertEqual(pair.car, "hello")

    def test_symbol_unique(self):
        store = core.SymbolStore()
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

    def test_write_pair(self):
        pair = core.Pair(1, "qqq")
        self.assertEqual(core.write(pair), '(1 . "qqq")')

    def test_display_pair(self):
        pair = core.Pair(1, "qqq")
        self.assertEqual(core.display(pair), '(1 . qqq)')

    def test_list(self):
        obj = interop.scheme_list([1, 2, 3])
        self.assertEqual(core.write(obj), "(1 2 3)")
        self.assertEqual(core.display(obj), "(1 2 3)")

    def test_improper_list(self):
        obj = interop.scheme_list([1, 2, 3], 4)
        self.assertEqual(core.write(obj), "(1 2 3 . 4)")
        self.assertEqual(core.display(obj), "(1 2 3 . 4)")

    def test_empty_list(self):
        obj = interop.scheme_list([])
        self.assertEqual(core.write(obj), "()")
        self.assertEqual(core.display(obj), "()")

    def test_quote(self):
        obj = interop.scheme_list([
            core.Symbol("quote"),
            interop.scheme_list([1, 2], 3)
        ])
        self.assertEqual(core.write(obj), "'(1 2 . 3)")
        self.assertEqual(core.display(obj), "'(1 2 . 3)")
