from abc import ABC, abstractmethod
import numbers

from pyme import base, exceptions, interop


class ResultBox:

    def __init__(self):
        self.values = None


class Continuation(ABC):

    def __init__(self, *, result_box=None):
        self._result_box = result_box or ResultBox()

    @abstractmethod
    def eval(self, evaluator): pass

    @property
    def result_box(self):
        return self._result_box


class EvalContinuation(Continuation):

    def __init__(self, expr, *, result_box=None):
        super().__init__(result_box=result_box)
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
                raise exceptions.EvalError("Expected proper list in procedure application")
            proc_cont = EvalContinuation(proc)
            arg_conts = [EvalContinuation(arg) for arg in args]
            proc_result = proc_cont.result_box
            arg_results = [arg_cont.result_box for arg_cont in arg_conts]
            apply_cont = ApplyContinuation(proc_result, arg_results, result_box=self.result_box)
            evaluator.push_continuation(apply_cont)
            evaluator.push_continuations(arg_conts)
            evaluator.push_continuation(proc_cont)
        else:
            raise TypeError("Cannot eval type " + type(self.expr).__name__)


class ApplyContinuation(Continuation):

    def __init__(self, proc_result, arg_results, *, result_box=None):
        super().__init__(result_box=result_box)
        self.proc_result = proc_result
        self.arg_results = arg_results

    def eval(self, evaluator):
        proc = self.proc_result.values[0]
        args = [arg.values[0] for arg in self.arg_results]
        result = proc(*args)
        self.result_box.values = [result]


class Evaluator:

    def __init__(self, *, env):
        self._continuations = []
        self.env = env

    def push_continuation(self, continuation):
        self._continuations.append(continuation)


    def push_continuations(self, continuations):
        self._continuations.extend(continuations)


def eval(expr, *, env):
    evaluator = Evaluator(env=env)
    continuation = EvalContinuation(expr)
    result_box = continuation.result_box
    evaluator.push_continuation(continuation)
    while evaluator._continuations:
        continuation = evaluator._continuations.pop()
        continuation.eval(evaluator)
    return result_box.values[0]
