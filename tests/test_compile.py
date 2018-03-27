import unittest

from pyme import base
from pyme import exceptions
from pyme import interop
from pyme import reader
from pyme import types
from pyme.compile import compile, OpCode, Compiler, Builtins


class TestCompile(unittest.TestCase):

    def setUp(self):
        pass

    def test_opcode_1(self):
        compiler = Compiler(env=None)
        compiler.compile_shortest(0x45, 1, 2)
        self.assertEqual(bytes(compiler.bytecode.code), b"\x01\x45")

    def test_opcode_3(self):
        compiler = Compiler(env=None)
        compiler.compile_shortest(0x1122, 1, None, 3)
        self.assertEqual(bytes(compiler.bytecode.code), b"\x03\x00\x11\x22")

    def test_opcode_exception(self):
        compiler = Compiler(env=None)
        with self.assertRaises(exceptions.CompileError):
            compiler.compile_shortest(0x1122, 1)

    def test_const(self):
        env = types.Environment()
        expr = interop.read_str("123456")
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.constants, [123456])

    def test_var(self):
        env = types.Environment()
        expr = interop.read_str("a")
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [expr])

    def test_call(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["+"]: None})
        expr = interop.read_str("(+ 10 20)", symbol_table=symbol_table)
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.READ_VAR_1.value, 0,
            OpCode.CONST_1.value, 0,
            OpCode.CONST_1.value, 1,
            OpCode.CALL_1.value, 2,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [symbol_table["+"]])
        self.assertEqual(result.constants, [10, 20])

    def test_if(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(bindings={symbol_table["if"]: Builtins.IF})
        expr = interop.read_str("(if #t 3 4)", symbol_table=symbol_table)
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.JUMP_IF_NOT_3.value, 0, 0, 12,
            OpCode.CONST_1.value, 1,
            OpCode.JUMP_3.value, 0, 0, 14,
            OpCode.CONST_1.value, 2,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertEqual(result.constants, [True, 3, 4])

    def test_quote(self):
        symbol_table = types.SymbolTable()
        env = types.Environment(
            bindings={symbol_table["quote"]: Builtins.QUOTE})
        expr = interop.read_str("'a", symbol_table=symbol_table)
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST_1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.variables, [])
        self.assertEqual(result.constants, [symbol_table["a"]])
