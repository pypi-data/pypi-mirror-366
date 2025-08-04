from torch import Tensor, nn

from .... import nn as quant_nn

# from ..modeling.qlv3_activation_modeling import *
from ..modeling.qlv3_mcm_einsum_modeling import QLV3_ModelCompressorModuleEinsum_MOD
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = [
    "QLV3_ModelCompressorModuleEinsum",
]


class QLV3_ModelCompressorModuleEinsum(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleEinsum):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)
        self._qlv3_mod = QLV3_ModelCompressorModuleEinsum_MOD(self.org_target)

        self.qlv3_input_0_fetch = nn.Identity()
        self.qlv3_input_1_fetch = nn.Identity()

        self.qlv3_input_0_pre_quantizer = None
        self.qlv3_input_1_pre_quantizer = None
        self.qlv3_output_quantizer = None

    def qlv3_forward(self, equantion, *args, **kwargs):
        # binary op 이기 때문에 첫번째 index 가 tensor
        input_0 = args[0]
        input_1 = args[1]

        if not isinstance(self.qlv3_input_0_fetch, nn.Identity):
            input_0 = self.qlv3_input_0_fetch(input_0)
        if not isinstance(self.qlv3_input_1_fetch, nn.Identity):
            input_1 = self.qlv3_input_1_fetch(input_1)

        x = self.forward(equantion, input_0, input_1, *args[2:], **kwargs)
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
        self.input_quantizer.append(qlv2_mcm._input_1_quantizer)
        self.input_quantizer.append(qlv2_mcm._input_2_quantizer)

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_0_pre_quantizer
        del self.qlv3_input_1_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': [self.qlv3_input_0_pre_quantizer, self.qlv3_input_1_pre_quantizer],
            'mod': self._qlv3_mod,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        # 항상 fp32 로 casting 필요!
        # modeling 내에서 fp32 또는 fp64 로 converting 을 명시!
        for i, _iquantizer in enumerate(self.input_quantizer):
            if _iquantizer.quant_desc.dtype not in ['bf16', 'fp32']:
                raise ValueError(
                    "only ['bf16', 'fp32'] is implemented for binary mcm except for matmul"
                )

        for i, _iquantizer in enumerate(self.input_quantizer):
            if not _iquantizer.rollback:
                _iquantizer.reset()
                self.input_quantizer[i] = nn.Identity()
            else:
                if _iquantizer.quant_desc.dtype == 'fp32':
                    raise ValueError("fp32 should not be rollback")
                else:
                    _iquantizer.enable_real_quant()
                    _iquantizer._dequantize = False

        self.output_quantizer[0].enable_real_quant()
        self.output_quantizer[0]._dequantize = False

        self.qlv3_input_0_pre_quantizer = self.input_quantizer[0]
        self.qlv3_input_1_pre_quantizer = self.input_quantizer[1]
        self.qlv3_output_quantizer = self.output_quantizer[0]

        del self.input_quantizer
        del self.output_quantizer
