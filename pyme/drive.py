"""Compile from Scheme source to abstract syntax tree."""

from pyme import core
from pyme import base
from pyme import interop
from pyme.exceptions import CompileError
from pyme.registry import builtin


class RunDriver:

    def __init__(self, *, env):
        self.env = env

    def compile_const(self, expr):
        return core.Constant(value=expr)

    def compile_variable(self, expr):
        return core.GetVariable(variable=expr)

    def compile_call(self, expr):
        proc = expr.car
        args = interop.from_scheme_list(expr.cdr)
        proc_binding = self.env.get(proc)
        if isinstance(proc_binding, _Builtin):
            return proc_binding.compile(self, *args)
        else:
            proc = self.compile_expr(proc)
            args = [self.compile_expr(arg) for arg in args]
            return core.Apply(proc=proc, args=args, kwargs={})

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
        return core.Block(exprs=exprs)

    def compile_if(self, condition, then_, else_):
        condition = self.compile_expr(condition)
        then_ = self.compile_expr(then_)
        else_ = self.compile_expr(else_)
        return core.If(condition=condition, then_=then_, else_=else_)

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
        return core.Lambda(name=False,
                           args=positional,
                           rest_args=formals_rest,
                           kwargs=None,
                           rest_kwargs=None,
                           body=body)

    def compile_define_var(self, var, value):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in variable definition")
        value = self.compile_expr(value)
        return core.DefineVariable(variable=var,
                                   value=value)

    def compile_define_proc(self, var, signature, *body):
        if not base.symbolp(var):
            raise CompileError("define: non-symbol in procedure definition")
        lambda_ = self.compile_lambda(signature, *body)
        return core.DefineVariable(variable=var,
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
        return core.SetVariable(variable=var,
                                value=value)


class _Builtin:

    def __init__(self, proc):
        self.proc = proc

    def compile(self, compiler, *args):
        return self.proc(compiler, *args)


class Builtins:

    IF = builtin("if")(_Builtin(RunDriver.compile_if))
    QUOTE = builtin("quote")(_Builtin(RunDriver.compile_const))
    LAMBDA = builtin("lambda")(_Builtin(RunDriver.compile_lambda))
    DEFINE = builtin("define")(_Builtin(RunDriver.compile_define))
    SET = builtin("set!")(_Builtin(RunDriver.compile_set_var))
