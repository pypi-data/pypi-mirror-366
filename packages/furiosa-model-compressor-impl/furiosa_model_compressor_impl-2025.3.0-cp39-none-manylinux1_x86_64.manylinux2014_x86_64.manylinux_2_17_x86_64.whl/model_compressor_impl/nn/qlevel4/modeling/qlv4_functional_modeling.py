#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Quantized Linear"""

import torch
from torch import nn

from ....utils import DATA_MATCHER
from ...custom_ops.wrap_fucn_with_custom_ops import wrap_func_with_type_emulation

__all__ = [
    "QLV4_Mul_MOD",
    "QLV4_Div_MOD",
    "QLV4_FloorDiv_MOD",
    "QLV4_TrueDiv_MOD",
    "QLV4_Add_MOD",
    "QLV4_Sub_MOD",
    "QLV4_Cumsum_MOD",
    "QLV4_MaskedFill_MOD",
    "QLV4_Mean_MOD",
    "QLV4_Pow_MOD",
    "QLV4_Rsqrt_MOD",
    "QLV4_Einsum_MOD",
    "QLV4_MatMul_MOD",
    "QLV4_FSoftmax_MOD",
    "QLV4_LogSoftmax_MOD",
    "QLV4_Fetch",
]


class QLV4_Mul_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr multiplication case
            return input_0 * input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(
                        input_0, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(
                        input_1, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.mul.Tensor(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.mul.Tensor(_input_0, _input_1)

        return output


class QLV4_Div_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr division case
            return input_0 / input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(input_0, dtype=self.emul_dtype)
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(input_1, dtype=self.emul_dtype)
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.div.Tensor(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.div.Tensor(_input_0, _input_1)

        return output


class QLV4_FloorDiv_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr division case
            return input_0 // input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(input_0, dtype=self.emul_dtype)
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(input_1, dtype=self.emul_dtype)
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.floor_divide(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.floor_divide(_input_0, _input_1)

        return output


class QLV4_TrueDiv_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr division case
            return input_0 // input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(input_0, dtype=self.emul_dtype)
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(input_1, dtype=self.emul_dtype)
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.true_divide(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.true_divide(_input_0, _input_1)

        return output


class QLV4_Add_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr addition case
            return input_0 + input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(
                        input_0, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(
                        input_1, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.add.Tensor(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.add.Tensor(_input_0, _input_1)

        return output


class QLV4_Sub_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input_0, input_1, **kwargs):
        if not isinstance(input_1, torch.Tensor) and not isinstance(input_0, torch.Tensor):
            # scalr addition case
            return input_0 - input_1
        else:
            _input_0 = input_0
            _input_1 = input_1
            if isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
                if input_0.dtype != torch.int64:
                    _input_0 = torch.ops.aten._to_copy(
                        input_0, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            elif not isinstance(input_0, torch.Tensor) and isinstance(input_1, torch.Tensor):
                if input_1.dtype != torch.int64:
                    _input_1 = torch.ops.aten._to_copy(
                        input_1, dtype=self.emul_dtype
                    )  # SRAM -> VE type cast
            else:
                if torch.int64 in (input_0.dtype, input_1.dtype):
                    return torch.ops.aten.sub.Tensor(input_0, input_1)

                _input_0 = torch.ops.aten._to_copy(
                    input_0, dtype=self.emul_dtype
                )  # SRAM -> VE type cast
                _input_1 = torch.ops.aten._to_copy(
                    input_1, dtype=self.emul_dtype
                )  # SRAM -> VE type cast

            output = torch.ops.aten.sub.Tensor(_input_0, _input_1)

        return output


class QLV4_Cumsum_MOD(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, input, dim, **kwargs):
        _input = input

        # VE type cast
        if torch.is_floating_point(input):
            if _input.dtype != torch.float32:
                _input = torch.ops.aten._to_copy(_input, dtype=torch.float32)
        else:
            if _input.dtype != torch.int32:
                _input = torch.ops.aten._to_copy(_input, dtype=torch.int32)

        output = torch.ops.aten.cumsum(_input, dim, **kwargs)

        return output


class QLV4_MaskedFill_MOD(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(
        self,
        input,
        mask,
        value,
    ):
        _input = input

        output = torch.ops.aten.masked_fill.Scalar(_input, mask, value)

        return output


class QLV4_Mean_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input, dim, **kwargs):
        if self.emul_dtype != input.dtype:
            _input = torch.ops.aten._to_copy(input, dtype=self.emul_dtype)
        else:
            _input = input

        output = torch.ops.aten.mean.dim(_input, dim, dtype=self.emul_dtype, **kwargs)

        return output


class QLV4_Pow_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input, exponent, **kwargs):
        if input.dtype == torch.bfloat16:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)  # Type cast for VE
        elif input.dtype == torch.float32:
            _input = input
        else:
            raise ValueError("Wrong input dtype. Pow allows bf16 and fp32 only!")

        if self.emul_dtype != _input.dtype:
            _input = torch.ops.aten._to_copy(_input, dtype=self.emul_dtype)

        output = torch.ops.aten.pow.Tensor_Scalar(_input, exponent)

        return output


class QLV4_Rsqrt_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input, **kwargs):
        if self.emul_dtype != input.dtype:
            _input = torch.ops.aten._to_copy(input, dtype=self.emul_dtype)
        else:
            _input = input
        output = torch.ops.aten.rsqrt(_input)

        return output


class QLV4_Einsum_MOD(nn.Module):
    def __init__(self, emul_dtype, node_name):
        super().__init__()
        self.emul_dtype = emul_dtype
        self.node_name = node_name

    def forward(self, equation, input_0, input_1, **kwargs):

        # VectorEngine에서 수행된다고 가정하고 구현합니다.
        # TODO: gpt-j/huggingface_rope 의 apply_rotary_pos_emb() 내부 einsum 만을 위한 특수 구현
        # TODO: Einsum을 DPE에서 구동하는 모드는 후에 optional하게 구현이 필요합니다.
        # TODO: input dtype이 integer의 경우 int32로 동작할 수 있게끔 해야 합니다.
        output = wrap_func_with_type_emulation(
            [input_0, input_1],
            ['float32', 'float32'],  # SRAM -> VE type cast
            torch.float32,
            self.node_name,
            self.emul_dtype,
            lambda x, y: torch.ops.aten.einsum(equation, [x, y]),
        )

        return output


class QLV4_Fetch(nn.Module):
    def __init__(self, node_name, quant_desc, zero_point):
        super().__init__()

        # TODO : kwargs 의 구조체 정의 필요
        quant_desc = quant_desc

        self.real_dtype = quant_desc.dtype
        # if self.dtype == 'int8':
        #     self.real_dtype = 'int9'
        # else:
        #     raise NotImplementedError("This case not implemented")

        self.register_buffer('zero_point', zero_point, persistent=False)
        self.node_name = node_name

    def forward(self, input):
        output = wrap_func_with_type_emulation(
            [input, self.zero_point],
            [DATA_MATCHER[self.real_dtype], DATA_MATCHER[self.real_dtype]],
            torch.int32,
            self.node_name,
            torch.float64,
            lambda x, y: torch.ops.aten.sub.Tensor(x, y),
        )

        return output


class QLV4_MatMul_MOD(nn.Module):
    def __init__(
        self,
        emul_dtype,
        node_name,
        input_0_dtype=None,
        input_1_dtype=None,
        qlv3_input_0_fetch=None,
        qlv3_input_1_fetch=None,
    ):
        super().__init__()
        self.emul_dtype = emul_dtype
        # self.register_buffer(
        #     'input1_scale',
        #     (
        #         kwargs['_input1_dequantizer']['_merged_scale']
        #         if '_input1_dequantizer' in kwargs
        #         else None
        #     ),
        # )

        # self.input0_real_dtype = kwargs["input0_real_dtype"]
        # self.input1_real_dtype = kwargs["input1_real_dtype"]
        # self.input0_dtype = kwargs['input0_dtype']
        # self.input1_dtype = kwargs['input1_dtype']
        # if self.input0_dtype == torch.bfloat16 and self.input1_dtype == torch.bfloat16:
        #     pass
        # elif self.input0_dtype == torch.bfloat16 and not self.input1_dtype.is_floating_point:
        #     self.register_buffer('zero_point', kwargs['_input1_dequantizer']['_zero_point'])
        # else:
        #     self.register_buffer('zero_point_0', kwargs["zero_point"][0])
        #     self.register_buffer('zero_point_1', kwargs["zero_point"][1])

        self.node_name = node_name

        # 임시구현!!!!!!
        if qlv3_input_0_fetch is not None and len(qlv3_input_0_fetch) == 0:
            self.input_0_real_dtype = input_0_dtype
            self.input_1_real_dtype = input_1_dtype
            self.output_dtype = torch.float32

            return

        # TODO :
        self.input_0_dtype = qlv3_input_0_fetch['quant_desc'].dtype
        self.input_1_dtype = qlv3_input_1_fetch['quant_desc'].dtype

        if self.input_0_dtype == 'int8':
            self.input_0_real_dtype = 'int9'
        elif self.input_0_dtype in ['fp32', 'bf16']:
            self.input_0_real_dtype = self.input_0_dtype
        else:
            raise NotImplementedError

        if self.input_1_dtype == 'int8':
            self.input_1_real_dtype = 'int9'
        elif self.input_1_dtype in ['fp32', 'bf16']:
            self.input_1_real_dtype = self.input_1_dtype
        else:
            raise NotImplementedError

        self.output_dtype = (
            torch.int32
            if (self.input_0_dtype == 'int8' and self.input_1_dtype == 'int8')
            else torch.float32
        )

    def forward(self, input_0, input_1, **kwargs):
        output = wrap_func_with_type_emulation(
            [input_0, input_1],
            [DATA_MATCHER[self.input_0_real_dtype], DATA_MATCHER[self.input_1_real_dtype]],
            self.output_dtype,
            self.node_name,
            self.emul_dtype,
            lambda x, y: torch.ops.aten.matmul(x, y),
        )

        return output


class QLV4_FSoftmax_MOD(nn.Module):
    def __init__(self, emul_dtype, node_name):
        super().__init__()
        self.emul_dtype = emul_dtype
        self.node_name = node_name

    def forward(self, input, dim=None, _stacklevel=3, dtype=None):
        # input dtype of softmax must be in [bf16, fp32, op integer(for debugging)]
        if input.dtype in [torch.bfloat16, torch.int8]:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)  # Type cast for VE
        else:
            _input = input

        if self.emul_dtype == torch.float64:
            output = wrap_func_with_type_emulation(
                [_input],
                ['float32'],
                torch.float32,
                self.node_name + '_softmax',
                self.emul_dtype,
                lambda x: torch.ops.aten._softmax(x, dim, False),
            )
        else:
            output = torch.ops.aten._softmax(_input, dim, False)

        return output


class QLV4_LogSoftmax_MOD(nn.Module):
    def __init__(self, emul_dtype, node_name):
        super().__init__()
        self.emul_dtype = emul_dtype
        self.node_name = node_name

    def forward(self, input, dim=None, _stacklevel=3, dtype=None):
        # input dtype of softmax must be in [bf16 or fp32]
        if input.dtype == torch.bfloat16:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)
        else:
            _input = input

        if self.emul_dtype == torch.float64:
            output = wrap_func_with_type_emulation(
                [_input],
                ['float32'],
                torch.float32,
                self.node_name + '_log_softmax',
                self.emul_dtype,
                lambda x: torch.ops.aten.log_softmax(x, dim),
            )
        else:
            output = torch.ops.aten.log_softmax(_input, dim)

        return output
