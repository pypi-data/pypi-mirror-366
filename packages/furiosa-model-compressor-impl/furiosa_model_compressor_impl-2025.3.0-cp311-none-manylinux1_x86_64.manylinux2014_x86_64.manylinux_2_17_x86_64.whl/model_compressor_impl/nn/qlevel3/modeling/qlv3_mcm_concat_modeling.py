import torch
from torch import nn

__all__ = [
    "QLV3_ModelCompressorModuleConcat_MOD",
]


class QLV3_ModelCompressorModuleConcat_MOD(nn.Module):
    def __init__(self, org_target):
        super().__init__()
        self._org_target = org_target
        self.emul_dtype = None

    def forward(self, *args, **kwargs):
        input_tensor = tuple(item for item in args[0] if isinstance(item, torch.Tensor))

        if len(args) > 1:
            if len(args) == 2:
                kwargs["dim"] = args[1]
            else:
                raise NotImplementedError("Not Expected case.")

        args = (input_tensor,)
        output = self._org_target(*args, **kwargs)

        return output

    def golden_mode(self):
        pass

    def set_emulation_dtype(self, emul_dtype):
        pass
