import torch

from ..modeling.bcq_groupconv2d import _BCQ_GroupConv2d
from ..modeling.binaryconv2d import _BinaryConv2d
from .qlv3_old_module import QLV3_OldModule

__all__ = ["QLV3_BCQConv2d"]


class QLV3_BCQConv2d(QLV3_OldModule):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        nbits,
        stride=(2, 2),
        padding=(1, 1),
        dilation=(1, 1),
        groups=1,
        padding_mode="zeros",
        device=None,
        out_dtype=torch.float64,
        dump_mode=False,
        **kwargs,
    ):
        super(QLV3_BCQConv2d, self).__init__()
        self.dump_mode = dump_mode
        self.binaryconv = _BinaryConv2d(
            in_channels,
            out_channels * nbits,
            kernel_size,
            stride,
            padding,
            dilation,
            groups,
            padding_mode,
            **kwargs,
        )

        self.groupconv = _BCQ_GroupConv2d(
            out_channels * nbits, out_channels, bias=True, out_dtype=out_dtype, **kwargs
        )

    def forward(self, x):
        inter_features = self.binaryconv(x)
        out = self.groupconv(inter_features)

        if self.dump_mode:
            return out, inter_features
        else:
            return out

    def golden_mode(self):
        self.groupconv.golden_mode()
