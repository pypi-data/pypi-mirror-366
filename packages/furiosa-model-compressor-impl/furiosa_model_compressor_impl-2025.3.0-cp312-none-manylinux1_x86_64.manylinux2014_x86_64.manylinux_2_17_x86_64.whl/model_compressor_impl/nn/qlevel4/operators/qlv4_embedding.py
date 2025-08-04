from typing import Optional

from ..modeling.qlv4_embedding_modeling import QLV4_Embedding_MOD
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Embedding"]


class QLV4_Embedding(QLV4_ModelCompressorModule):
    def __init__(
        self,
        org_target,
        weight_real_dtype,
        emul_dtype,
        node_name,
        _weight_dequantizer=None,
        qlv3_output_quantizer=None,
        padding_idx: Optional[int] = None,
        max_norm: Optional[float] = None,
        norm_type: float = 2.0,
        scale_grad_by_freq: bool = False,
        sparse: bool = False,
        **org_target_kwargs,
    ):
        super().__init__(org_target)
        self.QLV4_embedding = QLV4_Embedding_MOD(
            org_target,
            weight_real_dtype,
            emul_dtype,
            node_name,
            _weight_dequantizer,
            padding_idx,
            max_norm,
            norm_type,
            scale_grad_by_freq,
            sparse,
        )
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        if hasattr(self, '_hf_hook'):
            args, _ = self._hf_hook.pre_forward(self, input)
            input = args[0]

        output = self.QLV4_embedding(input)
        output = self.QLV4_output(output)

        if hasattr(self, '_hf_hook'):
            output = self._hf_hook.post_forward(self, output)

        return output
