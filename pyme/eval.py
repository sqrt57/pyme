"""Evaluate Scheme code."""

import numbers
from abc import ABC, abstractmethod
from collections import namedtuple

from pyme import base
from pyme import compile
from pyme import interop
from pyme import types
from pyme.compile import OpCode
from pyme.exceptions import EvalError


Closure = namedtuple('Closure', ['bytecode', 'env'])


def _bind_formals(bytecode, args):
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


class Evaluator:
    """Scheme code evaluator."""
    def __init__(self, *, bytecode, env, hooks=None):
        self.call_stack = []
        self.stack = []
        self.bytecode = bytecode
        self.env = env
        self.ip = 0
        self.call_hook = interop.get_config(hooks, "eval.call")

    class Return(Exception):

        def __init__(self, value):
            self.value = value

    def pop_proc_args(self, num):
        if len(self.stack) < num + 1:
            raise EvalError("Not enough values on stack for procedure call")
        proc = self.stack[len(self.stack)-num-1]
        args = self.stack[len(self.stack)-num :]
        self.stack = self.stack[: len(self.stack)-num-1]
        return proc, args

    def do_apply(self, proc, args, *, tail):
        if isinstance(proc, Closure):
            bindings = _bind_formals(proc.bytecode, args)
            if not tail:
                self.call_stack.append((self.bytecode, self.ip, self.env))
            self.bytecode = proc.bytecode
            self.ip = 0
            self.env = types.Environment(parent=proc.env, bindings=bindings)
            if self.call_hook is not None:
                self.call_hook(self)
        else:
            result = proc(*args)
            self.stack.append(result)
            if tail:
                self.do_ret()

    def do_call(self, num_args, *, tail):
        proc, args = self.pop_proc_args(num_args)
        self.do_apply(proc, args, tail=tail)

    def do_ret(self):
        if self.call_stack:
            self.bytecode, self.ip, self.env = self.call_stack.pop()
        else:
            assert len(self.stack) == 1
            raise self.Return(self.stack[0])

    def step(self):
        instr = self.bytecode.code[self.ip]
        self.ip += 1
        if instr == OpCode.CONST_1.value:
            index = self.bytecode.code[self.ip]
            self.ip += 1
            self.stack.append(self.bytecode.constants[index])
        elif instr == OpCode.CONST_3.value:
            index = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                   byteorder='big')
            self.ip += 3
            self.stack.append(self.bytecode.constants[index])
        elif instr == OpCode.READ_VAR_1.value:
            index = self.bytecode.code[self.ip]
            self.ip += 1
            self.stack.append(self.env[self.bytecode.variables[index]])
        elif instr == OpCode.READ_VAR_3.value:
            index = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                   byteorder='big')
            self.ip += 3
            self.stack.append(self.env[self.bytecode.variables[index]])
        elif instr == OpCode.RET.value:
            self.do_ret()
        elif instr == OpCode.DROP.value:
            self.stack.pop()
        elif instr == OpCode.CALL_1.value:
            num_args = self.bytecode.code[self.ip]
            self.ip += 1
            self.do_call(num_args, tail=False)
        elif instr == OpCode.CALL_3.value:
            num_args = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                      byteorder='big')
            self.ip += 3
            self.do_call(num_args, tail=False)
        elif instr == OpCode.TAIL_CALL_1.value:
            num_args = self.bytecode.code[self.ip]
            self.ip += 1
            self.do_call(num_args, tail=True)
        elif instr == OpCode.TAIL_CALL_3.value:
            num_args = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                      byteorder='big')
            self.ip += 3
            self.do_call(num_args, tail=True)
        elif instr == OpCode.JUMP_IF_NOT_3.value:
            new_pos = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                     byteorder='big')
            self.ip += 3
            condition = self.stack.pop()
            if base.is_false(condition):
                self.ip = new_pos
        elif instr == OpCode.JUMP_3.value:
            new_pos = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                     byteorder='big')
            self.ip = new_pos
        elif instr == OpCode.DEFINE_1.value:
            index = self.bytecode.code[self.ip]
            self.ip += 1
            value = self.stack.pop()
            self.env.define(self.bytecode.variables[index], value)
        elif instr == OpCode.DEFINE_3.value:
            index = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                   byteorder='big')
            self.ip += 3
            value = self.stack.pop()
            self.env.define(self.bytecode.variables[index], value)
        elif instr == OpCode.SET_VAR_1.value:
            index = self.bytecode.code[self.ip]
            self.ip += 1
            value = self.stack.pop()
            self.env.set_(self.bytecode.variables[index], value)
        elif instr == OpCode.SET_VAR_3.value:
            index = int.from_bytes(self.bytecode.code[self.ip : self.ip+3],
                                   byteorder='big')
            self.ip += 3
            value = self.stack.pop()
            self.env.set_(self.bytecode.variables[index], value)
        elif instr == OpCode.PUSH_FALSE.value:
            self.stack.append(False)
        elif instr == OpCode.MAKE_CLOSURE.value:
            bytecode_const = self.stack.pop()
            closure = Closure(bytecode_const, env=self.env)
            self.stack.append(closure)
        else:
            raise EvalError("Unknown bytecode: 0x{:02x}".format(instr))

    def run(self):
        try:
            while True:
                self.step()
        except self.Return as e:
            return e.value


def eval(expr, *, env, hooks=None):
    """Evaluate scheme expr.

    Compile and execute Scheme expression 'expr'
    in environment 'env'.
    """
    bytecode = compile.compile(expr, env=env)
    evaluator = Evaluator(bytecode=bytecode, env=env, hooks=hooks)
    return evaluator.run()
