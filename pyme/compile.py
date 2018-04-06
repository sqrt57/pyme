"""Compiler from Scheme source to bytecode."""

from abc import ABC, abstractmethod
import collections
from enum import Enum, IntEnum, auto
import math

from pyme import base
from pyme.exceptions import CompileError
from pyme import interop
from pyme import types


class OpCode(IntEnum):
    """Operation code."""

    CONST_1 = auto()
    CONST_3 = auto()
    READ_VAR_1 = auto()
    READ_VAR_3 = auto()
    RET = auto()
    DROP = auto()
    CALL_1 = auto()
    CALL_3 = auto()
    JUMP_IF_NOT_3 = auto()
    JUMP_3 = auto()
    DEFINE_1 = auto()
    DEFINE_3 = auto()
    SET_VAR_1 = auto()
    SET_VAR_3 = auto()
    PUSH_FALSE = auto()
    MAKE_CLOSURE = auto()
    APPLY = auto()


opcode_num_args = {
    OpCode.CONST_1: 1,
    OpCode.CONST_3: 3,
    OpCode.READ_VAR_1: 1,
    OpCode.READ_VAR_3: 3,
    OpCode.RET: 0,
    OpCode.DROP: 0,
    OpCode.CALL_1: 1,
    OpCode.CALL_3: 3,
    OpCode.JUMP_IF_NOT_3: 3,
    OpCode.JUMP_3: 3,
    OpCode.DEFINE_1: 1,
    OpCode.DEFINE_3: 3,
    OpCode.SET_VAR_1: 1,
    OpCode.SET_VAR_3: 3,
    OpCode.PUSH_FALSE: 0,
    OpCode.MAKE_CLOSURE: 0,
}


class Bytecode:
    """Bytecode for Scheme function or code block."""

    def __init__(self):
        """Create empty bytecode."""
        self.code = bytearray()
        self.constants = []
        self.variables = []
        self.formals = []
        self.formals_rest = None

    def append(self, byte):
        self.code.append(byte)

    def position(self):
        return len(self.code)

    def extend(self, bytes_):
        self.code.extend(bytes_)

    def add_constant(self, value):
        pos = len(self.constants)
        self.constants.append(value)
        return pos

    def add_variable(self, value):
        pos = len(self.variables)
        self.variables.append(value)
        return pos


class _Builtin:

    def __init__(self, proc):
        self.proc = proc

    def compile(self, compiler, *args):
        return self.proc(compiler, *args)


class Compiler:

    def __init__(self, *, env):
        self.env = env
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

    def compile_const(self, expr):
        pos = self.bytecode.add_constant(expr)
        self.compile_shortest(
            pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)

    def compile_variable(self, expr):
        pos = self.bytecode.add_variable(expr)
        self.compile_shortest(
            pos,
            OpCode.READ_VAR_1.value, None, OpCode.READ_VAR_3.value)

    def compile_call(self, expr):
        proc = expr.car
        args, rest = interop.from_scheme_list(expr.cdr)
        if not base.nullp(rest):
            raise CompileError("Improper list in procedure call")
        proc_binding = self.env.get(proc)
        if isinstance(proc_binding, _Builtin):
            return proc_binding.compile(self, *args)
        else:
            self.compile_expr(proc)
            for arg in args:
                self.compile_expr(arg)
            self.compile_apply(len(args))

    def compile_expr(self, expr):
        if (base.numberp(expr) or base.stringp(expr)
                or base.booleanp(expr)):
            self.compile_const(expr)
        elif base.symbolp(expr):
            self.compile_variable(expr)
        elif base.pairp(expr):
            self.compile_call(expr)
        else:
            msg = "Bad expr for compilation: {}".format(expr)
            raise CompileError(msg)

    def compile_apply(self, num_args):
        self.compile_shortest(
            num_args,
            OpCode.CALL_1.value, None, OpCode.CALL_3.value)

    def compile_block(self, exprs):
        """Compile exprs to Bytecode.

        'exprs' is a list of expressions to compile.
        """
        first = True
        for expr in exprs:
            if first:
                first = False
            else:
                self.bytecode.append(OpCode.DROP.value)
            self.compile_expr(expr)
        self.bytecode.append(OpCode.RET.value)

    def compile_if(self, if_, then_, else_):
        self.compile_expr(if_)
        self.bytecode.append(OpCode.JUMP_IF_NOT_3)
        if_addr = self.bytecode.position()
        self.bytecode.extend(b"\x00\x00\x00")

        self.compile_expr(then_)
        self.bytecode.append(OpCode.JUMP_3)
        then_addr = self.bytecode.position()
        self.bytecode.extend(b"\x00\x00\x00")
        pos = self.bytecode.position().to_bytes(3, byteorder='big')
        self.bytecode.code[if_addr:if_addr+3] = pos

        self.compile_expr(else_)
        pos = self.bytecode.position().to_bytes(3, byteorder='big')
        self.bytecode.code[then_addr:then_addr+3] = pos

    def compile_lambda(self, formals, *body):
        formals, formals_rest = interop.from_scheme_list(formals)
        for f in formals:
            if not base.symbolp(f):
                raise CompileError("Non-symbol in lambda arguments list")
        lambda_ = Bytecode()
        lambda_.formals = formals
        if base.symbolp(formals_rest):
            lambda_.formals_rest = formals_rest
        elif base.nullp(formals_rest):
            lambda_.formals_rest = None
        else:
            raise CompileError("Non-symbol in lambda rest argument")
        self.outer_bytecodes.append(self.bytecode)
        self.bytecode = lambda_
        self.compile_block(body)
        self.bytecode = self.outer_bytecodes.pop()
        self.compile_const(lambda_)
        self.bytecode.append(OpCode.MAKE_CLOSURE.value)

    def compile_define_var(self, var, value):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in variable definition")
        self.compile_expr(value)
        pos = self.bytecode.add_variable(var)
        self.compile_shortest(
            pos,
            OpCode.DEFINE_1.value, None, OpCode.DEFINE_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)

    def compile_define_proc(self, var, signature, *body):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in procedure definition")
        self.compile_lambda(signature, *body)
        pos = self.bytecode.add_variable(var)
        self.compile_shortest(
            pos,
            OpCode.DEFINE_1.value, None, OpCode.DEFINE_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)

    def compile_define(self, lvalue, *rest):
        if base.symbolp(lvalue):
            if len(rest) < 1:
                raise CompileError(
                    "define: missing value for identifier")
            if len(rest) > 1:
                raise CompileError(
                    "define: multiple values for identifier")
            self.compile_define_var(lvalue, rest[0])
        elif base.pairp(lvalue):
            self.compile_define_proc(lvalue.car, lvalue.cdr, *rest)
        else:
            raise CompileError("define: invalid syntax")

    def compile_set_var(self, var, value):
        if not base.symbolp(var):
            raise CompileError("Non-symbol in set!")
        self.compile_expr(value)
        pos = self.bytecode.add_variable(var)
        self.compile_shortest(
            pos,
            OpCode.SET_VAR_1.value, None, OpCode.SET_VAR_3.value)
        self.bytecode.append(OpCode.PUSH_FALSE.value)


def compile(expr, *, env):
    """Compile expr to Bytecode.

    'exprs' is a Scheme expression to compile.

    Use 'env' to resolve special forms while compiling exprssion.
    """
    compiler = Compiler(env=env)
    compiler.compile_block([expr])
    return compiler.bytecode


class Builtins:

    IF = _Builtin(Compiler.compile_if)
    QUOTE = _Builtin(Compiler.compile_const)
    LAMBDA = _Builtin(Compiler.compile_lambda)
    DEFINE = _Builtin(Compiler.compile_define)
    SET = _Builtin(Compiler.compile_set_var)


def decompile_code_inner(bytecode, *, result, prefix):
    l = math.ceil(math.log10(len(bytecode.code) + 1))
    ip = 0
    result.append("{0}formals = {1}".format(prefix, bytecode.formals))
    result.append("{0}formals_rest = {1}".format(prefix, bytecode.formals_rest))
    result.append("{0}constants = {1}".format(prefix, bytecode.constants))
    result.append("{0}variables = {1}".format(prefix, bytecode.variables))
    while ip < len(bytecode.code):
        instr = OpCode(bytecode.code[ip])
        n = opcode_num_args[instr]
        if n > 0:
            arg = int.from_bytes(bytecode.code[ip+1:ip+n+1], byteorder='big')
            result.append("{0}{1:0{2}}: {3:10} {4}".format(
                prefix, ip, l, instr.name, arg))
            ip += n + 1
        else:
            result.append("{0}{1:0{2}}: {3:10}".format(
                prefix, ip, l, instr.name))
            ip += 1
    result.append(prefix)
    for i, const in enumerate(bytecode.constants):
        if isinstance(const, Bytecode):
            result.append("{0}constants[{1}]:".format(prefix, i))
            decompile_code_inner(const, result=result, prefix=prefix+".   ")

def decompile_code(bytecode):
    result = [""]
    decompile_code_inner(bytecode, result=result, prefix="")
    return "\n".join(result)
