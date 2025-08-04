from typing import Callable, List

import torch


def wrap_func_with_type_emulation(
    inputs: List[torch.Tensor],
    input_types: List[str],
    output_type: torch.dtype,
    scope: str,
    scope_dtype: torch.dtype,
    opfunc: Callable,
):
    input_list = []
    for t, t_type in zip(inputs, input_types):
        s = torch.ops.furiosa.type_emulation_in(t, t_type, scope, scope_dtype)
        input_list.append(s)
    output = opfunc(*input_list)
    return torch.ops.furiosa.type_emulation_out(output, output_type, scope)
