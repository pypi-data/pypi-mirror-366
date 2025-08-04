from typing import Any

from torch import Tensor

from ..modeling.qlv4_output_modeling import QLV4_Output_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Output"]


# TODO: to be integrated by type_cast
class QLV4_Output(QLV4_ModelCompressorModule):
    def __init__(self, qlv3_output_quantizer, **org_target_kwargs: Any):
        super().__init__()
        self.QLV4_output = QLV4_Output_MOD(qlv3_output_quantizer)

    def forward(self, input: Tensor, *args, **kwargs) -> Tensor:
        if not isinstance(input, Tensor):
            return input
        output = self.QLV4_output(input)

        return output
