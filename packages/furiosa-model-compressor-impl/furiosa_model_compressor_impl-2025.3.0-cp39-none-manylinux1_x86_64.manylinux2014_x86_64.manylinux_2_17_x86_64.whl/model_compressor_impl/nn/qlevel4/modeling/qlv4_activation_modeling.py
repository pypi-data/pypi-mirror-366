"""Quantized Activation functions
Base code is from nn.activation, details of Module and original argument can be found there.
Module names are intentionally kept same as unquantized version so that they can be dropped into preexisting model
easily, and load pretrained weight. Aliases with Quant prefix are defined and are encouraged to be used explicitly
when start scratch.
"""

import torch
from torch import Tensor, nn

from ...custom_ops.wrap_fucn_with_custom_ops import wrap_func_with_type_emulation

__all__ = [
    "QLV4_ReLU6_MOD",
    "QLV4_ReLU_MOD",
    "QLV4_SiLU_MOD",
    "QLV4_Sigmoid_MOD",
    "QLV4_Hardswish_MOD",
    "QLV4_Hardsigmoid_MOD",
    "QLV4_Elu_MOD",
    "QLV4_Softmax_MOD",
    "QLV4_GeLU_MOD",
    "QLV4_Tanh_MOD",
    "QLV4_erf_MOD",
]


class QLV4_ReLU6_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.relu6(_input)

        return output


class QLV4_ReLU_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.relu(_input)

        return output


class QLV4_SiLU_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.silu(_input)

        return output


class QLV4_GeLU_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.gelu(_input, **kwargs)

        return output


class QLV4_Tanh_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.tanh(_input, **kwargs)

        return output


class QLV4_Sigmoid_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.sigmoid(_input)

        return output


class QLV4_Hardswish_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.hardswish(_input)

        return output


class QLV4_Hardsigmoid_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.hardsigmoid(_input)
        return output


class QLV4_Elu_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.elu(_input)
        return output


class QLV4_Softmax_MOD(nn.Module):
    def __init__(self, dim=None, emul_dtype=None, node_name=None):
        super().__init__()
        self.dim = dim
        self.emul_dtype = emul_dtype
        self.node_name = node_name

    def forward(self, input: Tensor) -> Tensor:
        # input dtype of softmax must be in [bf16, fp32, or integer(for debugging)]
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
                lambda x: torch.ops.aten._softmax(x, self.dim, False),
            )
        else:
            ouptut = torch.ops.aten._softmax(_input, self.dim, False)

        return output


class QLV4_erf_MOD(nn.Module):
    def __init__(self, emul_dtype):
        super().__init__()
        self.emul_dtype = emul_dtype

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        _input = input

        # dtype of activation function is fp32 or fp64
        if self.emul_dtype == torch.float64:
            _input = torch.ops.aten._to_copy(
                _input, dtype=self.emul_dtype
            )  # Type cast input(fp32) -> fp64

        output = torch.ops.aten.erf(_input, **kwargs)

        return output
