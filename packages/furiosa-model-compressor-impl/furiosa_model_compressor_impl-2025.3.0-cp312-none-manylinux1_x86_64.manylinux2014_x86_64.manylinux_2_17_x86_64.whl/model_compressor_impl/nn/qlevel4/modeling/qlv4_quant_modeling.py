from typing import Any, Dict

import torch
from torch import Tensor
import torch.nn as nn

__all__ = ["QLV4_Quant_MOD"]


_O_DTYPE = {
    'int8': torch.int8,
    'bf16': torch.bfloat16,
    'fp32': torch.float32,
    'fp8-E4M3': torch.int8,
    'auto': 'auto',
}


class QLV4_Quant_MOD(nn.Module):
    def __init__(self, real_quantizer, node_name) -> None:
        super().__init__()

        quant_desc = real_quantizer.quant_desc

        self.real_dtype = quant_desc.dtype

        self.o_dtype = torch.float64 if self.real_dtype in ['int4'] else _O_DTYPE[self.real_dtype]

        self.register_buffer('scale', real_quantizer.merged_scale, persistent=False)
        self.register_buffer('zero_point', real_quantizer.zero_point, persistent=False)
        self.num_bits = quant_desc.num_bits
        self.dtype = quant_desc.dtype
        self.dequant = real_quantizer._dequantize
        self.dequant_output_dtype = real_quantizer.dequant_output_dtype
        self.node_name = node_name
        self.do_input_scale = hasattr(real_quantizer, '_scale_per_channel')

        # dumping 기능
        self.skip_rounding = False
        self.run_dumping = False
        self.dumping_before_rounding = False
        self.dumped_data = None

        return

    def forward(self, input: Tensor) -> Tensor:
        # TODO: temporal code fp32 이거나 identity 라면 미리 지워져야함
        if self.dtype == 'fp32':
            return input

        quantized = input

        if not self.dequant:
            if self.dtype != 'fp8-E4M3':
                if self.dtype != 'bf16':
                    quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
                    quantized = torch.ops.aten.divide.Tensor(quantized, self.scale)  # input / scale
                    quantized = torch.ops.aten.add.Tensor(
                        quantized, self.zero_point
                    )  # (input / scale) + zeropoint

                    min_bound = -(2 ** (self.num_bits - 1))
                    max_bound = 2 ** (self.num_bits - 1) - 1
                    quantized = torch.ops.furiosa.away_from_zero_fp2fxp(quantized)
                    quantized = torch.ops.aten.clamp(quantized, min_bound, max_bound)
                elif self.dtype == 'bf16' and self.do_input_scale:
                    quantized = torch.ops.aten.divide.Tensor(quantized, self.scale)

                quantized = torch.ops.aten._to_copy(quantized, dtype=self.o_dtype)
            else:
                quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
                quantized = torch.ops.aten.divide.Tensor(quantized, self.scale)  # input / scale
                quantized = torch.ops.furiosa.fp32_to_fp8_cast(
                    quantized
                )  # fp32 to fp8 (int8로 encoding)

        else:
            _dequant_output_dtype = _O_DTYPE[self.dequant_output_dtype]
            if self.dtype != 'fp8-E4M3':
                quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
                quantized = torch.ops.aten.sub.Tensor(quantized, self.zero_point)
                quantized = torch.ops.aten.mul.Tensor(
                    quantized, self.scale
                )  # (input - zeropoint) * scale
            else:
                # int8 to fp8 decoding
                quantized = torch.ops.furiosa.type_emulation_in(
                    quantized, 'fp8-E4M3', None, torch.float64
                )
                quantized = torch.ops.furiosa.type_emulation_out(quantized, torch.float32, None)

                # ve type casting and decoding
                quantized = torch.ops.aten.mul.Tensor(quantized, self.scale)

            quantized = torch.ops.aten._to_copy(quantized, dtype=_dequant_output_dtype)

        return quantized

        # Type cast for VE

        # quantized = torch.ops.aten.add.Tensor(
        #     quantized, self.zero_point
        # )
        # # quantized = torch.zeros(_input.shape)
        # # for batch_idx in range(_input.shape[0]): #iterate through tensor along the batch axis
        # #     quantized[batch_idx] = torch.ops.aten.divide.Tensor(_input[batch_idx], self.scale)

        if self.dtype != 'bf16' and self.dtype != 'fp32':
            min_bound = -(2 ** (self.num_bits - 1))
            max_bound = 2 ** (self.num_bits - 1) - 1

            if self.run_dumping and self.dumping_before_rounding:
                self.dumped_data = {
                    'output_before_rounding': (
                        quantized.to('cpu') if hasattr(quantized, 'to') else quantized
                    ),
                    'output_cast_dtype': self.o_dtype,
                }

            if not self.skip_rounding:
                quantized = torch.ops.furiosa.away_from_zero_fp2fxp(quantized)
                quantized = torch.ops.aten.clamp(quantized, min_bound, max_bound)

        if (
            self.real_dtype not in ['int4']
            and quantized.dtype != self.o_dtype
            and not self.skip_rounding
        ):
            quantized = torch.ops.aten._to_copy(
                quantized, dtype=self.o_dtype
            )  # type cast for next ops

        return quantized

    def get_qmeta(self) -> Dict:
        QUANT_CONFIG_KEYS = ['num_bits', 'dtype', 'dequant', 'dequant_output_dtype']
        qmeta = {}

        for child_name, child in self.named_children():
            tq_meta = {}
            for key in QUANT_CONFIG_KEYS:
                if hasattr(child, key):
                    tq_meta[key] = getattr(child, key)

            qmeta[child_name] = tq_meta

        return qmeta
