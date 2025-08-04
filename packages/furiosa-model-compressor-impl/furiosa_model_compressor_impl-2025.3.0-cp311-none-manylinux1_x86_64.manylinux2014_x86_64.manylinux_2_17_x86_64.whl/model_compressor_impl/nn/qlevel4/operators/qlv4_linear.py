import torch

from ..modeling.qlv4_bias_modeling import QLV4_BIAS_MOD
from ..modeling.qlv4_linear_modeling import QLV4_Linear_MOD
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Linear"]


class QLV4_Linear(QLV4_ModelCompressorModule):
    def __init__(
        self,
        org_target,
        emul_dtype,
        node_name,
        bias,
        weight_real_dtype,
        weight_quantizer,
        in_features,
        out_features,
        emul_dtype_bias=None,
        qlv3_output_quantizer=None,
        **org_target_kwargs,
    ):
        super().__init__(org_target)
        self.QLV4_linear = QLV4_Linear_MOD(
            emul_dtype,
            node_name,
            org_target,
            weight_real_dtype,
            weight_quantizer,
            in_features,
            out_features,
        )
        self.QLV4_bias = QLV4_BIAS_MOD(bias, emul_dtype_bias)
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        if hasattr(self, '_hf_hook'):
            args, _ = self._hf_hook.pre_forward(self, input)
            input = args[0]

        output = self.QLV4_linear(input)
        output = self.QLV4_bias(output)

        output = self.QLV4_output(output)

        if hasattr(self, '_hf_hook'):
            output = self._hf_hook.post_forward(self, output)
        return output

    def _calculate_qerr_ub(self, input, emulation_dtype=torch.float64):
        from ....utils.calculate_qerr_ub import calculate_qerr_upper_bound_linear_and_matmul

        _input = input
        _, _weight = self.QLV4_linear.decoding_weight(_input, self.QLV4_linear.weight)

        qrr_ub = calculate_qerr_upper_bound_linear_and_matmul(
            _input, _weight, emulation_dtype=emulation_dtype
        )
        return qrr_ub.cpu()
