from typing import Any

import torch
from torch import Tensor, nn

__all__ = ["QLV4_Input_MOD"]


class QLV4_Input_MOD(nn.Module):
    def __init__(self, emul_dtype, node_name, _real_dtype, _o_dtype, _input_quantizer) -> None:
        super().__init__()
        self.emul_dtype = emul_dtype
        self.real_dtype = _real_dtype
        self.o_dtype = _o_dtype

        input_quant_dict = _input_quantizer
        self.disabled = input_quant_dict['disabled']
        # self.scale = input_quant_dict["_merged_scale"]

        quant_desc = input_quant_dict["quant_desc"]
        self.scale = input_quant_dict["_merged_scale"]
        self.zero_point = input_quant_dict["_zero_point"]
        self.do_input_scale = '_scale_per_channel' in input_quant_dict
        self.num_bits = quant_desc.num_bits
        self.node_name = node_name

    def forward(self, input: Tensor) -> Tensor:
        if not isinstance(input, torch.Tensor):
            return input

        # Computation must be over FP32 to prevent potential over flow.
        if self.o_dtype not in [torch.bfloat16, torch.float32]:
            _input = input
            _scale = self.scale
            _zero_point = self.zero_point
            if self.emul_dtype == torch.float64:
                _input = torch.ops.aten._to_copy(_input, dtype=self.emul_dtype)
                _scale = torch.ops.aten._to_copy(_scale, dtype=self.emul_dtype)
                _zero_point = torch.ops.aten._to_copy(_zero_point, dtype=self.emul_dtype)

            quantized = torch.ops.aten.divide.Tensor(_input, _scale)
            quantized = torch.ops.aten.add.Tensor(
                quantized, _zero_point
            )  # input/ scale + zeropoint

            min_bound = -(2 ** (self.num_bits - 1))
            max_bound = 2 ** (self.num_bits - 1) - 1
            quantized = torch.ops.furiosa.away_from_zero_fp2fxp(quantized)
            quantized = torch.ops.aten.clamp(quantized, min_bound, max_bound)
        elif self.o_dtype == torch.bfloat16 and self.do_input_scale:
            _input = input
            _scale = self.scale
            if self.emul_dtype == torch.float64:
                _input = torch.ops.aten._to_copy(_input, dtype=self.emul_dtype)
                _scale = torch.ops.aten._to_copy(_scale, dtype=self.emul_dtype)

            quantized = torch.ops.aten.divide.Tensor(_input, _scale)
        else:
            quantized = input

        if self.real_dtype not in ['int4', 'float8'] and quantized.dtype != self.o_dtype:
            quantized = torch.ops.aten._to_copy(
                quantized, dtype=self.o_dtype
            )  # type cast for next ops

        return quantized
