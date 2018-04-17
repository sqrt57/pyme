"""Top-level interpreter class."""

import io

from pyme import base
from pyme import eval
from pyme import interop
from pyme import ports
from pyme import reader
from pyme import registry
from pyme import types


class Interpreter:

    def __init__(self):
        self._symbol_table = types.SymbolTable()
        self._reader = reader.Reader(symbol_table=self._symbol_table)
        self._global_env = interop.str_bindings_to_env(
            self._default_builtins_dict, symbol_table=self._symbol_table)

    @property
    def _default_builtins_dict(self):
        result = dict(registry.builtins)
        result.update({
            key: value(self)
            for key, value in registry.builtins_with_interpreter.items()
        })
        return result

    def eval_port(self, in_port, env=None):
        if env is None:
            env = self._global_env
        result = False
        while True:
            expr = self._reader.read(in_port)
            if base.eofp(expr):
                return result
            result = eval.eval(expr, env=env)

    def eval_str(self, string, env=None):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(string))
        return self.eval_port(in_port, env=env)

    def eval_file(self, filename, env=None):
        with open(filename) as file:
            in_port = ports.TextStreamPort.from_stream(file)
            return self.eval_port(in_port, env=env)
