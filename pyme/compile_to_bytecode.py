"""Compile from abstract source tree to bytecode."""

from pyme import core
from pyme.core import TAIL
from pyme.bytecode import Bytecode, OpCode
from pyme.exceptions import CompileError


class BytecodeCompiler:

    def __init__(self):
        self.bytecode = Bytecode()
        self.outer_bytecodes = []

    def compile(self, element):
        element.accept(self)

    def compile_shortest(self, arg, *opcodes):
        """Compile shortest form of opcode with argument.

        Compile shortest variant of opcode to 'bytecode'.
        'arg' is integer argument to bytecode.
        'opcodes' are opcode variants for different arg sizes:
        opcodes=[op1, op2, op3, ...], where op1 has 1-byte argument,
        op2 has 2-bytes argument, etc. If opn is None then we don't have
        n-bytes opcode variant, we next shortest variant.
        """
        for n in range(len(opcodes)):
            if opcodes[n] is not None:
                try:
                    arg_bytes = arg.to_bytes(n+1, byteorder='big')
                    self.bytecode.append(opcodes[n])
                    self.bytecode.extend(arg_bytes)
                    return
                except OverflowError:
                    pass
        raise CompileError("Cannot compile opcode - argument too big")

    def compile_constant(self, value):
        pos = self.bytecode.add_constant(value)
        self.compile_shortest(
            pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)

    def constant(self, element):
        self.compile_constant(element.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def get_variable(self, element):
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.READ_VAR_1.value, None, OpCode.READ_VAR_3.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def apply(self, element):
        element.proc.accept(self)
        for arg in element.args:
            arg.accept(self)
        if element.attribute[TAIL]:
            self.compile_shortest(
                len(element.args),
                OpCode.TAIL_CALL_1.value, None, OpCode.TAIL_CALL_3.value)
        else:
            self.compile_shortest(
                len(element.args),
                OpCode.CALL_1.value, None, OpCode.CALL_3.value)

    def block(self, element):
        """Compile exprs to Bytecode.

        'exprs' is a list of expressions to compile.
        """
        if len(element.exprs) == 0:
            self.compile_constant(False)
            if element.attribute[TAIL]:
                self.bytecode.append(OpCode.RET.value)
        else:
            for expr in element.exprs:
                expr.accept(self)
                self.bytecode.append(OpCode.DROP.value)
            self.bytecode.truncate_by(1)

    def if_(self, element):
        element.condition.accept(self)
        self.bytecode.append(OpCode.JUMP_IF_NOT_3)
        if_addr = self.bytecode.position()
        self.bytecode.extend(b"\x00\x00\x00")

        element.then_.accept(self)
        if not element.attribute[TAIL]:
            self.bytecode.append(OpCode.JUMP_3)
            then_addr = self.bytecode.position()
            self.bytecode.extend(b"\x00\x00\x00")

        pos = self.bytecode.position().to_bytes(3, byteorder='big')
        self.bytecode.code[if_addr:if_addr+3] = pos
        element.else_.accept(self)

        if not element.attribute[TAIL]:
            pos = self.bytecode.position().to_bytes(3, byteorder='big')
            self.bytecode.code[then_addr:then_addr+3] = pos

    def lambda_(self, element):
        compiler = BytecodeCompiler()
        compiler.bytecode.formals = element.args
        compiler.bytecode.formals_rest = element.rest_args
        element.body.accept(compiler)
        self.compile_constant(compiler.bytecode)
        self.bytecode.append(OpCode.MAKE_CLOSURE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def define_variable(self, element):
        element.value.accept(self)
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.DEFINE_1.value, None, OpCode.DEFINE_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def set_variable(self, element):
        element.value.accept(self)
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.SET_VAR_1.value, None, OpCode.SET_VAR_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)
