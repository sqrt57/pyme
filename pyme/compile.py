"""Compiler from Scheme source to bytecode."""

import collections
import math
from abc import ABC, abstractmethod
from enum import Enum, IntEnum, auto

from pyme import ast
from pyme import base
from pyme import interop
from pyme import types
from pyme.exceptions import CompileError
from pyme.registry import builtin


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
    TAIL_CALL_1 = auto()
    TAIL_CALL_3 = auto()
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
    OpCode.TAIL_CALL_1: 1,
    OpCode.TAIL_CALL_3: 3,
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
        lambda_ = Bytecode()
        lambda_.formals = expr.args
        lambda_.formals_rest = expr.rest_args
        self.outer_bytecodes.append(self.bytecode)
        self.bytecode = lambda_
        self.compile_block(expr.body, tail=True)
        self.bytecode = self.outer_bytecodes.pop()
        self.compile_const(lambda_, tail=False)
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


class ConcreteCompiler:

    def __init__(self, *, env):
        self.env = env

    def compile_const(self, expr):
        return ast.Constant(value=expr)

    def compile_variable(self, expr):
        return ast.GetVariable(variable=ast.VariableRef(variable=expr))

    def compile_call(self, expr):
        proc = expr.car
        args = interop.from_scheme_list(expr.cdr)
        proc_binding = self.env.get(proc)
        if isinstance(proc_binding, _Builtin):
            return proc_binding.compile(self, *args)
        else:
            proc = self.compile_expr(proc)
            args = [self.compile_expr(arg) for arg in args]
            return ast.Apply(proc=proc, args=args, kwargs={})

    def compile_expr(self, expr):
        if (base.numberp(expr) or base.stringp(expr)
                or base.booleanp(expr)):
            return self.compile_const(expr)
        elif base.symbolp(expr):
            return self.compile_variable(expr)
        elif base.pairp(expr):
            return self.compile_call(expr)
        else:
            msg = "Bad expr for compilation: {}".format(expr)
            raise CompileError(msg)

    def compile_block(self, exprs):
        exprs = [self.compile_expr(expr) for expr in exprs]
        return ast.Block(exprs=exprs)

    def compile_if(self, condition, then_, else_):
        condition = self.compile_expr(condition)
        then_ = self.compile_expr(then_)
        else_ = self.compile_expr(else_)
        return ast.If(condition=condition, then_=then_, else_=else_)

    def compile_lambda(self, formals, *body):
        formals = interop.from_scheme_list(formals)
        formals_rest = None
        formals_iter = iter(formals)
        positional = []
        for f in formals_iter:
            if base.keywordp(f) and f.name == ":rest":
                f = next(formals_iter, None)
                if not base.symbolp(f):
                    raise CompileError("lambda: expected rest argument name after :rest keyword")
                formals_rest = f
            elif base.symbolp(f):
                positional.append(f)
            else:
                raise CompileError(f"syntax error in lambda arguments list: {f}")
        body = self.compile_block(body)
        return ast.Lambda(name=False,
                          args=positional,
                          rest_args=formals_rest,
                          kwargs=None,
                          rest_kwargs=None,
                          body=body)

    def compile_define_var(self, var, value):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in variable definition")
        value = self.compile_expr(value)
        return ast.DefineVariable(variable=ast.VariableRef(variable=var),
                                  value=value)

    def compile_define_proc(self, var, signature, *body):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in procedure definition")
        lambda_ = self.compile_lambda(signature, *body)
        return ast.DefineVariable(variable=ast.VariableRef(variable=var),
                                  value=lambda_)

    def compile_define(self, lvalue, *rest):
        if base.symbolp(lvalue):
            if len(rest) < 1:
                raise CompileError(
                    "define: missing value for identifier")
            if len(rest) > 1:
                raise CompileError(
                    "define: multiple values for identifier")
            return self.compile_define_var(lvalue, rest[0])
        elif base.pairp(lvalue):
            return self.compile_define_proc(lvalue.car, lvalue.cdr, *rest)
        else:
            raise CompileError("define: invalid syntax")

    def compile_set_var(self, var, value):
        if not base.symbolp(var):
            raise CompileError("set!: non-symbol in variable assignment")
        value = self.compile_expr(value)
        return ast.SetVariable(variable=ast.VariableRef(variable=var),
                               value=value)


def compile(expr, *, env):
    """Compile expr to Bytecode.

    'exprs' is a Scheme expression to compile.

    Use 'env' to resolve special forms while compiling expression.
    """
    concrete_compiler = ConcreteCompiler(env=env)
    abstract_syntax_tree = concrete_compiler.compile_block([expr])
    compiler = Compiler()
    compiler.compile_block(abstract_syntax_tree, tail=True)
    return compiler.bytecode


class Builtins:

    IF = builtin("if")(_Builtin(ConcreteCompiler.compile_if))
    QUOTE = builtin("quote")(_Builtin(ConcreteCompiler.compile_const))
    LAMBDA = builtin("lambda")(_Builtin(ConcreteCompiler.compile_lambda))
    DEFINE = builtin("define")(_Builtin(ConcreteCompiler.compile_define))
    SET = builtin("set!")(_Builtin(ConcreteCompiler.compile_set_var))


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
