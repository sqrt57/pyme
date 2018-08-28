"""Compile from abstract source tree to bytecode."""

from pyme import core
from pyme.core import TAIL
from pyme.bytecode import Bytecode, OpCode
from pyme.exceptions import CompileError


class BytecodeCompiler:

    def __init__(self):
        self.bytecode = Bytecode()
        self.outer_bytecodes = []

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

    def compile_const(self, element):
        pos = self.bytecode.add_constant(element.value)
        self.compile_shortest(
            pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def compile_get_variable(self, element):
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.READ_VAR_1.value, None, OpCode.READ_VAR_3.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def compile_call(self, element):
        self.compile_expr(element.proc)
        for arg in element.args:
            self.compile_expr(arg)
        if element.attribute[TAIL]:
            self.compile_shortest(
                len(element.args),
                OpCode.TAIL_CALL_1.value, None, OpCode.TAIL_CALL_3.value)
        else:
            self.compile_shortest(
                len(element.args),
                OpCode.CALL_1.value, None, OpCode.CALL_3.value)

    def compile_expr(self, expr):
        if isinstance(expr, core.Constant):
            self.compile_const(expr)
        elif isinstance(expr, core.GetVariable):
            self.compile_get_variable(expr)
        elif isinstance(expr, core.SetVariable):
            self.compile_set_variable(expr)
        elif isinstance(expr, core.DefineVariable):
            self.compile_define_variable(expr)
        elif isinstance(expr, core.Apply):
            self.compile_call(expr)
        elif isinstance(expr, core.If):
            self.compile_if(expr)
        elif isinstance(expr, core.Lambda):
            self.compile_lambda(expr)
        else:
            msg = "Bad expr for compilation: {}".format(expr)
            raise CompileError(msg)

    def compile_block(self, element):
        """Compile exprs to Bytecode.

        'exprs' is a list of expressions to compile.
        """
        if len(element.exprs) == 0:
            constant = core.Constant(value=False)
            constant.attribute[TAIL] = element.attribute[TAIL]
            self.compile_const(constant)
        else:
            for expr in element.exprs[:-1]:
                self.compile_expr(expr)
                self.bytecode.append(OpCode.DROP.value)
            self.compile_expr(element.exprs[-1])

    def compile_if(self, element):
        self.compile_expr(element.condition)
        self.bytecode.append(OpCode.JUMP_IF_NOT_3)
        if_addr = self.bytecode.position()
        self.bytecode.extend(b"\x00\x00\x00")

        self.compile_expr(element.then_)
        if not element.attribute[TAIL]:
            self.bytecode.append(OpCode.JUMP_3)
            then_addr = self.bytecode.position()
            self.bytecode.extend(b"\x00\x00\x00")

        pos = self.bytecode.position().to_bytes(3, byteorder='big')
        self.bytecode.code[if_addr:if_addr+3] = pos
        self.compile_expr(element.else_)

        if not element.attribute[TAIL]:
            pos = self.bytecode.position().to_bytes(3, byteorder='big')
            self.bytecode.code[then_addr:then_addr+3] = pos

    def compile_lambda(self, element):
        compiler = BytecodeCompiler()
        compiler.bytecode.formals = element.args
        compiler.bytecode.formals_rest = element.rest_args
        compiler.compile_block(element.body)
        constant = core.Constant(value=compiler.bytecode)
        constant.attribute[TAIL] = False
        self.compile_const(constant)
        self.bytecode.append(OpCode.MAKE_CLOSURE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def compile_define_variable(self, element):
        self.compile_expr(element.value)
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.DEFINE_1.value, None, OpCode.DEFINE_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)

    def compile_set_variable(self, element):
        self.compile_expr(element.value)
        pos = self.bytecode.add_variable(element.variable)
        self.compile_shortest(
            pos,
            OpCode.SET_VAR_1.value, None, OpCode.SET_VAR_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if element.attribute[TAIL]:
            self.bytecode.append(OpCode.RET.value)
