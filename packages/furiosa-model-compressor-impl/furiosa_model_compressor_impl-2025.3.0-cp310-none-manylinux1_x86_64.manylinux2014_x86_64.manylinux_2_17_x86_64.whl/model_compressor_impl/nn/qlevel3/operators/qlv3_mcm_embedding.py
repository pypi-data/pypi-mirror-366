import torch
from torch import Tensor, nn

from .... import nn as quant_nn
from ..modeling.qlv3_mcm_embedding_modeling import QLV3_ModelCompressorModuleEmbedding_MOD
from ..precompute import get_qparams
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = ["QLV3_ModelCompressorModuleEmbedding"]

_tmp_string_to_torch_dtype = {'bf16': torch.bfloat16, 'int8': torch.int8}


class QLV3_ModelCompressorModuleEmbedding(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleEmbedding):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        self.weight_quantizer = None
        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)

        self.qlv3_embedding = QLV3_ModelCompressorModuleEmbedding_MOD(self.org_target)

        self.qlv3_input_pre_quantizer = None
        self.qlv3_output_quantizer = None

    def qlv3_forward(self, *args, **kwargs):
        _idx = args[0]
        # inputs of embedding are indices, so dtype of embedding input must be int64 or int32
        # if not _idx.dtype in [torch.int64, torch.int32]:
        #     raise ValueError("input must be long or int type tensor")
        _idx = _idx.to(torch.int64)  # TODO : 임시 구현

        # _idx = self.qlv3_input_quantizer(
        #     _idx
        # )  # TODO : embedding input 에 대한 quantizer 는 지워야 할듯?

        modeling_output = self.forward(_idx, *args[1:], **kwargs)
        output = self.qlv3_output_quantizer(modeling_output)

        return output

    def forward(self, *args, **kwargs) -> Tensor:
        output = self.qlv3_embedding(*args, **kwargs)

        return output

    def golden_mode(self):
        self.qlv3_embedding.golden_mode()

    def set_emulation_dtype(self, emul_dtype):
        self.qlv3_embedding.set_emulation_dtype(emul_dtype)

    def set_input_quantizer(self, qlv2_mcm):
        self.input_quantizer.append(qlv2_mcm._input_quantizer)
        self.weight_quantizer = qlv2_mcm._weight_quantizer

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': [self.qlv3_input_pre_quantizer],
            'mod': self.qlv3_embedding,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        _device = (
            self.org_target.weight.device if self.org_target.weight.device.type != 'meta' else 'cpu'
        )
        # # 1. self.input_quantizer 를 enable_real_quant 로 변환
        _iquantizer = self.input_quantizer[0]
        if not _iquantizer.rollback:
            _iquantizer.reset()
            _iquantizer = nn.Identity()
        else:
            if _iquantizer.quant_desc.dtype == 'fp32':
                raise ValueError("fp32 should not be rollback")
            else:
                _iquantizer.enable_real_quant()
                _iquantizer._dequantize = False
        self.qlv3_input_pre_quantizer = _iquantizer

        # 2. weight 을 quantized weight 으로 변환
        self.weight_quantizer.enable_real_quant()
        self.weight_quantizer._dequantize = (
            False  # TODO :  real quant vs real dequant 를 변경할 수 있는 method 필요
        )

        # TODO : real tensor quant 를 하기 위해선 merged_scale 및 zero_point 변수를 사용해야하지만, 기존 qparam으로 이를 할 수 있어야함
        weight_qparams = get_qparams(self.weight_quantizer, if_bcq=False, device=_device)
        self.weight_quantizer.merged_scale = weight_qparams[0]  # TODO : 이거 안해줘도됨
        self.weight_quantizer.zero_point = weight_qparams[1]

        # TODO : 매우 hardcoding
        if self.weight_quantizer.quant_desc.axis is not None:
            self.weight_quantizer.merged_scale = self.weight_quantizer.merged_scale.unsqueeze(-1)

        if not is_decode and self.org_target.weight.device.type != 'meta':
            quantized_weight = self.weight_quantizer(self.org_target.weight).detach()
            _dtype = _tmp_string_to_torch_dtype[self.weight_quantizer.quant_desc.dtype]
            # TODO : model 내의 모든 tensor 를 한번에 detach 하는 기능은 어떨까?
            # self.org_target.weight.requires_grad = False
            self.org_target.register_parameter(
                'weight', nn.Parameter(quantized_weight.to(_dtype), requires_grad=False)
            )
            # prefill_module 이 있으면 weight 은 그대로 둔다!

        # self.org_target.weight.data = quantized_weight.to(_dtype)  # TODO :  왜? real quant 는 type 변화는 하지 않고 있는가?

        # 2. self.weight_quantizer 를 사용해서 modeling 내부의 weight_dequantizer 생성 필요
        self.qlv3_embedding._weight_dequantizer = self.weight_quantizer
        self.qlv3_embedding._weight_dequantizer.enable_real_quant()
        self.qlv3_embedding._weight_dequantizer.enable_dequantize()

        # 3. self.output_quantizer 를 enable_real_quant 로 변환
        self.qlv3_output_quantizer = self.output_quantizer[0]
        self.qlv3_output_quantizer.enable_real_quant()
        self.qlv3_output_quantizer._dequantize = False

        del self.input_quantizer
        del self.output_quantizer

    # TODO : 현 qlv4 module 생성을 위한 attribute 임시 구현
    @property
    def _additional_attr(self):
        return {'weight_real_dtype': self.weight_quantizer.quant_desc.dtype}
