import io
import unittest

from pyme import base, eval, exceptions, interop, reader


class TestFuns(unittest.TestCase):

    def setUp(self):
        pass

    def test_nullp(self):
        self.assertEqual(base.nullp(None), True)
        self.assertEqual(base.nullp(base.cons(None, None)), False)

    def test_pairp(self):
        self.assertEqual(base.pairp(None), False)
        self.assertEqual(base.pairp(5), False)
        self.assertEqual(base.pairp(base.cons(None, None)), True)

    def test_listp(self):
        self.assertEqual(base.listp(None), True)
        self.assertEqual(base.listp(5), False)
        self.assertEqual(base.listp(base.cons(1, None)), True)
        self.assertEqual(base.listp(base.cons(1, 2)), False)
