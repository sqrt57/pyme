from pyme import base
from pyme import interop
from pyme import types
from pyme.exceptions import EvalError
from pyme.registry import builtin


@builtin("create-record-type")
def create_record_type(name, initialized_fields, other_fields):
    initialized_fields, rest = interop.from_scheme_list(initialized_fields)
    if not base.nullp(rest):
        raise EvalError("create-record-type: fields list should be a proper list")
    other_fields, rest = interop.from_scheme_list(other_fields)
    if not base.nullp(rest):
        raise EvalError("create-record-type: fields list should be a proper list")

    def record_init(self, *args):
        if len(args) != len(initialized_fields):
            raise TypeError(
                "wrong number of arguments: got {}, expected {}".format(
                    len(args), len(initialized_fields)))
        for f, value in zip(initialized_fields, args):
            setattr(self, f.name, value)
        for f in other_fields:
            setattr(self, f.name, False)

    record_type = type(name.name, (object,), {"__init__": record_init})

    def is_record_type(record):
        return isinstance(record, record_type)

    result = [record_type, is_record_type]

    for f in initialized_fields + other_fields:
        def field_getter_wrapper(field_name=f.name):
            def field_getter(record):
                return getattr(record, field_name)
            return field_getter

        def field_setter_wrapper(field_name=f.name):
            def field_setter(record, value):
                return setattr(record, field_name, value)
            return field_setter

        result.append(interop.scheme_list(
            [f, field_getter_wrapper(), field_setter_wrapper()]))

    return interop.scheme_list(result)
