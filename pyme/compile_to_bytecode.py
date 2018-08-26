"""Compile from Scheme source to abstract syntax tree."""

from pyme import ast
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

    def compile_const(self, value, *, tail):
        pos = self.bytecode.add_constant(value)
        self.compile_shortest(
            pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)
        if tail: self.bytecode.append(OpCode.RET.value)

    def compile_get_variable(self, variable, *, tail):
        pos = self.bytecode.add_variable(variable.variable)
        self.compile_shortest(
            pos,
            OpCode.READ_VAR_1.value, None, OpCode.READ_VAR_3.value)
        if tail: self.bytecode.append(OpCode.RET.value)

    def compile_call(self, expr, *, tail):
        self.compile_expr(expr.proc, tail=False)
        for arg in expr.args:
            self.compile_expr(arg, tail=False)
        self.compile_apply(len(expr.args), tail=tail)

    def compile_expr(self, expr, *, tail):
        if isinstance(expr, ast.Constant):
            self.compile_const(expr.value, tail=tail)
        elif isinstance(expr, ast.GetVariable):
            self.compile_get_variable(expr.variable, tail=tail)
        elif isinstance(expr, ast.SetVariable):
            self.compile_set_variable(expr.variable, expr.value, tail=tail)
        elif isinstance(expr, ast.DefineVariable):
            self.compile_define_variable(expr.variable, expr.value, tail=tail)
        elif isinstance(expr, ast.Apply):
            self.compile_call(expr, tail=tail)
        elif isinstance(expr, ast.If):
            self.compile_if(expr.condition, expr.then_, expr.else_, tail=tail)
        elif isinstance(expr, ast.Lambda):
            self.compile_lambda(expr, tail=tail)
        else:
            msg = "Bad expr for compilation: {}".format(expr)
            raise CompileError(msg)

    def compile_apply(self, num_args, *, tail):
        if tail:
            self.compile_shortest(
                num_args,
                OpCode.TAIL_CALL_1.value, None, OpCode.TAIL_CALL_3.value)
        else:
            self.compile_shortest(
                num_args,
                OpCode.CALL_1.value, None, OpCode.CALL_3.value)

    def compile_block(self, block, *, tail):
        """Compile exprs to Bytecode.

        'exprs' is a list of expressions to compile.
        """
        if len(block.exprs) == 0:
            if tail:
                self.bytecode.append(OpCode.RET.value)
        else:
            for expr in block.exprs[:-1]:
                self.compile_expr(expr, tail=False)
                self.bytecode.append(OpCode.DROP.value)
            self.compile_expr(block.exprs[-1], tail=tail)

    def compile_if(self, if_, then_, else_, *, tail):
        self.compile_expr(if_, tail=False)
        self.bytecode.append(OpCode.JUMP_IF_NOT_3)
        if_addr = self.bytecode.position()
        self.bytecode.extend(b"\x00\x00\x00")

        self.compile_expr(then_, tail=tail)
        if not tail:
            self.bytecode.append(OpCode.JUMP_3)
            then_addr = self.bytecode.position()
            self.bytecode.extend(b"\x00\x00\x00")

        pos = self.bytecode.position().to_bytes(3, byteorder='big')
        self.bytecode.code[if_addr:if_addr+3] = pos
        self.compile_expr(else_, tail=tail)

        if not tail:
            pos = self.bytecode.position().to_bytes(3, byteorder='big')
            self.bytecode.code[then_addr:then_addr+3] = pos

    def compile_lambda(self, expr, tail):
        compiler = BytecodeCompiler()
        compiler.bytecode.formals = expr.args
        compiler.bytecode.formals_rest = expr.rest_args
        compiler.compile_block(expr.body, tail=True)
        self.compile_const(compiler.bytecode, tail=False)
        self.bytecode.append(OpCode.MAKE_CLOSURE.value)
        if tail: self.bytecode.append(OpCode.RET.value)

    def compile_define_variable(self, var, value, *, tail):
        self.compile_expr(value, tail=False)
        pos = self.bytecode.add_variable(var.variable)
        self.compile_shortest(
            pos,
            OpCode.DEFINE_1.value, None, OpCode.DEFINE_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if tail: self.bytecode.append(OpCode.RET.value)

    def compile_set_variable(self, var, value, *, tail):
        self.compile_expr(value, tail=False)
        pos = self.bytecode.add_variable(var.variable)
        self.compile_shortest(
            pos,
            OpCode.SET_VAR_1.value, None, OpCode.SET_VAR_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)
        if tail: self.bytecode.append(OpCode.RET.value)
