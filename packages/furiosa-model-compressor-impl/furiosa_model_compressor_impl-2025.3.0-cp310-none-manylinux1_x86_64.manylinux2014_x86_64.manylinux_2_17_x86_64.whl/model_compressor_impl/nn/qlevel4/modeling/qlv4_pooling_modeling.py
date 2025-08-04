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


"""Quantized Pooling
Base code is from nn.pooling, details of Module and original argument can be found there.
Module names are intentionally kept same as unquantized version so that they can be dropped into preexisting model
easily, and load pretrained weight. Aliases with Quant prefix are defined and are encouraged to be used explicitly
when start scratch.
"""
from typing import Optional

import torch
from torch import nn
from torch.nn.common_types import _size_any_t

__all__ = [
    "QLV4_AdaptiveAvgPool2d_MOD",
    "QLV4_FAdaptiveAvgPool2d_MOD",
    "QLV4_MaxPool2d_MOD",
]


class QLV4_AdaptiveAvgPool2d_MOD(nn.Module):
    def __init__(self, output_size, emul_dtype):
        super().__init__()
        self.output_size = (output_size, output_size) if type(output_size) is int else output_size
        self.emul_dtype = emul_dtype

    def forward(self, input):
        _input = input
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast for emulation (FP64)

        output = torch.ops.aten._adaptive_avg_pool2d(_input, self.output_size)

        return output


class QLV4_FAdaptiveAvgPool2d_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input, output_size):
        _input = input
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast for emulation (FP64)

        output = torch.ops.aten._adaptive_avg_pool2d(_input, output_size)

        return output


class QLV4_MaxPool2d_MOD(nn.Module):
    def __init__(
        self,
        kernel_size: _size_any_t,
        stride: Optional[_size_any_t],
        padding: _size_any_t,
        dilation: _size_any_t,
        ceil_mode: bool,
    ):
        super().__init__()
        # return indices is excluded as aten.max_pool2d does not accept it.
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.ceil_mode = ceil_mode

    def forward(self, input):
        output = torch.ops.aten.max_pool2d(
            input, self.kernel_size, self.stride, self.padding, self.dilation, self.ceil_mode
        )

        return output
