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
            registry.builtins, symbol_table=self._symbol_table)

    def eval_str(self, string):
        in_port = ports.TextStreamPort(io.StringIO(string))
        result = False
        while True:
            expr = self._reader.read(in_port)
            if base.eofp(expr):
                return result
            result = eval.eval(expr, env=self._global_env)
