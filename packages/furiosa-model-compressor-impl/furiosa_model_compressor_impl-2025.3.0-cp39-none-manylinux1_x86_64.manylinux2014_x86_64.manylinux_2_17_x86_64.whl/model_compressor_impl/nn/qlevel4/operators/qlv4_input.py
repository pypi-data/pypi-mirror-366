from typing import Any

from torch import Tensor

from ..modeling.qlv4_input_modeling import QLV4_Input_MOD
from .qlv4_mcm_base import QLV4_ModelCompressorModule

__all__ = ["QLV4_Input"]


# TODO: to be integrated by type_cast
class QLV4_Input(QLV4_ModelCompressorModule):
    def __init__(
        self,
        emul_dtype,
        node_name,
        _real_dtype,
        _o_dtype,
        _input_quantizer,
        **org_target_kwargs: Any,
    ):
        super().__init__()
        self.QLV4_input_quantizer = QLV4_Input_MOD(
            emul_dtype, node_name, _real_dtype, _o_dtype, _input_quantizer
        )

    def forward(self, input, *args, **kwargs) -> Tensor:
        output = self.QLV4_input_quantizer(input)

        return output
