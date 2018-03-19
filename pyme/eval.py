from abc import ABC, abstractmethod
import numbers

from pyme import base, exceptions, interop


class Result:

    def __init__(self):
        self.values = None


class Continuation(ABC):

    def __init__(self, *, result=None):
        self._result = result or Result()

    @abstractmethod
    def eval(self, evaluator): pass

    @property
    def result(self):
        return self._result


class EvalContinuation(Continuation):

    def __init__(self, expr, *, result=None):
        super().__init__(result=result)
        self.expr = expr

    def eval(self, evaluator):
        if isinstance(self.expr, numbers.Integral):
            self.result.values = [self.expr]
        elif isinstance(self.expr, str):
            self.result.values = [self.expr]
        elif base.symbolp(self.expr):
            value = evaluator.env[self.expr]
            self.result.values = [value]
        elif base.pairp(self.expr):
            proc = self.expr.car
            args, rest = interop.from_scheme_list(self.expr.cdr)
            if not base.nullp(rest):
                raise exceptions.EvalError("Expected proper list in procedure application")
            proc_cont = EvalContinuation(proc)
            arg_conts = [EvalContinuation(arg) for arg in args]
            proc_result = proc_cont.result
            arg_results = [arg_cont.result for arg_cont in arg_conts]
            apply_cont = ApplyContinuation(proc_result, arg_results, result=self.result)
            evaluator.push_continuation(apply_cont)
            evaluator.push_continuations(arg_conts)
            evaluator.push_continuation(proc_cont)
        else:
            raise TypeError("Cannot eval type " + type(self.expr).__name__)


class ApplyContinuation(Continuation):

    def __init__(self, proc_result, arg_results, *, result=None):
        super().__init__(result=result)
        self.proc_result = proc_result
        self.arg_results = arg_results

    def eval(self, evaluator):
        proc = self.proc_result.values[0]
        args = [arg.values[0] for arg in self.arg_results]
        result = proc(*args)
        self.result.values = [result]


class Evaluator:

    def __init__(self, *, env):
        self._continuations = []
        self.env = env

    def eval(self, expr):
        while self._continuations:
            continuation = self._continuations.pop()
            continuation.run(self)

    def push_continuation(self, continuation):
        self._continuations.append(continuation)


    def push_continuations(self, continuations):
        self._continuations.extend(continuations)


def eval(expr, *, env):
    evaluator = Evaluator(env=env)
    continuation = EvalContinuation(expr)
    result = continuation.result
    evaluator.push_continuation(continuation)
    while evaluator._continuations:
        continuation = evaluator._continuations.pop()
        continuation.eval(evaluator)
    return result.values[0]
