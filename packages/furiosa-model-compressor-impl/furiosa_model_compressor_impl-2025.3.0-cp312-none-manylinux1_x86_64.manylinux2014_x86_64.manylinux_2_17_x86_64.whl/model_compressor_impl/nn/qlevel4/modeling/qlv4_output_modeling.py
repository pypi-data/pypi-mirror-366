from typing import Any

import torch
from torch import Tensor, nn

__all__ = ["QLV4_Output_MOD"]


_O_DTYPE = {
    'int8': torch.int8,
    'bf16': torch.bfloat16,
    'fp32': torch.float32,
    'int32': torch.int32,
    'int64': torch.int64,
    'fp8-E4M3': torch.int8,
    'auto': 'auto',
}


class QLV4_Output_MOD(nn.Module):
    def __init__(self, qlv3_output_quantizer=None) -> None:
        super().__init__()

        # dumping 기능
        self.skip_rounding = False
        self.run_dumping = False
        self.dumping_before_rounding = False
        self.dumped_data = None

        output_quant_dict = qlv3_output_quantizer
        self.bypass = False

        if output_quant_dict is None or len(output_quant_dict) == 0:
            self.dtype = None  # TODO : tmp
            self.bypass = True
            self.o_dtype = None
            return

        quant_desc = output_quant_dict["quant_desc"]

        self.real_dtype = quant_desc.dtype
        self.dequant = output_quant_dict['_dequantize']
        self.dequant_output_dtype = output_quant_dict['dequant_output_dtype']

        # bypass type quantizer 는 미리 삭제되어 있어야함
        if self.real_dtype == 'auto':
            self.dtype = None  # TODO : tmp
            self.bypass = True
            self.o_dtype = None
            return

        self.o_dtype = torch.float64 if self.real_dtype in ['int4'] else _O_DTYPE[self.real_dtype]

        # TODO : scale zp 가 생성time 에 존재하지 않는다... qlv3 real quant 로 변환시 미리 다 계산해놓도록 변경 필요!
        self.register_buffer('scale', output_quant_dict["_merged_scale"], persistent=False)
        self.register_buffer('zero_point', output_quant_dict["_zero_point"], persistent=False)
        self.do_input_scale = '_scale_per_channel' in output_quant_dict
        self.num_bits = quant_desc.num_bits
        self.dtype = quant_desc.dtype

        return

    def forward(self, input: Tensor) -> Tensor:
        quantized = input
        if self.bypass:
            if self.run_dumping:
                output_key = 'output_before_rounding' if self.dumping_before_rounding else 'output'
                self.dumped_data = {
                    output_key: input.to('cpu') if hasattr(input, 'to') else input,
                    'output_cast_dtype': self.o_dtype,
                }

            return quantized

        # TODO : temp impl
        if self.dequant:
            _dequant_output_dtype = _O_DTYPE[self.dequant_output_dtype]
            quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
            if self.real_dtype != 'fp8-E4M3':
                quantized = torch.ops.aten.sub.Tensor(quantized, self.zero_point)
            quantized = torch.ops.aten.mul.Tensor(
                quantized, self.scale
            )  # (input - zeropoint) * scale

            quantized = torch.ops.aten._to_copy(quantized, dtype=_dequant_output_dtype)

            if self.run_dumping:
                output_key = 'output_before_rounding' if self.dumping_before_rounding else 'output'
                self.dumped_data = {
                    output_key: input.to('cpu') if hasattr(input, 'to') else input,
                    'output_cast_dtype': self.o_dtype,
                }
            # return input

            return quantized

        # TODO : 임시 주석처리
        # if not isinstance(input, torch.Tensor) or input.dtype == torch.int64:
        #     if self.run_dumping:
        #         output_key = 'output_before_rounding' if self.dumping_before_rounding else 'output'
        #         self.dumped_data = {
        #             output_key: input,
        #             'output_cast_dtype': self.o_dtype,
        #         }
        #     return input

        # Computation must be over FP32 to prevent potential over flow.
        if self.dtype not in ['bf16', 'fp32', 'int32', 'int64']:

            # Type cast for VE
            quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
            quantized = torch.ops.aten.divide.Tensor(quantized, self.scale)

            # quantized = torch.ops.aten.add.Tensor(
            #     quantized, self.zero_point
            # )
            # # quantized = torch.zeros(_input.shape)
            # # for batch_idx in range(_input.shape[0]): #iterate through tensor along the batch axis
            # #     quantized[batch_idx] = torch.ops.aten.divide.Tensor(_input[batch_idx], self.scale)

            if self.dtype != 'fp8-E4M3':
                quantized = torch.ops.aten.add.Tensor(
                    quantized, self.zero_point
                )  # input / scale + zeropoint

                min_bound = -(2 ** (self.num_bits - 1))
                max_bound = 2 ** (self.num_bits - 1) - 1

                if self.run_dumping and self.dumping_before_rounding:
                    self.dumped_data = {
                        'output_before_rounding': quantized,
                        'output_cast_dtype': self.o_dtype,
                    }

                if not self.skip_rounding:
                    quantized = torch.ops.furiosa.away_from_zero_fp2fxp(quantized)
                    quantized = torch.ops.aten.clamp(quantized, min_bound, max_bound)
            else:
                quantized = torch.ops.furiosa.fp32_to_fp8_cast(quantized)
        elif self.dtype == 'bf16' and self.do_input_scale:
            quantized = torch.ops.aten._to_copy(quantized, dtype=torch.float32)
            quantized = torch.ops.aten.divide.Tensor(quantized, self.scale)

        if self.run_dumping and self.dumping_before_rounding and self.dumped_data is None:
            self.dumped_data = {
                'output_before_rounding': quantized,
                'output_cast_dtype': self.o_dtype,
            }

        if (
            self.real_dtype not in ['int4', 'fp8-E4M3']
            and quantized.dtype != self.o_dtype
            and not self.skip_rounding
        ):
            quantized = torch.ops.aten._to_copy(
                quantized, dtype=self.o_dtype
            )  # type cast for next ops

        if self.run_dumping and not self.dumping_before_rounding:
            self.dumped_data = {
                'output': quantized,
                'output_cast_dtype': self.o_dtype,
            }

        return quantized
