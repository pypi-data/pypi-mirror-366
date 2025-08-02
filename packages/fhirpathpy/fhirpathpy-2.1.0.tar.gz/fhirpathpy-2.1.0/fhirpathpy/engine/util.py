from decimal import Decimal
import json
from collections import OrderedDict
from functools import reduce
from fhirpathpy.engine.nodes import ResourceNode, FP_Quantity


class set_paths:
    def __init__(self, func, parsedPath, model=None, options=None):
        self.func = func
        self.parsedPath = parsedPath
        self.model = model
        self.options = options

    def __call__(self, resource, context=None):
        return self.func(
            resource, self.parsedPath, context or {}, self.model, self.options
        )


def get_data(value):
    if isinstance(value, ResourceNode):
        value = value.data

    if isinstance(value, float):
        return Decimal(str(value))
    return value


def parse_value(value):
    def parse_complex_value(v):
        num_value, unit = v.get("value"), v.get("code")
        return FP_Quantity(num_value, f"'{unit}'") if num_value and unit else None

    return (
        parse_complex_value(value.data)
        if getattr(value, "get_type_info", lambda: None)()
        and value.get_type_info().name == "Quantity"
        else value
    )


def is_number(value):
    return isinstance(value, (int, Decimal, complex)) and not isinstance(value, bool)


def is_capitalized(x):
    return isinstance(x, str) and x[0] == x[0].upper()


def is_empty(x):
    return isinstance(x, list) and len(x) == 0


def is_some(x):
    return x is not None and not is_empty(x)


def is_nullable(x):
    return x is None or is_empty(x)


def is_true(x):
    return x == True or isinstance(x, list) and len(x) == 1 and x[0] == True


def arraify(x, instead_none=None):
    if isinstance(x, list):
        return x
    if is_some(x):
        return [x]
    return [] if instead_none is None else [instead_none]


def flatten(x):
    def func(acc, x):
        if isinstance(x, list):
            acc = acc + x
        else:
            acc.append(x)

        return acc

    return reduce(func, x, [])


def uniq(arr):
    # Strong type fast implementation for unique values that preserves ordering
    ordered_dict = OrderedDict()
    for x in arr:
        try:
            key = json.dumps(x, sort_keys=True)
        except TypeError:
            key = str(x)
        ordered_dict[key] = x
    return list(ordered_dict.values())


def val_data_converted(val):
    if isinstance(val, ResourceNode):
        val = val.convert_data()

    return val


def process_user_invocation_table(table):
    return {
        name: {
            **entity,
            "fn": lambda ctx, inputs, *args, __fn__=entity["fn"]: __fn__(
                [get_data(i) for i in inputs], *args
            ),
        }
        for name, entity in table.items()
    }
