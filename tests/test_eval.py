import unittest

from pyme import core, eval, exceptions, interop, scheme_base, reader


class TestEval(unittest.TestCase):

    def setUp(self):
        pass

    def test_variable(self):
        symbol_table = core.SymbolTable()
        env = core.Environment(bindings={symbol_table["a"]: 5})
        expr = interop.read_str("a", symbol_table=symbol_table)
        result = eval.eval(expr, env)
        self.assertEqual(result, 5)

    def test_number(self):
        env = core.Environment()
        expr = interop.read_str("3")
        result = eval.eval(expr, env)
        self.assertEqual(result, 3)

    def test_fun_call(self):
        symbol_table = core.SymbolTable()
        env = core.Environment(bindings={symbol_table["+"]: scheme_base.plus})
        expr = interop.read_str("(+ 1 2)", symbol_table=symbol_table)
        result = eval.eval(expr, env)
        self.assertEqual(result, 3)
