import inspect
import typing

import torch

if torch.__version__ < '2.4':
    from torch._custom_op.impl import SUPPORTED_PARAM_TYPES, SUPPORTED_RETURN_TYPES
else:
    from torch._library.infer_schema import SUPPORTED_PARAM_TYPES, SUPPORTED_RETURN_TYPES


def op_name(func: typing.Callable) -> str:
    return func.__name__


def infer_schema(prototype_function: typing.Callable) -> str:
    sig = inspect.signature(prototype_function)

    def error_fn(what):
        raise ValueError(f'custom_op(...)(func): {what} ' f'Got func with signature {sig})')

    params = [parse_param(name, param, error_fn) for name, param in sig.parameters.items()]
    ret = parse_return(sig.return_annotation, error_fn)
    return f"({', '.join(params)}) -> {ret}"


def supported_param(param: inspect.Parameter) -> bool:
    return param.kind in (
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        inspect.Parameter.KEYWORD_ONLY,
    )


def parse_param(name, param, error_fn):
    if not supported_param(param):
        error_fn('We do not support positional-only args, varargs, or varkwargs.')

    if param.annotation is inspect.Parameter.empty:
        error_fn(f'Parameter {name} must have a type annotation.')

    if param.annotation not in SUPPORTED_PARAM_TYPES.keys():
        error_fn(
            f'Parameter {name} has unsupported type {param.annotation}. '
            f'The valid types are: {SUPPORTED_PARAM_TYPES.keys()}.'
        )

    if param.default is not inspect.Parameter.empty:
        error_fn(
            f'Parameter {name} has a default value; this is not supported. '
            f'If you want to use default values then create a function with '
            f'default values that calls the CustomOp'
        )

    return f'{SUPPORTED_PARAM_TYPES[param.annotation]} {name}'


def parse_return(annotation, error_fn):
    origin = typing.get_origin(annotation)
    if origin is not tuple:
        if annotation not in SUPPORTED_RETURN_TYPES.keys():
            error_fn(
                f'Return has unsupported type {annotation}. '
                f'The valid types are: {SUPPORTED_RETURN_TYPES}.'
            )
        return SUPPORTED_RETURN_TYPES[annotation]

    args = typing.get_args(annotation)
    for arg in args:
        if arg not in SUPPORTED_RETURN_TYPES:
            error_fn(
                f'Return has unsupported type {annotation}. '
                f'The valid types are: {SUPPORTED_RETURN_TYPES}.'
            )

    return '(' + ', '.join([SUPPORTED_RETURN_TYPES[arg] for arg in args]) + ')'
