
class PymeException(Exception):
    pass


class ReaderError(PymeException):
    pass


class EvalError(PymeException):
    pass


class IdentifierNotBoundError(EvalError):
    pass