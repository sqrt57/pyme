"""Compiler from Scheme source to bytecode."""

from enum import Enum, auto

from pyme import base
from pyme.exceptions import CompileError
from pyme import types


class OpCode(Enum):
    """Operation code."""

    CONST1 = auto()
    CONST3 = auto()
    READ_VAR1 = auto()
    READ_VAR3 = auto()
    RET = auto()
    DROP = auto()


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


def compile_expr(bytecode, expr, *, env):
    """Compile one 'expr' to 'bytecode' in environment 'env'."""
    if base.numberp(expr) or base.stringp(expr):
        pos = bytecode.add_constant(expr)
        compile_shortest(
            bytecode, pos,
            OpCode.CONST1.value, None, OpCode.CONST3.value)
    elif base.symbolp(expr):
        pos = bytecode.add_variable(expr)
        compile_shortest(
            bytecode, pos,
            OpCode.READ_VAR1.value, None, OpCode.READ_VAR1.value)
    elif base.pairp(expr):
        pass


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
        compile_expr(bytecode, expr, env=env)
    bytecode.append(OpCode.RET.value)
    return bytecode
