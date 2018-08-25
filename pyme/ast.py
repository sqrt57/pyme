
class Constant:

    def __init__(self, *, value):
        self.value = value

    def visit(self, visitor):
        return visitor.constant(value=self.value)


class VariableRef:

    def __init__(self, *, variable):
        self.variable = variable

    def visit(self, visitor):
        return visitor.variable_ref(variable=self.variable)


class GetVariable:

    def __init__(self, *, variable):
        self.variable = variable

    def visit(self, visitor):
        variable = self.variable.visit(visitor)
        return visitor.get_variable(variable=variable)


class SetVariable:

    def __init__(self, *, variable, value):
        self.variable = variable
        self.value = value

    def visit(self, visitor):
        variable = self.variable.visit(visitor)
        value = self.value.visit(visitor)
        return visitor.set_variable(variable=variable, value=value)


class DefineVariable:

    def __init__(self, *, variable, value):
        self.variable = variable
        self.value = value

    def visit(self, visitor):
        variable = self.variable.visit(visitor)
        value = self.value.visit(visitor)
        return visitor.define_variable(variable=variable, value=value)


class Apply:

    def __init__(self, *, proc, args, kwargs):
        self.proc = proc
        self.args = args
        self.kwargs = kwargs

    def visit(self, visitor):
        proc = self.proc.visit(visitor)
        args = [arg.visit(visitor) for arg in self.args]
        kwargs = {key: kwarg.visit(visitor)
                  for key, kwarg in self.kwargs.iteritems}
        return visitor.apply(proc=proc, args=args, kwargs=kwargs)


class If:

    def __init__(self, *, condition, then_, else_):
        self.condition = condition
        self.then_ = then_
        self.else_ = else_

    def visit(self, visitor):
        condition = self.condition.visit(visitor)
        then_ = self.then_.visit(visitor)
        else_ = self.else_.visit(visitor)
        return visitor.if_(condition=condition, then_=then_, else_=else_)


class Block:

    def __init__(self, *, exprs):
        self.exprs = exprs

    def visit(self, visitor):
        exprs = [expr.visit(visitor) for expr in self.exprs]
        return visitor.visit(exprs)


class Lambda:

    def __init__(self, *, name, args, rest_args, kwargs, rest_kwargs, body):
        self.name = name
        self.args = args
        self.rest_args = rest_args
        self.kwargs = kwargs
        self.rest_kwargs = rest_kwargs
        self.body = body

    def visit(self, visitor):
        body = self.body.visit(visitor)
        return visitor.lambda_(name=self.name,
                               args=self.args,
                               rest_args=self.rest_args,
                               kwargs=self.kwargs,
                               rest_kwargs=self.rest_kwargs,
                               body=body)
