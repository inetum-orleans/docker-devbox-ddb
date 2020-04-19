from typing import Iterable, Union, TYPE_CHECKING

from dotty_dict import Dotty
from marshmallow import Schema
from marshmallow.fields import Nested, Dict, List

if TYPE_CHECKING:
    from ddb.feature import Feature


def _get_stop_fields_from_schema(schema: Schema, stack, ret):
    for field_name, field in schema.fields.items():
        stack.append(field_name)
        if isinstance(field, Dict):
            ret.append(tuple(stack))
        if isinstance(field, List):
            ret.append(tuple(stack))
        if isinstance(field, Nested):
            _get_stop_fields_from_schema(field.schema, stack, ret)
        stack.pop()


def _get_stop_fields(features: Iterable['Feature']):
    ret = []
    stack = []
    for feature in features:
        stack.append(feature.name)
        _get_stop_fields_from_schema(feature.schema(), stack, ret)
        stack.pop()

    return ret


def to_environ(data: Union[Dotty, dict], env_prefix) -> dict:
    """
    Export configuration to environment dict.
    """
    return _flatten(env_prefix, "_", "_%s_",
                    lambda x: str.upper(x).replace('-', '_'),
                    str,
                    data=dict(data))


def flatten(data: Union[Dotty, dict], prefix=None, sep=".", array_index_format="[%s]",
            key_transformer=None, value_transformer=None,
            stop_for_features=None) -> dict:
    """
    Export configuration to a flat dict.
    """
    stop_for = tuple(map(sep.join, _get_stop_fields(stop_for_features))) if stop_for_features is not None else ()

    return _flatten(prefix, sep, array_index_format,
                    key_transformer, value_transformer,
                    stop_for, data=dict(data))


def _flatten(prefix=None, sep=".", array_index_format="[%s]",
             key_transformer=None, value_transformer=None,
             stop_for=(), data=None, output=None) -> dict:
    if output is None:
        output = dict()

    if prefix is None:
        prefix = ""
    if key_transformer is None:
        key_transformer = lambda x: x
    if value_transformer is None:
        value_transformer = lambda x: x

    stop_recursion = False
    if prefix in stop_for:
        stop_recursion = True

    if not stop_recursion and isinstance(data, dict):
        for (name, value) in data.items():
            key_prefix = (prefix + sep if prefix else "") + key_transformer(name)
            key_prefix = key_transformer(key_prefix)

            _flatten(key_prefix, sep, array_index_format,
                     key_transformer, value_transformer,
                     stop_for, value, output)

    elif not stop_recursion and isinstance(data, list):
        i = 0
        for value in data:
            replace_prefix = (prefix if prefix else "") + (array_index_format % str(i))
            replace_prefix = key_transformer(replace_prefix)

            _flatten(replace_prefix, sep, array_index_format,
                     key_transformer, value_transformer,
                     stop_for, value, output)

            i += 1
    else:
        output[prefix] = value_transformer(data)

    return output
