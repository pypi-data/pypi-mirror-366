import torch

from ..modeling.bcq_groupconv1d import _BCQ_GroupConv1d
from ..modeling.binarylinear import _BinaryLinear
from .qlv3_old_module import QLV3_OldModule

__all__ = ["QLV3_BCQLinear"]


class QLV3_BCQLinear(QLV3_OldModule):
    def __init__(
        self,
        in_features,
        out_features,
        nbits,
        device=None,
        out_dtype=torch.float64,
        dump_mode=False,
        **kwargs,
    ):
        super(QLV3_BCQLinear, self).__init__()
        self.dump_mode = dump_mode
        self.binarylinear = _BinaryLinear(
            in_features,
            out_features * nbits,
            device=device,
            **kwargs,
        )
        self.groupconv = _BCQ_GroupConv1d(
            out_features * nbits, out_features, bias=True, out_dtype=out_dtype, **kwargs
        )

    def forward(self, x):
        inter_features = self.binarylinear(x)
        out = self.groupconv(inter_features)

        if self.dump_mode:
            return out, inter_features
        else:
            return out

    def golden_mode(self):
        self.groupconv.golden_mode()
