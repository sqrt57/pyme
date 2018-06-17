from pyme.registry import builtin


@builtin("make-bytevector")
def make_bytevector(k, byte=0):
    return bytearray([byte] * k)


@builtin("bytevector")
def bytevector(*args):
    return bytearray(args)
