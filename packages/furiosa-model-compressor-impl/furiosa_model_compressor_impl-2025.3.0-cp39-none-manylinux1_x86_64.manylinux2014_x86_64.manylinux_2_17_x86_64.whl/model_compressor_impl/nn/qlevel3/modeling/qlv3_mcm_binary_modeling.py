import torch
from torch import nn

__all__ = [
    "QLV3_ModelCompressorModuleBinary_MOD",
]


# binary modeling은 항상 VE 에서 fp32 로 casting 이후 연산됨을 가정!
class QLV3_ModelCompressorModuleBinary_MOD(nn.Module):
    def __init__(self, org_target):
        super().__init__()
        self._org_target = org_target
        self.emul_dtype = torch.float32  # matmul 일때만 fp64 가 되도록 아닐때 fp32 가 맞음
        self.quant_enabled = False

    def forward(self, input_0, input_1, *args, **kwargs):
        if not isinstance(input_0, torch.Tensor) and not isinstance(input_1, torch.Tensor):
            output = self._org_target(input_0, input_1, *args, **kwargs)
            return output

        input_0 = torch.tensor(input_0) if not isinstance(input_0, torch.Tensor) else input_0
        input_1 = torch.tensor(input_1) if not isinstance(input_1, torch.Tensor) else input_1

        # 둘다 torch.tensor 이고 dtype이 모두 int64 가 아닐경우에만, emul_dtype으로 casting 하라고 되어 있는데...
        # SRAM(BF16) -> VE(FP32 or FP64) type casting
        _input_0 = input_0.to(
            self.emul_dtype
        )  # if input_0.dtype is not self.emul_dtype else input_0
        _input_1 = input_1.to(
            self.emul_dtype
        )  # if input_1.dtype is not self.emul_dtype else input_1

        output = self._org_target(_input_0, _input_1, *args, **kwargs)

        return output

    def golden_mode(self):
        self.emul_dtype = torch.float64

    def set_emulation_dtype(self, emul_dtype):
        self.emul_dtype = emul_dtype
