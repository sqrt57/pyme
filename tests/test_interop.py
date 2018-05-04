import unittest

from pyme import base
from pyme import interop
from pyme.interop import get_config


class TestInterop(unittest.TestCase):

    def test_scheme_list(self):
        x = interop.scheme_list([1, 2])
        self.assertTrue(base.pairp(x))
        self.assertEqual(x.car, 1)
        self.assertTrue(base.pairp(x.cdr))
        self.assertEqual(x.cdr.car, 2)
        self.assertTrue(base.nullp(x.cdr.cdr))


class TestGetConfig(unittest.TestCase):

    def test_none(self):
        self.assertIsNone(get_config(None, "x"))
        self.assertIsNone(get_config(None, "x.y"))

    def test_level1(self):
        config = {"x": 5}
        self.assertEquals(get_config(config, "x"), 5)
        self.assertIsNone(get_config(config, "y"))

    def test_level2(self):
        config = {
            "x": {"x": 7}
        }
        self.assertEquals(get_config(config, "x.x"), 7)
        self.assertIsNone(get_config(config, "x.y"))
