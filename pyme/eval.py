"""Evaluate Scheme code."""

from abc import ABC, abstractmethod
import numbers

from pyme import base
from pyme import interop
from pyme.compile import compile, OpCode
from pyme.exceptions import EvalError


def run(bytecode, *, env):
    """Run bytecode in environment 'env'."""
    stack = []
    ip = 0
    while True:
        instr = bytecode.code[ip]
        ip += 1
        if instr == OpCode.CONST1.value:
            index = bytecode.code[ip]
            ip += 1
            stack.append(bytecode.constants[index])
        elif instr == OpCode.CONST3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            stack.append(bytecode.constants[index])
        elif instr == OpCode.READ_VAR1.value:
            index = bytecode.code[ip]
            ip += 1
            stack.append(env[bytecode.variables[index]])
        elif instr == OpCode.READ_VAR3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            stack.append(env[bytecode.variables[index]])
        elif instr == OpCode.RET.value:
            return stack[-1]
        else:
            raise EvalError("Unknown bytecode: 0x{:02x}".format(instr))


def eval(exprs, *, env):
    """Evaluate list of scheme exprs.

    Compile and execute 'exprs' - list of Scheme expressions
    in environment 'env'.
    """
    bytecode = compile(exprs, env=env)
    result = run(bytecode, env=env)
    return result
