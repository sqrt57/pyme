"""Top-level interpreter class."""

import io
import pathlib
import sys

from pyme import base
from pyme import env
from pyme import eval
from pyme import exceptions
from pyme import interop
from pyme import ports
from pyme import reader
from pyme import registry
from pyme import types
from pyme import write


class Interpreter:

    def __init__(self):
        self.symbol_table = types.SymbolTable()
        self.reader = reader.Reader(symbol_table=self.symbol_table)
        self.global_env = interop.str_bindings_to_env(
            self._default_builtins_dict, symbol_table=self.symbol_table)
        self.load_paths = [pathlib.Path.cwd()]
        self.stdout = ports.TextStreamPort.from_stream(sys.stdout)
        self.stdin = ports.TextStreamPort.from_stream(sys.stdin)
        self.stderr = ports.TextStreamPort.from_stream(sys.stderr)
        self.hooks = {
            "eval": {
                "call": None
            }
        }

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
            env = self.global_env
        result = False
        while True:
            expr = self.reader.read(in_port)
            if base.eofp(expr):
                return result
            result = eval.eval(expr, env=env,
                               hooks=self.hooks)

    def eval_stream(self, stream, env=None):
        in_port = ports.TextStreamPort.from_stream(stream)
        return self.eval_port(in_port, env=env)

    def eval_str(self, string, env=None):
        in_port = ports.TextStreamPort.from_stream(io.StringIO(string))
        return self.eval_port(in_port, env=env)

    def find_file(self, filename):
        for path in self.load_paths:
            subpath = path.joinpath(filename)
            if subpath.exists():
                return subpath
        return None

    def eval_file(self, filename, env=None):
        path = self.find_file(filename)
        if path is None:
            msg = f"load error: {filename} not found"
            raise exceptions.EvalError(msg)
        with path.open() as file:
            in_port = ports.TextStreamPort.from_stream(file)
            return self.eval_port(in_port, env=env)
