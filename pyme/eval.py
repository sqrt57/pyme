"""Evaluate Scheme code."""

from abc import ABC, abstractmethod
import numbers

from pyme import base
from pyme import compile
from pyme import interop
from pyme import types
from pyme.compile import OpCode
from pyme.exceptions import EvalError


class Closure:

    def __init__(self, bytecode, *, env):
        self.bytecode = bytecode
        self.env = env


def bind_formals(bytecode, args):
    if len(bytecode.formals) > len(args):
        raise EvalError("Not enough arguments in procedure call")
    if bytecode.formals_rest is None and len(bytecode.formals) < len(args):
        raise EvalError("Too many arguments in procedure call")

    bindings = {}
    for i in range(len(bytecode.formals)):
        bindings[bytecode.formals[i]] = args[i]
    args_rest = args[len(bytecode.formals):]
    if bytecode.formals_rest is not None:
        bindings[bytecode.formals_rest] = interop.scheme_list(args_rest)
    return bindings


def pop_proc_args(stack, num):
    if len(stack) < num + 1:
        raise EvalError("Not enough values on stack for procedure call")
    new_stack = stack[:len(stack)-num-1]
    proc = stack[len(stack)-num-1]
    args = stack[len(stack)-num:]
    return new_stack, proc, args


def run(closure):
    """Run closure in its stored environment."""
    env = closure.env
    bytecode = closure.bytecode
    proc_stack = []
    stack = []
    ip = 0
    while True:
        instr = bytecode.code[ip]
        ip += 1
        if instr == OpCode.CONST_1.value:
            index = bytecode.code[ip]
            ip += 1
            stack.append(bytecode.constants[index])
        elif instr == OpCode.CONST_3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            stack.append(bytecode.constants[index])
        elif instr == OpCode.READ_VAR_1.value:
            index = bytecode.code[ip]
            ip += 1
            stack.append(env[bytecode.variables[index]])
        elif instr == OpCode.READ_VAR_3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            stack.append(env[bytecode.variables[index]])
        elif instr == OpCode.RET.value:
            if proc_stack:
                bytecode, ip, env = proc_stack.pop()
            else:
                assert len(stack) == 1
                return stack[0]
        elif instr == OpCode.DROP.value:
            stack.pop()
        elif instr == OpCode.CALL_1.value:
            num_args = bytecode.code[ip]
            ip += 1
            stack, proc, args = pop_proc_args(stack, num_args)
            if isinstance(proc, Closure):
                bindings = bind_formals(proc.bytecode, args)
                proc_stack.append((bytecode, ip, env))
                bytecode = proc.bytecode
                ip = 0
                env = types.Environment(parent=proc.env, bindings=bindings)
            else:
                result = proc(*args)
                stack.append(result)
        elif instr == OpCode.CALL_3.value:
            num_args = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            stack, proc, args = pop_proc_args(stack, num_args)
            if isinstance(proc, Closure):
                bindings = bind_formals(proc.bytecode, args)
                proc_stack.append((bytecode, ip, env))
                bytecode = proc.bytecode
                ip = 0
                env = types.Environment(parent=proc.env, bindings=bindings)
            else:
                result = proc(*args)
                stack.append(result)
        elif instr == OpCode.JUMP_IF_NOT_3.value:
            new_pos = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            condition = stack.pop()
            if base.is_false(condition):
                ip = new_pos
        elif instr == OpCode.JUMP_3.value:
            new_pos = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip = new_pos
        elif instr == OpCode.DEFINE_1.value:
            index = bytecode.code[ip]
            ip += 1
            value = stack.pop()
            env.define(bytecode.variables[index], value)
        elif instr == OpCode.DEFINE_3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            value = stack.pop()
            env.define(bytecode.variables[index], value)
        elif instr == OpCode.SET_VAR_1.value:
            index = bytecode.code[ip]
            ip += 1
            value = stack.pop()
            env.set_(bytecode.variables[index], value)
        elif instr == OpCode.SET_VAR_3.value:
            index = int.from_bytes(bytecode.code[ip:ip+3], byteorder='big')
            ip += 3
            value = stack.pop()
            env.set_(bytecode.variables[index], value)
        elif instr == OpCode.PUSH_FALSE.value:
            stack.append(False)
        elif instr == OpCode.MAKE_CLOSURE.value:
            bytecode_const = stack.pop()
            closure = Closure(bytecode_const, env=env)
            stack.append(closure)
        else:
            raise EvalError("Unknown bytecode: 0x{:02x}".format(instr))


def eval(exprs, *, env):
    """Evaluate list of scheme exprs.

    Compile and execute 'exprs' - list of Scheme expressions
    in environment 'env'.
    """
    bytecode = compile.compile(exprs, env=env)
    result = run(Closure(bytecode, env=env))
    return result
