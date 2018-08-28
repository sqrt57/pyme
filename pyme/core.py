from abc import ABC, abstractmethod


class Element(ABC):

    def __init__(self):
        self.attribute = {}

    @abstractmethod
    def accept(self, visitor):
        pass


class Constant(Element):

    def __init__(self, *, value):
        super().__init__()
        self.value = value

    def accept(self, visitor):
        return visitor.constant(self)


class GetVariable(Element):

    def __init__(self, *, variable):
        super().__init__()
        self.variable = variable

    def accept(self, visitor):
        return visitor.get_variable(self)


class SetVariable(Element):

    def __init__(self, *, variable, value):
        super().__init__()
        self.variable = variable
        self.value = value

    def accept(self, visitor):
        return visitor.set_variable(self)


class DefineVariable(Element):

    def __init__(self, *, variable, value):
        super().__init__()
        self.variable = variable
        self.value = value

    def accept(self, visitor):
        return visitor.define_variable(self)


class Apply(Element):

    def __init__(self, *, proc, args, kwargs):
        super().__init__()
        self.proc = proc
        self.args = args
        self.kwargs = kwargs

    def accept(self, visitor):
        return visitor.apply(self)


class If(Element):

    def __init__(self, *, condition, then_, else_):
        super().__init__()
        self.condition = condition
        self.then_ = then_
        self.else_ = else_

    def accept(self, visitor):
        return visitor.if_(self)


class Block(Element):

    def __init__(self, *, exprs):
        super().__init__()
        self.exprs = exprs

    def accept(self, visitor):
        return visitor.block(self)


class Lambda(Element):

    def __init__(self, *, name, args, rest_args, kwargs, rest_kwargs, body):
        super().__init__()
        self.name = name
        self.args = args
        self.rest_args = rest_args
        self.kwargs = kwargs
        self.rest_kwargs = rest_kwargs
        self.body = body

    def accept(self, visitor):
        return visitor.lambda_(self)


class Visitor(ABC):

    @abstractmethod
    def constant(self, element):
        pass

    @abstractmethod
    def get_variable(self, element):
        pass

    @abstractmethod
    def set_variable(self, element):
        pass

    @abstractmethod
    def define_variable(self, element):
        pass

    @abstractmethod
    def apply(self, element):
        pass

    @abstractmethod
    def if_(self, element):
        pass

    @abstractmethod
    def block(self, element):
        pass

    @abstractmethod
    def lambda_(self, element):
        pass


TAIL = "tail"
