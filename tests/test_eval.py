import io
import unittest

from pyme import core, eval, exceptions, interop, reader


class TestEval(unittest.TestCase):

    def setUp(self):
        pass

    def test_variable(self):
        symbol_table = core.SymbolTable()
        env = core.Environment(bindings={symbol_table["a"]: 5})
        expr = interop.read_str("a", symbol_table=symbol_table)
        result = eval.eval(expr, env)
        self.assertEqual(result, 5)
