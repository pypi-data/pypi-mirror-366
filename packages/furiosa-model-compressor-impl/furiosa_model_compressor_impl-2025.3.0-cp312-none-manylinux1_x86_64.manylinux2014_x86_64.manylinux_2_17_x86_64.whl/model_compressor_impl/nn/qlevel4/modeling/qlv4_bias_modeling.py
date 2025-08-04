from typing import Any

import torch
from torch import Tensor, nn

__all__ = ["QLV4_BIAS_MOD"]


class QLV4_BIAS_MOD(nn.Module):
    def __init__(self, bias, emul_dtype=None) -> None:
        super().__init__()
        self.register_buffer('bias', bias)
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        # dtype of bias input is int32 or fp32
        if self.bias is None:
            return input
        _input = input
        _bias = self.bias

        if self.emul_dtype is not None:
            # type cast
            _input = torch.ops.aten._to_copy(_input, dtype=self.emul_dtype)
            _bias = torch.ops.aten._to_copy(_bias, dtype=self.emul_dtype)

        output = torch.ops.aten.add.Tensor(_input, _bias)

        return output
