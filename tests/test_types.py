import io
import unittest

from pyme import base
from pyme import exceptions
from pyme import interop
from pyme import ports
from pyme import types
from pyme import write


class TestTypes(unittest.TestCase):

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

    def test_env_define(self):
        env = types.Environment()
        a = types.Symbol("a")
        env.define(a, 5)
        self.assertEqual(env[a], 5)

    def test_env_define_override(self):
        parent = types.Environment()
        env = types.Environment(parent=parent)
        a = types.Symbol("a")
        parent.define(a, 3)
        env.define(a, 5)
        self.assertEqual(parent[a], 3)
        self.assertEqual(env[a], 5)

    def test_env_define_set(self):
        parent = types.Environment()
        env = types.Environment(parent=parent)
        a = types.Symbol("a")
        parent.define(a, 3)
        env.set_(a, 5)
        self.assertEqual(parent[a], 5)
        self.assertEqual(env[a], 5)

    def test_env_set_error(self):
        env = types.Environment()
        a = types.Symbol("a")
        with self.assertRaises(exceptions.IdentifierNotBoundError):
            env.set_(a, 5)
