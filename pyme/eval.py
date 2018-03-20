from abc import ABC, abstractmethod
import numbers

from pyme import base, exceptions, interop


def special(fun):
    fun.special = True
    return fun


def is_special(fun):
    return hasattr(fun, "special")


class ResultBox:

    def __init__(self):
        self.values = None


class Evaluator:

    def __init__(self, *, env):
        self._continuations = []
        self.env = env

    def push_continuation(self, continuation):
        self._continuations.append(continuation)

    def push_continuations(self, continuations):
        self._continuations.extend(continuations)


class Continuation(ABC):

    def __init__(self, *, result_to=None):
        self._result_box = result_to or ResultBox()

    @abstractmethod
    def eval(self, evaluator): pass

    @property
    def result_box(self):
        return self._result_box


class EvalContinuation(Continuation):

    def __init__(self, expr, *, result_to=None):
        super().__init__(result_to=result_to)
        self.expr = expr

    def eval(self, evaluator):
        if isinstance(self.expr, numbers.Integral):
            self.result_box.values = [self.expr]
        elif isinstance(self.expr, str):
            self.result_box.values = [self.expr]
        elif base.symbolp(self.expr):
            value = evaluator.env[self.expr]
            self.result_box.values = [value]
        elif base.pairp(self.expr):
            proc = self.expr.car
            args, rest = interop.from_scheme_list(self.expr.cdr)
            if not base.nullp(rest):
                msg = "Expected proper list in procedure application"
                raise exceptions.EvalError(msg)
            proc_cont = EvalContinuation(proc)
            proc_result = proc_cont.result_box
            apply_cont = ApplyProcOrSpecialContinuation(
                proc_result, args, result_to=self.result_box)
            evaluator.push_continuation(apply_cont)
            evaluator.push_continuation(proc_cont)
        else:
            raise TypeError("Cannot eval type " + type(self.expr).__name__)


class ApplyProcOrSpecialContinuation(Continuation):

    def __init__(self, proc_result, args, *, result_to=None):
        super().__init__(result_to=result_to)
        self.proc_result = proc_result
        self.args = args

    def eval(self, evaluator):
        proc = self.proc_result.values[0]
        if is_special(proc):
            proc(*self.args, evaluator=evaluator, result_to=self.result_box)
        else:
            arg_conts = [EvalContinuation(arg) for arg in self.args]
            arg_results = [arg_cont.result_box for arg_cont in arg_conts]
            apply_cont = ApplyContinuation(
                proc, arg_results, result_to=self.result_box)
            evaluator.push_continuation(apply_cont)
            evaluator.push_continuations(arg_conts)


class ApplyContinuation(Continuation):

    def __init__(self, proc, arg_results, *, result_to=None):
        super().__init__(result_to=result_to)
        self.proc = proc
        self.arg_results = arg_results

    def eval(self, evaluator):
        args = [arg.values[0] for arg in self.arg_results]
        result = self.proc(*args)
        self.result_box.values = [result]


class IfContinuation(Continuation):

    def __init__(self, if_result, then_, else_ , *, result_to=None):
        super().__init__(result_to=result_to)
        self.if_result = if_result
        self.then_ = then_
        self.else_ = else_

    def eval(self, evaluator):
        cond = self.if_result.values[0]
        branch = self.then_ if cond != False else self.else_
        cont = EvalContinuation(branch, result_to=self.result_box)
        evaluator.push_continuation(cont)


@special
def scheme_if(if_, then_, else_, *, evaluator, result_to):
    eval_cont = EvalContinuation(if_)
    if_cont = IfContinuation(
        eval_cont.result_box, then_, else_, result_to=result_to)
    evaluator.push_continuation(if_cont)
    evaluator.push_continuation(eval_cont)


@special
def quote(arg, *, evaluator, result_to):
    result_to.values = [arg]


def eval(expr, *, env):
    evaluator = Evaluator(env=env)
    continuation = EvalContinuation(expr)
    result_box = continuation.result_box
    evaluator.push_continuation(continuation)
    while evaluator._continuations:
        continuation = evaluator._continuations.pop()
        continuation.eval(evaluator)
    return result_box.values[0]
