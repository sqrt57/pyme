"""Compiler from Scheme source to bytecode."""

from abc import ABC, abstractmethod
import collections
from enum import Enum, IntEnum, auto

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


class Bytecode:
    """Bytecode for Scheme function or code block."""

    def __init__(self):
        """Create empty bytecode."""
        self.code = bytearray()
        self.constants = []
        self.variables = []

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


class Compiler:

    def __init__(self, *, env):
        self.env = env
        self.bytecode = Bytecode()

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
        fun = expr.car
        args, rest = interop.from_scheme_list(expr.cdr)
        if not base.nullp(rest):
            raise CompileError("Improper list in procedure call")
        fun_binding = self.env.get(fun)
        if isinstance(fun_binding, _Builtin):
            return fun_binding.compile(self, *args)
        else:
            self.compile_expr(fun)
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


class _Builtin(ABC):
    """Builtins special forms.

    Those special forms are treated separately by compiler.
    """

    @abstractmethod
    def compile(self, compiler, *args):
        pass


class _If(_Builtin):

    def compile(self, compiler, if_, then_, else_):
        compiler.compile_expr(if_)
        compiler.bytecode.append(OpCode.JUMP_IF_NOT_3)
        if_addr = compiler.bytecode.position()
        compiler.bytecode.extend(b"\x00\x00\x00")

        compiler.compile_expr(then_)
        compiler.bytecode.append(OpCode.JUMP_3)
        then_addr = compiler.bytecode.position()
        compiler.bytecode.extend(b"\x00\x00\x00")
        pos = compiler.bytecode.position().to_bytes(3, byteorder='big')
        compiler.bytecode.code[if_addr:if_addr+3] = pos

        compiler.compile_expr(else_)
        pos = compiler.bytecode.position().to_bytes(3, byteorder='big')
        compiler.bytecode.code[then_addr:then_addr+3] = pos


class _Quote(_Builtin):

    def compile(self, compiler, expr):
        pos = compiler.bytecode.add_constant(expr)
        compiler.compile_shortest(
            pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)


def compile(exprs, *, env):
    """Compile exprs to Bytecode.

    'exprs' is a list of expressions to compile.

    Use 'env' to resolve special forms while compiling exprssions.
    """
    compiler = Compiler(env=env)
    compiler.compile_block(exprs)
    return compiler.bytecode


class Builtins:
    IF = _If()
    QUOTE = _Quote()
