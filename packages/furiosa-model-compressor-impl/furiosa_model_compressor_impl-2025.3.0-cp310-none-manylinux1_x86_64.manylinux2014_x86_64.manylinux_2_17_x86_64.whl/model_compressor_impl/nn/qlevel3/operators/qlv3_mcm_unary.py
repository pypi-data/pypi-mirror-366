from torch import Tensor, nn

from .... import nn as quant_nn
from ..modeling.qlv3_mcm_unary_modeling import QLV3_ModelCompressorModuleUnary_MOD
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = [
    "QLV3_ModelCompressorModuleUnary",
]


class QLV3_ModelCompressorModuleUnary(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleUnary):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)

        self._qlv3_mod = QLV3_ModelCompressorModuleUnary_MOD(self.org_target)

        self.qlv3_input_pre_quantizer = None
        self.qlv3_output_quantizer = None

    def qlv3_forward(self, *args, **kwargs):
        # unary op 이기 때문에 첫번째 index 가 tensor
        # input_tensor = args[0]
        x = self.forward(*args, **kwargs)
        x = self.qlv3_output_quantizer(x)

        return x

    def forward(self, *args, **kwargs) -> Tensor:
        output = self._qlv3_mod(*args, **kwargs)

        return output

    def golden_mode(self):
        self._qlv3_mod.golden_mode()

    def set_emulation_dtype(self, emul_dtype):
        self._qlv3_mod.set_emulation_dtype(emul_dtype)

    def set_input_quantizer(self, qlv2_mcm):
        self.input_quantizer.append(qlv2_mcm._input_quantizer)

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': [self.qlv3_input_pre_quantizer],
            'mod': self._qlv3_mod,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        if not self.input_quantizer[0].rollback:
            self.input_quantizer[0].reset()
            self.input_quantizer[0] = nn.Identity()

        else:
            if self.input_quantizer[0].quant_desc.dtype == 'fp32':
                raise ValueError("fp32 should not be rollback")
            else:
                # real quant 로 변환
                self.input_quantizer[0].enable_real_quant()
                self.input_quantizer[0]._dequantize = False

        self.output_quantizer[0].enable_real_quant()
        self.output_quantizer[0]._dequantize = False

        self.qlv3_input_pre_quantizer = self.input_quantizer[0]
        self.qlv3_output_quantizer = self.output_quantizer[0]

        del self.input_quantizer
        del self.output_quantizer
