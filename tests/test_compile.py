import unittest

from pyme import base
from pyme import exceptions
from pyme import interop
from pyme import reader
from pyme import types
from pyme.bytecode import Bytecode, OpCode
from pyme.compile import compile
from pyme.compile_to_bytecode import BytecodeCompiler
from pyme.compile_to_ast import Builtins


class TestCompile(unittest.TestCase):

    def setUp(self):
        pass

    def test_opcode_1(self):
        compiler = BytecodeCompiler()
        compiler.compile_shortest(0x45, 1, 2)
        self.assertEqual(bytes(compiler.bytecode.code), b"\x01\x45")

    def test_opcode_3(self):
        compiler = BytecodeCompiler()
        compiler.compile_shortest(0x1122, 1, None, 3)
        self.assertEqual(bytes(compiler.bytecode.code), b"\x03\x00\x11\x22")

    def test_opcode_exception(self):
        compiler = BytecodeCompiler()
        with self.assertRaises(exceptions.CompileError):
            compiler.compile_shortest(0x1122, 1)

    def test_const(self):
        env = types.Environment()
        expr = interop.read_str("123456")
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.constants, [123456])

    def test_var(self):
        env = types.Environment()
        expr = interop.read_str("a")
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [expr])

    def test_call(self):
        symbol_table = types.symbol_table()
        env = types.Environment(bindings={symbol_table["+"]: None})
        expr = interop.read_str("(+ 10 20)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.CONST_1.value, 0,
            OpCode.CONST_1.value, 1,
            OpCode.TAIL_CALL_1.value, 2,
        ]))
        self.assertEqual(result.variables, [symbol_table["+"]])
        self.assertEqual(result.constants, [10, 20])

    def test_if_tail(self):
        symbol_table = types.symbol_table()
        env = types.Environment(bindings={symbol_table["if"]: Builtins.IF})
        expr = interop.read_str("(if #t 3 4)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.JUMP_IF_NOT_3.value, 0, 0, 9,
            OpCode.CONST_1.value, 1,
            OpCode.RET.value,
            OpCode.CONST_1.value, 2,
            OpCode.RET.value,
        ]))
        self.assertEqual(result.variables, [])
        self.assertEqual(result.constants, [True, 3, 4])

    def test_if_non_tail(self):
        symbol_table = types.symbol_table()
        env = types.Environment(bindings={
            symbol_table["if"]: Builtins.IF,
            symbol_table["+"]: base.plus,
        })
        expr = interop.read_str("(+ (if #t 3 4) 5)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.CONST_1.value, 0,
            OpCode.JUMP_IF_NOT_3.value, 0, 0, 14,
            OpCode.CONST_1.value, 1,
            OpCode.JUMP_3.value, 0, 0, 16,
            OpCode.CONST_1.value, 2,
            OpCode.CONST_1.value, 3,
            OpCode.TAIL_CALL_1.value, 2,
        ]))
        self.assertEqual(result.variables, [symbol_table["+"]])
        self.assertEqual(result.constants, [True, 3, 4, 5])

    def test_quote(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["quote"]: Builtins.QUOTE})
        expr = interop.read_str("'a", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertEqual(result.constants, [symbol_table["a"]])

    def test_lambda(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["lambda"]: Builtins.LAMBDA})
        expr = interop.read_str("(lambda () 4 5)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.MAKE_CLOSURE.value,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertIsInstance(result.constants[0], Bytecode)
        self.assertEqual(result.constants[0].code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.DROP.value,
            OpCode.CONST_1.value, 1,
            OpCode.RET.value]))
        self.assertEqual(result.constants[0].constants, [4, 5])
        self.assertEqual(result.constants[0].variables, [])
        self.assertEqual(result.constants[0].formals, [])
        self.assertIsNone(result.constants[0].formals_rest)

    def test_lambda_arg(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["lambda"]: Builtins.LAMBDA})
        x = symbol_table["x"]
        expr = interop.read_str("(lambda (x) x)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.MAKE_CLOSURE.value,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertIsInstance(result.constants[0], Bytecode)
        self.assertEqual(result.constants[0].code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.constants[0].constants, [])
        self.assertEqual(result.constants[0].variables, [x])
        self.assertEqual(result.constants[0].formals, [x])

    def test_lambda_rest(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["lambda"]: Builtins.LAMBDA})
        x = symbol_table["x"]
        y = symbol_table["y"]
        expr = interop.read_str("(lambda (x :rest y) y)",
                                symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.MAKE_CLOSURE.value,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertIsInstance(result.constants[0], Bytecode)
        self.assertEqual(result.constants[0].code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.constants[0].constants, [])
        self.assertEqual(result.constants[0].variables, [y])
        self.assertEqual(result.constants[0].formals, [x])
        self.assertEqual(result.constants[0].formals_rest, y)

    def test_define(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["define"]: Builtins.DEFINE})
        x = symbol_table["x"]
        expr = interop.read_str("(define x 3)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.DEFINE_1.value, 0,
            OpCode.PUSH_FALSE.value,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [x])
        self.assertEqual(result.constants, [3])

    def test_set(self):
        symbol_table = types.symbol_table()
        env = types.Environment(
            bindings={symbol_table["set!"]: Builtins.SET})
        x = symbol_table["x"]
        expr = interop.read_str("(set! x 3)", symbol_table=symbol_table)
        result = compile(expr, env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.SET_VAR_1.value, 0,
            OpCode.PUSH_FALSE.value,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [x])
        self.assertEqual(result.constants, [3])
