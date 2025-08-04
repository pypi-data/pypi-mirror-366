import torch
from torch import nn

__all__ = [
    "QLV4_Concat_MOD",
]


class QLV4_Concat_MOD(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, *args, **kwargs):
        input_tensor = args[0]
        if len(args) > 1:
            if len(args) == 2:
                kwargs["dim"] = args[1]
            else:
                raise NotImplementedError("Not Expected case.")

        args = (tuple(input_tensor),)
        output = torch.ops.aten.cat(*args, **kwargs)

        return output
