import torch

from ..modeling.qlv4_bias_modeling import QLV4_BIAS_MOD
from ..modeling.qlv4_conv_modeling import QLV4_Conv2d_MOD
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Conv2d"]


class QLV4_Conv2d(QLV4_ModelCompressorModule):
    """Quantized 2D conv"""

    def __init__(
        self,
        org_target,
        bias,
        weight_real_dtype,
        weight_quantizer,
        emul_dtype,
        _zero_point_input,
        node_name,
        in_channels: int,
        out_channels: int,
        kernel_size,
        stride=1,
        padding=0,
        dilation=1,
        groups=1,
        padding_mode="zeros",
        emul_dtype_bias=None,
        qlv3_output_quantizer=None,
        **org_target_kwargs,
    ):
        super().__init__(org_target)
        self.QLV4_conv2d = QLV4_Conv2d_MOD(
            org_target,
            weight_real_dtype,
            weight_quantizer,
            emul_dtype,
            _zero_point_input,
            node_name,
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            dilation,
            groups,
            padding_mode,
        )
        self.QLV4_bias = QLV4_BIAS_MOD(bias, emul_dtype_bias)
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        if hasattr(self, '_hf_hook'):
            args, _ = self._hf_hook.pre_forward(self, input)
            input = args[0]

        output = self.QLV4_conv2d(input)
        output = self.QLV4_bias(output)

        output = self.QLV4_output(output)

        if hasattr(self, '_hf_hook'):
            output = self._hf_hook.post_forward(self, output)
        return output

    # TODO: conv에대해 qerr ub 구현 필요
    '''def _calculate_qerr_ub(self, input, emulation_dtype=torch.float64):
        from ....utils.calculate_qerr_ub import calculate_qerr_upper_bound_linear_and_matmul

        _input = input
        _, _weight = self.QLV4_linear.decoding_weight(_input, self.QLV4_linear.weight)

        qrr_ub = calculate_qerr_upper_bound_linear_and_matmul(
            _input, _weight, emulation_dtype=emulation_dtype
        )
        return qrr_ub.cpu()'''
