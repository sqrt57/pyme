"""Registry for Pyme builtins."""


builtins = {}


builtins_with_interpreter = {}


def builtin(name):
    def named_builtin(fun):
        builtins[name] = fun
        return fun
    return named_builtin


def builtin_with_interpreter(name):
    def named_builtin_with_interpreter(fun):
        builtins_with_interpreter[name] = fun
        return fun
    return named_builtin_with_interpreter
