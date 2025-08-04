import torch
from torch import Tensor

from ..modeling.qlv4_activation_modeling import *  # noqa: F403
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = [
    "QLV4_ReLU6",
    "QLV4_ReLU",
    "QLV4_SiLU",
    "QLV4_Sigmoid",
    "QLV4_Hardswish",
    "QLV4_Hardsigmoid",
    "QLV4_Elu",
    "QLV4_Softmax",
    "QLV4_GeLU",
    "QLV4_Tanh",
    "QLV4_erf",
]


class QLV4_ReLU6(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_relu6 = QLV4_ReLU6_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, inplace=False) -> Tensor:

        if inplace:
            '''
            inplace는 torch.nn.functional.relu6()의 option입니다.
            굳이 이를 위한 구현을 하기보다는 torch.fx.functionalize()를 적용하여 해당 경우가 발생하지 않게 막아야합니다.
            '''
            raise ValueError('inplace option is not supported.')

        output = self.QLV4_relu6(input)
        output = self.QLV4_output(output)
        return output


class QLV4_ReLU(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_relu = QLV4_ReLU_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, inplace=False) -> Tensor:

        if inplace:
            '''
            inplace는 torch.nn.functional.relu()의 option입니다.
            굳이 이를 위한 구현을 하기보다는 torch.fx.functionalize()를 적용하여 해당 경우가 발생하지 않게 막아야합니다.
            '''
            raise ValueError('inplace option is not supported.')

        output = self.QLV4_relu(input)
        output = self.QLV4_output(output)

        return output


class QLV4_SiLU(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_silu = QLV4_SiLU_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        output = self.QLV4_silu(input)
        output = self.QLV4_output(output)

        return output


class QLV4_GeLU(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_gelu = QLV4_GeLU_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        output = self.QLV4_gelu(input, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Tanh(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_tanh = QLV4_Tanh_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, **kwargs) -> Tensor:
        output = self.QLV4_tanh(input, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Sigmoid(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_sigmoid = QLV4_Sigmoid_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor) -> Tensor:
        output = self.QLV4_sigmoid(input)
        output = self.QLV4_output(output)

        return output


class QLV4_Hardswish(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_hardswish = QLV4_Hardsigmoid_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor) -> Tensor:
        output = self.QLV4_hardswish(input)
        output = self.QLV4_output(output)

        return output


class QLV4_Hardsigmoid(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_hardsigmoid = QLV4_Hardsigmoid_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor) -> Tensor:
        output = self.QLV4_hardsigmoid(input)
        output = self.QLV4_output(output)

        return output


class QLV4_Elu(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_elu = QLV4_Elu_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor) -> Tensor:
        output = self.QLV4_elu(input)
        output = self.QLV4_output(output)

        return output


class QLV4_Softmax(QLV4_ModelCompressorModule):
    def __init__(
        self,
        dim=None,
        emul_dtype=None,
        node_name=None,
        qlv3_output_quantizer=None,
        input_scale=None,
        **org_target_kwargs,
    ):
        super().__init__()
        self.QLV4_softmax = QLV4_Softmax_MOD(
            dim=dim, emul_dtype=emul_dtype, node_name=node_name
        )  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)
        self.input_scale = input_scale

    def forward(self, input: Tensor, dim=None, _stacklevel=3, dtype=None) -> Tensor:
        _input = input
        if input.dtype == torch.int8:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)

            _input = torch.ops.aten.mul(_input, self.input_scale)
        output = self.QLV4_softmax(_input)
        output = self.QLV4_output(output)

        return output


class QLV4_erf(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_mod = QLV4_erf_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor) -> Tensor:
        output = self.QLV4_mod(input)
        output = self.QLV4_output(output)

        return output
