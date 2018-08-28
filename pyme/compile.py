from pyme import core
from pyme.core import TAIL
from pyme.drive import RunDriver
from pyme.compile_to_bytecode import BytecodeCompiler


class TailAttribute(core.Visitor):

    def __init__(self, tail):
        self.tail = tail

    def constant(self, element):
        element.attribute[TAIL] = self.tail

    def get_variable(self, element):
        element.attribute[TAIL] = self.tail

    def set_variable(self, element):
        element.attribute[TAIL] = self.tail
        element.value.accept(TailAttribute.false)

    def define_variable(self, element):
        element.attribute[TAIL] = self.tail
        element.value.accept(TailAttribute.false)

    def apply(self, element):
        element.attribute[TAIL] = self.tail
        element.proc.accept(TailAttribute.false)
        for arg in element.args:
            arg.accept(TailAttribute.false)
        for arg in element.kwargs.values():
            arg.accept(TailAttribute.false)

    def if_(self, element):
        element.attribute[TAIL] = self.tail
        element.condition.accept(TailAttribute.false)
        element.then_.accept(self)
        element.else_.accept(self)

    def block(self, element):
        element.attribute[TAIL] = self.tail
        if len(element.exprs) > 0:
            for expr in element.exprs[:-1]:
                expr.accept(TailAttribute.false)
            element.exprs[-1].accept(self)

    def lambda_(self, element):
        element.attribute[TAIL] = self.tail
        element.body.accept(TailAttribute.true)


TailAttribute.true = TailAttribute(True)


TailAttribute.false = TailAttribute(False)


def compile(expr, *, env):
    """Compile expr to Bytecode.

    'exprs' is a Scheme expression to compile.

    Use 'env' to resolve special forms while compiling expression.
    """
    driver = RunDriver(env=env)
    core_code = driver.compile_expr(expr)
    core_code.accept(TailAttribute.true)
    compiler = BytecodeCompiler()
    compiler.compile_expr(core_code)
    return compiler.bytecode
