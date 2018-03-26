"""Compiler from Scheme source to bytecode."""

from abc import ABC, abstractmethod
import collections
from enum import Enum, auto

from pyme import base
from pyme.exceptions import CompileError
from pyme import interop
from pyme import types


class OpCode(Enum):
    """Operation code."""

    CONST1 = auto()
    CONST3 = auto()
    READ_VAR1 = auto()
    READ_VAR3 = auto()
    RET = auto()
    DROP = auto()
    CALL1 = auto()
    CALL3 = auto()


class Bytecode:
    """Bytecode for Scheme function or code block."""

    def __init__(self):
        """Create empty bytecode."""
        self.code = bytearray()
        self.constants = []
        self.variables = []

    def append(self, byte):
        self.code.append(byte)

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


def compile_shortest(bytecode, arg, *opcodes):
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
                bytecode.append(opcodes[n])
                bytecode.extend(arg_bytes)
                return
            except OverflowError:
                pass
    raise CompileError("Cannot compile opcode - argument too big")


class _OpBase(ABC):

    def compile(self, bytecode, *, env):
        pass


class _OpEval(_OpBase):

    def __init__(self, expr):
        self.expr = expr

    def compile(self, bytecode, *, env):
        if base.numberp(self.expr) or base.stringp(self.expr):
            pos = bytecode.add_constant(self.expr)
            compile_shortest(
                bytecode, pos,
                OpCode.CONST1.value, None, OpCode.CONST3.value)
        elif base.symbolp(self.expr):
            pos = bytecode.add_variable(self.expr)
            compile_shortest(
                bytecode, pos,
                OpCode.READ_VAR1.value, None, OpCode.READ_VAR3.value)
        elif base.pairp(self.expr):
            fun = self.expr.car
            args, rest = interop.from_scheme_list(self.expr.cdr)
            if not base.nullp(rest):
                raise CompileError("Improper list in procedure call")
            result = []
            result.append(_OpCall(len(args)))
            for arg in reversed(args):
                result.append(_OpEval(arg))
            result.append(_OpEval(fun))
            return result


class _OpCall(_OpBase):

    def __init__(self, num_args):
        self.num_args = num_args

    def compile(self, bytecode, *, env):
        compile_shortest(
            bytecode, self.num_args,
            OpCode.CALL1.value, None, OpCode.CALL3.value)


def compile(exprs, *, env):
    """Compile exprs to Bytecode.

    'exprs' is a list of expressions to compile.

    Use 'env' to resolve special forms while compiling exprssions.
    """
    bytecode = Bytecode()
    first = True
    for expr in exprs:
        if first:
            first = False
        else:
            bytecode.append(OpCode.DROP.value)
        stack = [_OpEval(expr)]
        while stack:
            op = stack.pop()
            new_ops = op.compile(bytecode, env=env)
            if new_ops:
                stack.extend(new_ops)
    bytecode.append(OpCode.RET.value)
    return bytecode
