import torch
from torch import Tensor, nn

__all__ = [
    "QLV3_ModelCompressorModuleUnary_MOD",
]


class QLV3_ModelCompressorModuleUnary_MOD(nn.Module):
    def __init__(self, org_target):
        super().__init__()
        self._org_target = org_target
        self.emul_dtype = torch.float32

    def forward(self, input: Tensor, *args, **kwargs) -> Tensor:
        _input = input
        _input = _input.to(self.emul_dtype) if _input.dtype is not self.emul_dtype else _input

        output = self._org_target(_input, *args, **kwargs)

        return output

    def golden_mode(self):
        self.emul_dtype = torch.float64

    def set_emulation_dtype(self, emul_dtype):
        self.emul_dtype = emul_dtype
