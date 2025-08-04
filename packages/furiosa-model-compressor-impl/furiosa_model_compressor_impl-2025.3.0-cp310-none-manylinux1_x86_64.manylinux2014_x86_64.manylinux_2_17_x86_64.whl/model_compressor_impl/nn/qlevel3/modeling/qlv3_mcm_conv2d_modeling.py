import torch
from torch import nn

from ....nn import unpack_int8_to_int4

__all__ = ["QLV3_ModelCompressorModuleConv2d_MOD"]


class QLV3_ModelCompressorModuleConv2d_MOD(nn.Module):
    def __init__(self, org_target):
        super().__init__()
        self._org_target = org_target

        self._zero_point_input = 0.0
        self._weight_dequantizer = None  # TODO: None 으로 init 하는게 맞을까?
        self.emul_dtype = torch.float64
        self._weight_decoding = False

    def forward(self, input):
        _input = input
        _weight = self._org_target.weight
        _bias = self.org_target.bias.data
        # TODO : lm_head 는??

        if self._weight_decoding:
            # weight decoding
            _org_weight = self._org_target.weight
            if self._weight_dequantizer.quant_desc.dtype == 'int4':
                _weight = unpack_int8_to_int4(_weight)
            _weight = _weight.to(dtype=torch.float32)  # type casting for VE
            _weight = self._weight_dequantizer(_weight)
            _weight = _weight.to(dtype=_input.dtype)  # matching with input dtype
            self._org_target.register_parameter(
                'weight', nn.Parameter(_weight, requires_grad=False)
            )

        if self.emul_dtype != torch.bfloat16:
            _input = _input.to(self.emul_dtype)  # Type casting for numerical semantic partial sum
            _weight = _weight.to(self.emul_dtype)  # Type casting for numerical semantic partial sum

            # TODO : weight 이 바뀌면 _org_target에 다시 넣어 해줘야함!
            self._org_target.register_parameter(
                'weight', nn.Parameter(_weight, requires_grad=False)
            )

        org_padding = self._org_target.padding
        if self._org_target.padding not in ((0, 0), 'valid'):
            # quantize를 한 경우 0에 대응되는 value가 있으므로 padding시 해당 값으로 처리를 해야함
            if self._org_target.padding_mode == "zeros":
                if self.padding == 'same':
                    # TODO: filter 크기를 보고 pad 필터를 계산하는 코드 구현필요
                    raise NotImplementedError("'same' padding is not implemented yet")
                _input = torch.nn.functional.pad(
                    _input,
                    (
                        self._org_target.padding[1],
                        self._org_target.padding[1],
                        self._org_target.padding[0],
                        self._org_target.padding[0],
                    ),
                    mode="constant",
                    value=self.zero_point,
                )
                # padding을 밖에서 수행하므로 padding을 안하도록 설정
                self._org_target.padding = (0, 0)

        self._org_target.register_parameter(
            'bias', None
        )  # org_target은 DPE와 VE의 동작이 합쳐져있어 DPE 단독 동작을 위해 bias를 제거
        output = self._org_target(_input)
        self._org_target.register_parameter(
            'bias', nn.Parameter(_bias, requires_grad=False)
        )  # org_target의 bias와 qlv3_bias의 link를 유지하기 위해 재할당
        self._org_target.padding = org_padding

        if self._weight_decoding:
            self._org_target.register_parameter(
                'weight', nn.Parameter(_org_weight, requires_grad=False)
            )
        return output

    def set_emulation_dtype(self, emul_dtype):
        self.emul_dtype = emul_dtype
