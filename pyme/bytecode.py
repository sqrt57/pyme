import math
from enum import IntEnum, auto


class OpCode(IntEnum):
    """Operation code."""

    CONST_1 = auto()
    CONST_3 = auto()
    READ_VAR_1 = auto()
    READ_VAR_3 = auto()
    RET = auto()
    DROP = auto()
    CALL_1 = auto()
    CALL_3 = auto()
    TAIL_CALL_1 = auto()
    TAIL_CALL_3 = auto()
    JUMP_IF_NOT_3 = auto()
    JUMP_3 = auto()
    DEFINE_1 = auto()
    DEFINE_3 = auto()
    SET_VAR_1 = auto()
    SET_VAR_3 = auto()
    PUSH_FALSE = auto()
    MAKE_CLOSURE = auto()
    APPLY = auto()


opcode_num_args = {
    OpCode.CONST_1: 1,
    OpCode.CONST_3: 3,
    OpCode.READ_VAR_1: 1,
    OpCode.READ_VAR_3: 3,
    OpCode.RET: 0,
    OpCode.DROP: 0,
    OpCode.CALL_1: 1,
    OpCode.CALL_3: 3,
    OpCode.TAIL_CALL_1: 1,
    OpCode.TAIL_CALL_3: 3,
    OpCode.JUMP_IF_NOT_3: 3,
    OpCode.JUMP_3: 3,
    OpCode.DEFINE_1: 1,
    OpCode.DEFINE_3: 3,
    OpCode.SET_VAR_1: 1,
    OpCode.SET_VAR_3: 3,
    OpCode.PUSH_FALSE: 0,
    OpCode.MAKE_CLOSURE: 0,
}


class Bytecode:
    """Bytecode for Scheme function or code block."""

    def __init__(self):
        """Create empty bytecode."""
        self.code = bytearray()
        self.constants = []
        self.variables = []
        self.formals = []
        self.formals_rest = None

    def append(self, byte):
        self.code.append(byte)

    def position(self):
        return len(self.code)

    def extend(self, bytes_):
        self.code.extend(bytes_)

    def truncate_by(self, length):
        del self.code[len(self.code) - length:]

    def add_constant(self, value):
        pos = len(self.constants)
        self.constants.append(value)
        return pos

    def add_variable(self, value):
        pos = len(self.variables)
        self.variables.append(value)
        return pos


def decompile_code_inner(bytecode, *, result, prefix):
    l = math.ceil(math.log10(len(bytecode.code) + 1))
    ip = 0
    result.append("{0}formals = {1}".format(prefix, bytecode.formals))
    result.append("{0}formals_rest = {1}".format(prefix, bytecode.formals_rest))
    result.append("{0}constants = {1}".format(prefix, bytecode.constants))
    result.append("{0}variables = {1}".format(prefix, bytecode.variables))
    while ip < len(bytecode.code):
        instr = OpCode(bytecode.code[ip])
        n = opcode_num_args[instr]
        if n > 0:
            arg = int.from_bytes(bytecode.code[ip+1:ip+n+1], byteorder='big')
            result.append("{0}{1:0{2}}: {3:10} {4}".format(
                prefix, ip, l, instr.name, arg))
            ip += n + 1
        else:
            result.append("{0}{1:0{2}}: {3:10}".format(
                prefix, ip, l, instr.name))
            ip += 1
    result.append(prefix)
    for i, const in enumerate(bytecode.constants):
        if isinstance(const, Bytecode):
            result.append("{0}constants[{1}]:".format(prefix, i))
            decompile_code_inner(const, result=result, prefix=prefix+".   ")


def decompile_code(bytecode):
    result = [""]
    decompile_code_inner(bytecode, result=result, prefix="")
    return "\n".join(result)
