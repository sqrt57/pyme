"""Registry for Pyme builtins."""


builtins = {}


def builtin(name):
    def named_builtin(fun):
        builtins[name] = fun
        return fun
    return named_builtin
