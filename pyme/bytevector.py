from pyme import exceptions
from pyme.registry import builtin


@builtin("make-bytevector")
def make_bytevector(k, byte=0):
    return bytearray([byte] * k)


@builtin("bytevector")
def bytevector(*args):
    return bytearray(args)


@builtin("bytevector-length")
def bytevector_length(bytevector):
    return len(bytevector)


@builtin("bytevector-u8-ref")
def bytevector_u8_ref(bytevector, k):
    return bytevector[k]


@builtin("bytevector-u8-set!")
def bytevector_u8_set(bytevector, k, byte):
    bytevector[k] = byte
    return False


@builtin("bytevector-u16-le-set!")
def bytevector_u16_le_set(bytevector, k, value):
    if k < 0 or k+2 > len(bytevector):
        raise exceptions.EvalError("bytevector-u16-le-set!: cannot write outside of bytevector bounds")
    bytevector[k : k+2] = value.to_bytes(2, byteorder='little', signed=False)
    return False


@builtin("bytevector-u32-le-set!")
def bytevector_u32_le_set(bytevector, k, value):
    if k < 0 or k+4 > len(bytevector):
        raise exceptions.EvalError("bytevector-u32-le-set!: cannot write outside of bytevector bounds")
    bytevector[k : k+4] = value.to_bytes(4, byteorder='little', signed=False)
    return False


@builtin("bytevector-copy")
def bytevector_copy(bytevector, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(bytevector)

    if end > len(bytevector):
        raise exceptions.EvalError("bytevector-copy: end should be less or equal to bytevector length")
    if start > end:
        raise exceptions.EvalError("bytevector-copy: end should be greater or equal to start")
    if start < 0:
        raise exceptions.EvalError("bytevector-copy: start should be non-negative")

    return bytevector[slice(start, end)]


@builtin("bytevector-copy!")
def bytevector_copy_(to, at, from_, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(from_)

    if end > len(from_):
        raise exceptions.EvalError("bytevector-copy!: end should be less or equal to source length")
    if start > end:
        raise exceptions.EvalError("bytevector-copy!: end should be greater or equal to start")
    if start < 0:
        raise exceptions.EvalError("bytevector-copy!: start should be non-negative")
    if at < 0:
        raise exceptions.EvalError("bytevector-copy!: at should be non-negative")
    if end - start > len(to) - at:
        raise exceptions.EvalError("bytevector-copy!: copied bytes should fit into destination")

    to[at : at + end - start] = from_[start:end]
    return False


@builtin("bytevector-append")
def bytevector_append(*bytevectors):
    return bytearray().join(bytevectors)


@builtin("utf8->string")
def utf8_to_string(bytevector, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(bytevector)

    if end > len(bytevector):
        raise exceptions.EvalError("utf8->string: end should be less or equal to bytevector length")
    if start > end:
        raise exceptions.EvalError("utf8->string: end should be greater or equal to start")
    if start < 0:
        raise exceptions.EvalError("utf8->string: start should be non-negative")

    return bytevector[slice(start, end)].decode()


@builtin("string->utf8")
def string_to_utf8(string, start=None, end=None):
    if start is None:
        start = 0
    if end is None:
        end = len(string)

    if end > len(string):
        raise exceptions.EvalError("string->utf8: end should be less or equal to string length")
    if start > end:
        raise exceptions.EvalError("string->utf8: end should be greater or equal to start")
    if start < 0:
        raise exceptions.EvalError("string->utf8: start should be non-negative")

    return bytearray(string[slice(start, end)].encode())
