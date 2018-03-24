import unittest

from pyme import base
from pyme import exceptions
from pyme import interop
from pyme import reader
from pyme import types
from pyme.compile import compile, compile_shortest, OpCode, Bytecode


class TestCompile(unittest.TestCase):

    def setUp(self):
        pass

    def test_opcode_1(self):
        bytecode = Bytecode()
        compile_shortest(bytecode, 0x45, 1, 2)
        self.assertEqual(bytes(bytecode.code), b"\x01\x45")

    def test_opcode_3(self):
        bytecode = Bytecode()
        compile_shortest(bytecode, 0x1122, 1, None, 3)
        self.assertEqual(bytes(bytecode.code), b"\x03\x00\x11\x22")

    def test_opcode_exception(self):
        bytecode = Bytecode()
        with self.assertRaises(exceptions.CompileError):
            compile_shortest(bytecode, 0x1122, 1)

    def test_const(self):
        env = types.Environment()
        expr = interop.read_str("123456")
        result = compile([expr], env=env)
        self.assertEqual(result.code, bytes([
            OpCode.CONST1.value, 0,
            OpCode.RET.value]))
        self.assertEqual(result.constants, [123456])
