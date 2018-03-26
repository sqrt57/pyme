"""Pyme exceptions."""


class PymeException(Exception):
    """Base Pyme exception.

    This is the root of Pyme exceptions hierarchy.
    """
    pass


class ReaderError(PymeException):
    """Lexical or syntax error."""
    pass


class EvalError(PymeException):
    """Runtime eval error."""
    pass


class IdentifierNotBoundError(EvalError):
    """Identifier not bound."""
    pass


class CompileError(PymeException):
    """Error compiling source."""
    pass
