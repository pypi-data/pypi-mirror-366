from ..modeling.qlv4_concat_modeling import QLV4_Concat_MOD
from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Concat"]


class QLV4_Concat(QLV4_ModelCompressorModule):
    def __init__(self, qlv3_output_quantizer=None, **org_target_kwargs):
        super().__init__()
        self.QLV4_concat = QLV4_Concat_MOD()
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, *args, **kwargs):
        output = self.QLV4_concat(*args, **kwargs)
        output = self.QLV4_output(output)

        return output
