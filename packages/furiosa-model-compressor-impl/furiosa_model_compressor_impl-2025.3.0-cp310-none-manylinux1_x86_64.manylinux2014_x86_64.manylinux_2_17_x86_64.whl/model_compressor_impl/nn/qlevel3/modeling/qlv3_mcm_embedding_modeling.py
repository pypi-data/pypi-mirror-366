import torch
from torch import nn

__all__ = ["QLV3_ModelCompressorModuleEmbedding_MOD"]


class QLV3_ModelCompressorModuleEmbedding_MOD(nn.Module):
    def __init__(self, org_target):
        super().__init__()
        self._org_target = org_target

        # self.num_embeddings = org_target.num_embeddings
        # self.embedding_dim = org_target.embedding_dim
        self.emul_dtype = torch.bfloat16

        self._weight_dequantizer = None  # TODO: None 으로 init 하는게 맞을까?

    def forward(self, input):
        # inputs of embedding are indices, so dtype of embedding input must be int64 or int32
        if input.dtype not in [torch.int64, torch.int32]:
            raise ValueError("input must be long or int type tensor")
        _input = input
        _weight = self._org_target.weight

        # TODO: runtime 시 동작하는 weight decoding 과정, >> 필요없음!
        # org_target 의 weight parameter를 update 는 하는 방식으로 구현 해도 ATEN 표현이 우리가 원하는 대로 될 수 있는지 확인필요
        if _weight.dtype != torch.bfloat16:
            _weight = _weight.to(torch.float32)  # type casting for VE
            _weight = self._weight_dequantizer(_weight)
            _weight = _weight.to(self.emul_dtype)
        elif self.emul_dtype != torch.bfloat16:
            _weight = _weight.to(self.emul_dtype)  # Type casting for numerical semantic partial sum
        self._org_target.register_parameter('weight', nn.Parameter(_weight, requires_grad=False))

        output = self._org_target(_input.to(_weight.device))

        # output = output.to(self._o_dtype)
        return output

    def golden_mode(self):
        self.emul_dtype = torch.float64

    def set_emulation_dtype(self, emul_dtype):
        self.emul_dtype = emul_dtype
