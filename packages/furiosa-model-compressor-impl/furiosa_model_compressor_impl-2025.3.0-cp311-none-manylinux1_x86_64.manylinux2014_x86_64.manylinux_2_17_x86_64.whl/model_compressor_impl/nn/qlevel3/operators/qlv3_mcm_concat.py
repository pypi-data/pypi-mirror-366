import copy

from torch import nn

from .... import descriptor
from .... import nn as quant_nn
from .... import quant_op
from ..modeling.qlv3_mcm_concat_modeling import QLV3_ModelCompressorModuleConcat_MOD
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = ["QLV3_ModelCompressorModuleConcat"]


class QLV3_ModelCompressorModuleConcat(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleConcat):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)

        self._qlv3_mod = QLV3_ModelCompressorModuleConcat_MOD(self.org_target)

        self.qlv3_input_pre_quantizer = None
        self.qlv3_output_quantizer = None

    def qlv3_forward(self, *args, **kwargs):
        quant_input = []
        # input_tensor = args[0]
        # for i, tensor in enumerate(input_tensor):
        #     quant_input.append(self.qlv3_input_pre_quantizer[i](tensor))

        # if len(args) > 1:
        #     if len(args) == 2:
        #         kwargs["dim"] = args[1]
        #     else:
        #         raise NotImplementedError("Not Expected case.")

        # args = (tuple(quant_input),)

        x = self.forward(*args, **kwargs)
        x = self.qlv3_output_quantizer(x)

        return x

    def forward(self, *args, **kwargs):
        output = self._qlv3_mod(*args, **kwargs)

        return output

    def golden_mode(self):
        self._qlv3_mod.golden_mode()

    def set_emulation_dtype(self, emul_dtype):
        self._qlv3_mod.set_emulation_dtype(emul_dtype)

    def set_input_quantizer(self, qlv2_mcm):
        for i, quantizer in enumerate(qlv2_mcm._input_quantizer):
            self.input_quantizer.append(quantizer)

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': list(self.qlv3_input_pre_quantizer),
            'mod': self._qlv3_mod,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        _output_quantizer = self.output_quantizer[0]

        # TODO : hard coding for KV cache concat
        if len(self.input_quantizer) == 0:
            for _ in range(2):
                self.input_quantizer.append(
                    quant_op.TensorQuantizer(copy.deepcopy(descriptor.QUANT_DESC_DISABLE))
                )

        # TODO : output param을 input shape에 맞도록 케이스를 나누어 split하는 구현 필요
        propagate_oquantizer = True
        for i, _iquantizer in enumerate(self.input_quantizer):
            input_shape = _iquantizer.quant_desc.input_shape
            if not _iquantizer.rollback:
                _iquantizer.reset()
                _iquantizer = nn.Identity()
            else:
                if _iquantizer.quant_desc.dtype == 'fp32':
                    raise ValueError("fp32 should not be rollback")
                else:
                    _iquantizer.enable_real_quant()
                    _iquantizer._dequantize = False

            qparam_axis = _output_quantizer.quant_desc.axis
            if (
                qparam_axis is not None
                and self.output_shape[qparam_axis] != input_shape[qparam_axis]
            ):
                propagate_oquantizer = False
                continue
            else:
                _new_input_quantizer = copy.deepcopy(_output_quantizer)
                _new_input_quantizer.enable_real_quant()
                _new_input_quantizer._dequantize = False
                self.input_quantizer[i] = nn.Sequential(_iquantizer, _new_input_quantizer)

        if propagate_oquantizer:
            self.output_quantizer[0].reset()
            self.output_quantizer[0] = nn.Identity()
        else:
            self.output_quantizer[0].enable_real_quant()
            self.output_quantizer[0]._dequantize = False

        self.qlv3_input_pre_quantizer = self.input_quantizer
        self.qlv3_output_quantizer = self.output_quantizer[0]

        del self.input_quantizer
        del self.output_quantizer
