from pyme import base
from pyme import interop
from pyme import write
from pyme.exceptions import EvalError
from pyme.registry import builtin


class RecordType:

    def __init__(self, name, initialized_fields, other_fields):
        self.name = name
        self.initialized_fields = initialized_fields
        self.other_fields = other_fields

    def write_to(self, port):
        port.write("#<record type ")
        port.write(self.name.name)
        port.write(">")

    def is_record_type(self, record):
        return isinstance(record, Record) and record.record_type == self

    def create_record(self, *args):
        return Record(self, *args)


class Record:

    def __init__(self, record_type, *args):
        self.record_type = record_type
        self.fields = {}
        if len(args) != len(record_type.initialized_fields):
            raise TypeError(
                "wrong number of arguments: got {}, expected {}".format(
                    len(args), len(record_type.initialized_fields)))
        for f, value in zip(record_type.initialized_fields, args):
            self.fields[f.name] = value
        for f in record_type.other_fields:
            self.fields[f.name] = False

    def __getitem__(self, name):
        return self.fields[name]

    def __setitem__(self, name, value):
        self.fields[name] = value

    def write_to(self, port):
        port.write("#<record ")
        port.write(self.record_type.name.name)
        for f, value in self.fields.items():
            port.write(" (")
            port.write(f)
            port.write(" ")
            write.write_to(value, port)
            port.write(")")
        port.write(">")


@builtin("create-record-type")
def create_record_type(name, initialized_fields, other_fields):
    initialized_fields, rest = interop.from_scheme_list(initialized_fields)
    if not base.nullp(rest):
        raise EvalError("create-record-type: fields list should be a proper list")
    other_fields, rest = interop.from_scheme_list(other_fields)
    if not base.nullp(rest):
        raise EvalError("create-record-type: fields list should be a proper list")
    return RecordType(name, initialized_fields, other_fields)


@builtin("record-type-name")
def record_type_name(record_type):
    return record_type.name


@builtin("record-constructor")
def record_constructor(record_type):
    return record_type.create_record


@builtin("record-type-checker")
def record_type_checker(record_type):
    return record_type.is_record_type


@builtin("record-field-getter")
def record_field_getter(field):
    def field_getter(record):
        return record[field.name]
    return field_getter


@builtin("record-field-setter")
def record_field_setter(field):
    def field_setter(record, value):
        record[field.name] = value
        return False
    return field_setter
