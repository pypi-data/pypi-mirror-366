from typing import Any

import torch
from torch import Tensor, nn

__all__ = ["QLV3_MCM_BIAS_MOD"]

_float_dtype = [torch.bfloat16, torch.float32]


class QLV3_MCM_BIAS_MOD(nn.Module):
    _float_dtype = [torch.bfloat16, torch.float32]

    def __init__(self) -> None:
        super().__init__()
        self.emul_dtype_bias = None
        self.register_buffer('bias', None, persistent=False)
        self.register_parameter('imbias', None)

    def forward(self, input: Tensor) -> Tensor:
        _bias = self.bias
        _input = input

        if self.emul_dtype_bias is not None:
            _input = _input.to(self.emul_dtype_bias)
            _bias = _bias.to(self.emul_dtype_bias) if _bias is not None else None

        output = _input + _bias if _bias is not None else _input

        # if self.quant_enabled:
        #     output = self._output_quantizer(output)

        # output = output.to(self._o_dtype)  # Type cast for next node

        return output

    def golden_mode(self):
        self.emul_dtype_bias = torch.float64

    def set_emulation_dtype(self, emul_dtype):
        self.emul_dtype_bias = emul_dtype
