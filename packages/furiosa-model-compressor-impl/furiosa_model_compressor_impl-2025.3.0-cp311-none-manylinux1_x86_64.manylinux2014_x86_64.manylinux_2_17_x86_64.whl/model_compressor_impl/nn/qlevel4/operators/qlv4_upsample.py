from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from ..modeling.qlv4_upsample_modeling import QLV4_Upsample2d_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = [
    "QLV4_Upsample2d",
]


class QLV4_Upsample2d(QLV4_ModelCompressorModule):
    def __init__(
        self,
        size,
        scale_factor,
        mode,
        align_corners,
        recompute_scale_factor,
        qlv3_output_quantizer=None,
        **org_target_kwargs,
    ):
        super().__init__()
        self.QLV4_upsample2d = QLV4_Upsample2d_MOD(
            size, scale_factor, mode, align_corners, recompute_scale_factor
        )
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input):
        output = self.QLV4_upsample2d(input)
        output = self.QLV4_output(output)

        return output
