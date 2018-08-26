from pyme.compile_to_ast import ConcreteCompiler
from pyme.compile_to_bytecode import BytecodeCompiler


def compile(expr, *, env):
    """Compile expr to Bytecode.

    'exprs' is a Scheme expression to compile.

    Use 'env' to resolve special forms while compiling expression.
    """
    concrete_compiler = ConcreteCompiler(env=env)
    abstract_syntax_tree = concrete_compiler.compile_expr(expr)
    compiler = BytecodeCompiler()
    compiler.compile_expr(abstract_syntax_tree, tail=True)
    return compiler.bytecode
