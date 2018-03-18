import io
import unittest

from pyme import core, eval, exceptions, interop, scheme_base, reader


class TestFuns(unittest.TestCase):

    def setUp(self):
        pass

    def test_nullp(self):
        self.assertEqual(scheme_base.nullp(None), True)
        self.assertEqual(scheme_base.nullp(core.Pair(None, None)), False)

    def test_pairp(self):
        self.assertEqual(scheme_base.pairp(None), False)
        self.assertEqual(scheme_base.pairp(5), False)
        self.assertEqual(scheme_base.pairp(core.Pair(None, None)), True)

    def test_listp(self):
        self.assertEqual(scheme_base.listp(None), True)
        self.assertEqual(scheme_base.listp(5), False)
        self.assertEqual(scheme_base.listp(core.Pair(1, None)), True)
        self.assertEqual(scheme_base.listp(core.Pair(1, 2)), False)
