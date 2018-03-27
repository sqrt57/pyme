import unittest

from pyme.compile import Builtins
from pyme import eval
from pyme import interop
from pyme import base
from pyme import reader
from pyme import types


class TestEval(unittest.TestCase):

    def setUp(self):
        pass

    @unittest.skip
    def test_variable(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["a"]: 5})
        expr = interop.read_str("a", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 5)

    def test_number(self):
        env = types.Environment()
        expr = interop.read_str("3")
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 3)

    def test_fun_call(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["+"]: base.plus})
        expr = interop.read_str("(+ 1 2)", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 3)

    def test_fun_call_order(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["-"]: base.minus})
        expr = interop.read_str("(- 1 2 3)", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, -4)

    def test_recursive(self):
        n = 100
        string = "(+ 1 "*n + ")"*n
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["+"]: base.plus})
        expr = interop.read_str(string, symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, n)

    def test_deep_recursive(self):
        """Deep enough so that constants don't fit in 1 byte.

        Not deep enough to overflow Python stack.
        """
        n = 300
        expr = 0
        plus = types.Symbol("+")
        for _ in range(n):
            expr = interop.scheme_list([plus, 1, expr])
        env = types.Environment(bindings={plus: base.plus})
        result = eval.eval([expr], env=env)
        self.assertEqual(result, n)

    def test_if_true(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["if"]: Builtins.IF})
        expr = interop.read_str("(if 1 2 3)", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 2)

    def test_if_false(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["if"]: Builtins.IF})
        expr = interop.read_str("(if #f 2 3)", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 3)

    def test_quote(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={symbol_table["quote"]: Builtins.QUOTE})
        expr = interop.read_str("'abc", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, symbol_table["abc"])
