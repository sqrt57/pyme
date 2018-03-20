import unittest

from pyme import eval, interop, base, reader, types


class TestEval(unittest.TestCase):

    def setUp(self):
        pass

    def test_variable(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["a"]: 5})
        expr = interop.read_str("a", symbol_table=symbol_table)
        result = eval.eval(expr, env=env)
        self.assertEqual(result, 5)

    def test_number(self):
        env = types.Environment()
        expr = interop.read_str("3")
        result = eval.eval(expr, env=env)
        self.assertEqual(result, 3)

    def test_fun_call(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["+"]: base.plus})
        expr = interop.read_str("(+ 1 2)", symbol_table=symbol_table)
        result = eval.eval(expr, env=env)
        self.assertEqual(result, 3)

    def test_recursive(self):
        n = 100
        string = "(+ 1 "*n + ")"*n
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["+"]: base.plus})
        expr = interop.read_str(string, symbol_table=symbol_table)
        result = eval.eval(expr, env=env)
        self.assertEqual(result, n)

    def test_deep_recursive(self):
        n = 1000
        expr = 0
        plus = types.Symbol("+")
        for i in range(n):
            expr = base.cons(plus, base.cons(1, base.cons(expr, None)))
        env = types.Environment(bindings={plus: base.plus})
        result = eval.eval(expr, env=env)
        self.assertEqual(result, n)
