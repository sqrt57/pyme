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

    @abstractmethod
    def compile(self, bytecode, *, env):
        pass


class _OpEval(_OpBase):

    def __init__(self, expr):
        self.expr = expr

    def compile(self, bytecode, *, env):
        if (base.numberp(self.expr) or base.stringp(self.expr)
                or base.booleanp(self.expr)):
            pos = bytecode.add_constant(self.expr)
            compile_shortest(
                bytecode, pos,
                OpCode.CONST_1.value, None, OpCode.CONST_3.value)
        elif base.symbolp(self.expr):
            pos = bytecode.add_variable(self.expr)
            compile_shortest(
                bytecode, pos,
                OpCode.READ_VAR_1.value, None, OpCode.READ_VAR_3.value)
        elif base.pairp(self.expr):
            fun = self.expr.car
            args, rest = interop.from_scheme_list(self.expr.cdr)
            if not base.nullp(rest):
                raise CompileError("Improper list in procedure call")
            fun_binding = env.get(fun)
            if isinstance(fun_binding, _Builtin):
                return fun_binding.compile(bytecode, args, env=env)
            else:
                result = []
                result.append(_OpEval(fun))
                for arg in args:
                    result.append(_OpEval(arg))
                result.append(_OpCall(len(args)))
                return result
        else:
            msg = "Bad expr for compilation: {}".format(self.expr)
            raise CompileError(msg)


class _OpCall(_OpBase):

    def __init__(self, num_args):
        self.num_args = num_args

    def compile(self, bytecode, *, env):
        compile_shortest(
            bytecode, self.num_args,
            OpCode.CALL_1.value, None, OpCode.CALL_3.value)


class _Builtin(ABC):
    """Builtins special forms.

    Those special forms are treated separately by compiler.
    """

    @abstractmethod
    def compile(self, bytecode, args, *, env):
        pass


class _If(_Builtin):

    class JumpAddresses:

        def __init__(self):
            self.if_jump = None
            self.then_jump = None

    class CheckCondition(_OpBase):

        def __init__(self, jump_addresses):
            self.jump_addresses = jump_addresses

        def compile(self, bytecode, *, env):
            bytecode.append(OpCode.JUMP_IF_NOT_3)
            self.jump_addresses.if_jump = bytecode.position()
            bytecode.extend(b"\x00\x00\x00")

    class AfterThen(_OpBase):

        def __init__(self, jump_addresses):
            self.jump_addresses = jump_addresses

        def compile(self, bytecode, *, env):
            bytecode.append(OpCode.JUMP_3)
            self.jump_addresses.then_jump = bytecode.position()
            bytecode.extend(b"\x00\x00\x00")
            pos = bytecode.position().to_bytes(3, byteorder='big')
            if_jump = self.jump_addresses.if_jump
            bytecode.code[if_jump:if_jump+3] = pos

    class AfterElse(_OpBase):

        def __init__(self, jump_addresses):
            self.jump_addresses = jump_addresses

        def compile(self, bytecode, *, env):
            pos = bytecode.position().to_bytes(3, byteorder='big')
            then_jump = self.jump_addresses.then_jump
            bytecode.code[then_jump:then_jump+3] = pos

    def compile(self, bytecode, args, *, env):
        if_, then_, else_ = args
        jump_addresses = self.JumpAddresses()
        return [
            _OpEval(if_),
            self.CheckCondition(jump_addresses),
            _OpEval(then_),
            self.AfterThen(jump_addresses),
            _OpEval(else_),
            self.AfterElse(jump_addresses),
        ]


class _Quote(_Builtin):

    def compile(self, bytecode, args, *, env):
        expr, = args
        pos = bytecode.add_constant(expr)
        compile_shortest(
            bytecode, pos,
            OpCode.CONST_1.value, None, OpCode.CONST_3.value)


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
                stack.extend(reversed(new_ops))
    bytecode.append(OpCode.RET.value)
    return bytecode


class Builtins:
    IF = _If()
    QUOTE = _Quote()
