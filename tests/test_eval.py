import unittest

from pyme.compile import Builtins
from pyme import eval
from pyme import exceptions
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

    def test_lambda(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={symbol_table["lambda"]: Builtins.LAMBDA})
        expr = interop.read_str("((lambda () 1))", symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 1)

    def test_lambda_arg(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={symbol_table["lambda"]: Builtins.LAMBDA})
        expr = interop.read_str("((lambda (x) x) 5)",
                                symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 5)

    def test_lambda_rest(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={
                symbol_table["lambda"]: Builtins.LAMBDA,
                symbol_table["quote"]: Builtins.QUOTE,
            })
        expr = interop.read_str("((lambda (x . y) y) 1 2 3)",
                                symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        result_list, result_rest = interop.from_scheme_list(result)
        self.assertEqual(result_list, [2, 3])
        self.assertTrue(base.nullp(result_rest))

    def test_define(self):
        symbol_table = types.SymbolTable()
        x = symbol_table['x']
        env = types.Environment(
            bindings={
                symbol_table["define"]: Builtins.DEFINE,
            })
        expr = interop.read_str("(define x 5)",
                                symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, False)
        self.assertEqual(env[x], 5)

    def test_define_set(self):
        symbol_table = types.SymbolTable()
        x = symbol_table['x']
        env = types.Environment(
            bindings={
                symbol_table["set!"]: Builtins.SET,
                x: 3,
            })
        expr = interop.read_str("(set! x 8)",
                                symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, False)
        self.assertEqual(env[x], 8)

    def test_set_error(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={
                symbol_table["set!"]: Builtins.SET,
            })
        expr = interop.read_str("(set! x 8)",
                                symbol_table=symbol_table)
        with self.assertRaises(exceptions.IdentifierNotBoundError):
            result = eval.eval([expr], env=env)

    def test_define_local(self):
        symbol_table = types.SymbolTable()
        x = symbol_table['x']
        env = types.Environment(
            bindings={
                symbol_table["lambda"]: Builtins.LAMBDA,
                symbol_table["define"]: Builtins.DEFINE,
                x: 3,
            })
        expr = interop.read_str(
            """
                ((lambda ()
                    (define x 8)
                    x))
            """,
            symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 8)
        self.assertEqual(env[x], 3)

    def test_set_local(self):
        symbol_table = types.SymbolTable()
        x = symbol_table['x']
        env = types.Environment(
            bindings={
                symbol_table["lambda"]: Builtins.LAMBDA,
                symbol_table["set!"]: Builtins.SET,
                x: 3,
            })
        expr = interop.read_str(
            """
                ((lambda ()
                    (set! x 8)
                    x))
            """,
            symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, 8)
        self.assertEqual(env[x], 8)

    def test_lexical_scope(self):
        symbol_table = types.SymbolTable()
        lexical = symbol_table['lexical']
        dynamic = symbol_table['dynamic']
        env = types.Environment(
            bindings={
                symbol_table["lambda"]: Builtins.LAMBDA,
                symbol_table["quote"]: Builtins.QUOTE,
            })
        expr = interop.read_str(
            """
                ((lambda (x) (((lambda (x) (lambda () x)) 'lexical)))
                    'dynamic)
            """,
            symbol_table=symbol_table)
        result = eval.eval([expr], env=env)
        self.assertEqual(result, lexical)
