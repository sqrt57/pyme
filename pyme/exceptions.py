"""Pyme exceptions."""


class PymeException(Exception):
    """Base Pyme exception.

    This is the root of Pyme exceptions hierarchy.
    """
    pass


class ReaderError(PymeException):
    """Lexical or syntax error."""
    pass


class CompileError(PymeException):
    """Error compiling source."""
    pass


class EvalError(PymeException):
    """Runtime eval error."""
    pass


class IdentifierNotBoundError(EvalError):
    """Identifier not bound."""
    pass


class SchemeError(EvalError):
    """Identifier not bound."""

    def __init__(self, obj):
        super().__init__(obj)
        self.object = obj
