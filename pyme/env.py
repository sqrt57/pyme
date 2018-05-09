from pyme import base
from pyme import interop
from pyme import types
from pyme.registry import builtin, builtin_with_interpreter


@builtin("environment?")
def environmentp(obj):
    return isinstance(obj, types.Environment)


@builtin("empty-environment")
def empty_environment():
    return types.Environment()


@builtin_with_interpreter("global-environment")
def empty_environment(interpreter):
    def inner_empty_environment():
        return interpreter.global_env
    return inner_empty_environment


@builtin("copy-environment")
def copy_environment(env):
    return types.Environment(parent=env.parent, bindings=dict(env.bindings))


@builtin("get-environment-parent")
def env_parent(env):
    if env.parent is None:
        return False
    else:
        return env.parent


@builtin("set-environment-parent!")
def set_env_parent(env, parent):
    if parent:
        env.parent = parent
    else:
        env.parent = None
    return False


@builtin("has-environment-binding?")
def has_environment_binding(env, key):
    return key in env.bindings


@builtin("get-environment-binding")
def get_environment_binding(env, key, default=False):
    return env.bindings.get(key, default)


@builtin("set-environment-binding!")
def set_environment_binding(env, key, value):
    env.bindings[key] = value
    return False


@builtin("delete-environment-binding!")
def delete_environment_binding(env, key):
    env.bindings.pop(key, None)
    return False


@builtin("get-environment-bindings")
def get_environment_bindings(env):
    items = [base.cons(key, value) for key, value in env.bindings.items()]
    return interop.scheme_list(items)


@builtin("clear-environment-bindings!")
def clear_environment_bindings(env):
    env.bindings.clear()
    return False
