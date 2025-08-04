import torch
from torch import Tensor

from ..modeling.qlv4_layernorm_modeling import QLV4_LayerNorm_MOD
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_LayerNorm"]


class QLV4_LayerNorm(QLV4_ModelCompressorModule):
    def __init__(
        self,
        org_target,
        emul_dtype,
        node_name,
        normalized_shape,
        eps: float = 1e-5,
        elementwise_affine: bool = True,
        qlv3_output_quantizer=None,
        input_scale=None,
        input_zero_point=None,
        **org_target_kwargs,
    ):
        super().__init__(org_target)
        self.QLV4_layernorm = QLV4_LayerNorm_MOD(
            emul_dtype,
            node_name,
            org_target,
            normalized_shape,
            eps,
            elementwise_affine,
        )
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)
        self.input_scale = input_scale
        self.input_zero_point = input_zero_point

    def forward(self, input: Tensor) -> Tensor:
        _input = input
        if input.dtype == torch.int8:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)
            _zero_point = torch.ops.aten._to_copy(self.input_zero_point, dtype=torch.float32)
            _input = torch.ops.aten.sub(_input, _zero_point)
            _input = torch.ops.aten.mul(_input, self.input_scale)
        output = self.QLV4_layernorm(_input)
        output = self.QLV4_output(output)

        return output
