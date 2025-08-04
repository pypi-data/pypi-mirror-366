from typing import Callable, List, Optional

from torch.library import Library

from .utils import infer_schema, op_name
from .verify import verify_dispatch_key

FURIOSA_LIB = Library('furiosa', 'DEF')


# TODO: support FURIOSA_LIB is sinlgeton library
def bring_lib(name_space: Optional[str]) -> Library:
    lib = FURIOSA_LIB if name_space is None else Library(name_space, 'FRAGMENT')

    return lib


def define(also_impl_cpu: bool = True, name_space: Optional[str] = None) -> Callable:
    lib = bring_lib(name_space)

    def inner(func):
        scheme = infer_schema(func)
        name = op_name(func)
        scheme_str = f'{name}{scheme}'
        lib.define(scheme_str)
        if also_impl_cpu:
            impl_custom_op(func, ['CPU'], name_space=name_space)
        return func

    return inner


def impl_custom_op(
    original_func: Callable,
    dispatch_keys: List[str],
    dispatched_func: Optional[Callable] = None,
    name_space: Optional[str] = None,
):
    lib = bring_lib(name_space)
    func_name = op_name(original_func)
    applied_func = dispatched_func if dispatched_func is not None else original_func
    for dispatch_key in dispatch_keys:
        verify_dispatch_key(dispatch_key)
        lib.impl(func_name, applied_func, dispatch_key)


def impl_abstract_custom_op(
    original_func: Optional[Callable] = None,
    name_space: Optional[str] = None,
):
    lib = bring_lib(name_space)

    def inner(abstract_func):
        func_name = op_name(original_func) if original_func is not None else op_name(abstract_func)
        lib.impl(func_name, abstract_func, 'Meta')
        return abstract_func

    return inner
