import torch

from ..modeling.qlv4_functional_modeling import *  # noqa: F403
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = [
    "QLV4_Mul",
    "QLV4_Div",
    "QLV4_FloorDiv",
    "QLV4_TrueDiv",
    "QLV4_Add",
    "QLV4_Sub",
    "QLV4_Cumsum",
    "QLV4_MaskedFill",
    "QLV4_Mean",
    "QLV4_Pow",
    "QLV4_Rsqrt",
    "QLV4_Einsum",
    "QLV4_MatMul",
    "QLV4_FSoftmax",
    "QLV4_LogSoftmax",
]


class QLV4_Mul(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_mul = QLV4_Mul_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_mul(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Div(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_div = QLV4_Div_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_div(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_FloorDiv(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_floordiv = QLV4_FloorDiv_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_floordiv(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_TrueDiv(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_truediv = QLV4_TrueDiv_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_truediv(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Add(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_add = QLV4_Add_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_add(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Sub(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_sub = QLV4_Sub_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        output = self.QLV4_sub(input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Cumsum(QLV4_ModelCompressorModule):
    def __init__(self, **org_target_kwargs):
        super().__init__()
        self.QLV4_cumsum = QLV4_Cumsum_MOD()  # noqa: F405

    def forward(self, input, dim, **kwargs):
        output = self.QLV4_cumsum(input, dim, **kwargs)
        return output


class QLV4_MaskedFill(QLV4_ModelCompressorModule):
    def __init__(self, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_maskedfill = QLV4_MaskedFill_MOD()  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, mask, value):
        output = self.QLV4_maskedfill(input, mask, value)
        output = self.QLV4_output(output)

        return output


class QLV4_Mean(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_mean = QLV4_Mean_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, dim, **kwargs):
        output = self.QLV4_mean(input, dim, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Pow(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_pow = QLV4_Pow_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, exponent, **kwargs):
        output = self.QLV4_pow(input, exponent, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_Rsqrt(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_rsqrt = QLV4_Rsqrt_MOD(emul_dtype)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, **kwargs):
        output = self.QLV4_rsqrt(input, **kwargs)
        output = self.QLV4_output(output)

        return output


# TODO: gpt-j/huggingface_rope 의 apply_rotary_pos_emb() 내부 einsum 만을 위한 특수 구현
class QLV4_Einsum(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, node_name, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_einsum = QLV4_Einsum_MOD(emul_dtype, node_name)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, equation, input_0, input_1, **kwargs):
        output = self.QLV4_einsum(equation, input_0, input_1, **kwargs)
        output = self.QLV4_output(output)

        return output


class QLV4_MatMul(QLV4_ModelCompressorModule):
    def __init__(
        self,
        emul_dtype,
        node_name,
        input_0_dtype=None,
        input_1_dtype=None,
        qlv3_input_0_fetch=None,
        qlv3_input_1_fetch=None,
        qlv3_output_quantizer=None,
        **org_target_kwargs,
    ):
        super().__init__()
        fetch_0_quant_desc = qlv3_input_0_fetch
        fetch_1_quant_desc = qlv3_input_1_fetch
        node_name = node_name

        if len(fetch_0_quant_desc) == 0:
            self.QLV4_fetch_0 = torch.nn.Identity()
        else:
            self.QLV4_fetch_0 = QLV4_Fetch(
                node_name + '_sub_0',
                fetch_0_quant_desc['quant_desc'],
                fetch_0_quant_desc['_zero_point'],
            )
        if len(fetch_1_quant_desc) == 0:
            self.QLV4_fetch_1 = torch.nn.Identity()
        else:
            self.QLV4_fetch_1 = QLV4_Fetch(
                node_name + '_sub_1',
                fetch_1_quant_desc['quant_desc'],
                fetch_1_quant_desc['_zero_point'],
            )
        self.QLV4_matmul = QLV4_MatMul_MOD(
            emul_dtype,
            node_name,
            input_0_dtype,
            input_1_dtype,
            qlv3_input_0_fetch,
            qlv3_input_1_fetch,
        )  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input_0, input_1, **kwargs):
        _input_0 = self.QLV4_fetch_0(input_0)
        _input_1 = self.QLV4_fetch_1(input_1)
        output = self.QLV4_matmul(_input_0, _input_1, **kwargs)
        output = self.QLV4_output(output)

        return output

    def _calculate_qerr_ub(self, input_0, input_1, emulation_dtype=torch.float64):
        from ....utils.calculate_qerr_ub import calculate_qerr_upper_bound_linear_and_matmul

        _input_0, _input_1, _, _, _ = self.QLV4_matmul.decoding_inputs(input_0, input_1)
        qrr_ub = calculate_qerr_upper_bound_linear_and_matmul(
            _input_0, _input_1, emulation_dtype=emulation_dtype, is_matmul=True
        )

        return qrr_ub.cpu()


# TODO : should be integrated with module softmax
class QLV4_FSoftmax(QLV4_ModelCompressorModule):
    def __init__(
        self,
        emul_dtype,
        node_name,
        qlv3_output_quantizer=None,
        input_scale=None,
        **org_target_kwargs,
    ):
        super().__init__()
        self.QLV4_softmax = QLV4_FSoftmax_MOD(emul_dtype, node_name)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)
        self.input_scale = input_scale

    def forward(self, input, dim=None, _stacklevel=3, dtype=None):
        _input = input
        if input.dtype == torch.int8:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)
            _input = torch.ops.aten.mul(_input, self.input_scale)
        output = self.QLV4_softmax(_input, dim, _stacklevel, dtype)
        output = self.QLV4_output(output)
        return output


class QLV4_LogSoftmax(QLV4_ModelCompressorModule):
    def __init__(self, emul_dtype, node_name, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_mod = QLV4_LogSoftmax_MOD(emul_dtype, node_name)  # noqa: F405
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input, dim=None, _stacklevel=3, dtype=None):
        output = self.QLV4_mod(input, dim, _stacklevel, dtype)
        output = self.QLV4_output(output)
        return output
