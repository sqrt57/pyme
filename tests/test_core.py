import unittest

from pyme import core

class TestCore(unittest.TestCase):

    def test_pair(self):
        pair = core.Pair(1, 2)
        self.assertEqual(pair.car, 1)
        self.assertEqual(pair.cdr, 2)
        pair.car = "hello"
        self.assertEqual(pair.car, "hello")

    def test_write_pair(self):
        pair = core.Pair(1, "qqq")
        self.assertEqual(core.write(pair), '(1 . "qqq")')

    def test_display_pair(self):
        pair = core.Pair(1, "qqq")
        self.assertEqual(core.display(pair), '(1 . qqq)')

class TestSymbols(unittest.TestCase):

    def test_unique(self):
        store = core.SymbolStore()
        a = store['qwe']
        b = store['qwe']
        self.assertEqual(a, b)
