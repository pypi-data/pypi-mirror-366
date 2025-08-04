import torch
from torch import nn
import torch.nn.functional as F

from .....utils.datamapper import DATA_MAPPER, DATA_MATCHER

__all__ = ["_BinaryConv2d"]


class _BinaryConv2d(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size,
        stride=(2, 2),
        padding=(1, 1),
        dilation=(1, 1),
        groups=1,
        padding_mode="zeros",
        **kwargs,
    ):
        super(_BinaryConv2d, self).__init__()
        self.emul_dtype = torch.float64
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding
        self.dilation = dilation
        self.groups = groups
        self.padding_mode = padding_mode
        device = kwargs.pop("device", None)
        self.weight_real_dtype = DATA_MATCHER[
            kwargs.pop('dtype', 'int8')
        ]  # weight is binary, so dtype could be fixed
        factory_kwargs = {'device': device, 'dtype': DATA_MAPPER[self.weight_real_dtype]}

        # set parameters
        self.weight = nn.Parameter(
            torch.empty((out_channels, in_channels // groups, *kernel_size), **factory_kwargs),
            requires_grad=False,
        )

        self.register_buffer('bias', None)
        self.zero_point = 0.0

    def forward(self, x):
        _weight = self.weight.data.to(self.emul_dtype)  # Type cast for accumulation
        out_dtype = (
            torch.float32 if x.dtype.is_floating_point else torch.int32
        )  # out_dtype depends on only input type
        x = x.to(device=_weight.device, dtype=_weight.dtype)  # Type cast for accumulation

        # decode binary weight to  1, -1
        m_ones = -1 * torch.ones(_weight.shape).to(device=_weight.device, dtype=_weight.dtype)
        decoded_weight = torch.where(_weight == 1.0, _weight, m_ones)

        # forward
        if self.padding_mode != "zeros":
            padded_x = F.pad(
                x,
                (self.padding[1], self.padding[1], self.padding[0], self.padding[0]),
                mode=self.padding_mode,
            )
        else:
            padded_x = F.pad(
                x,
                (self.padding[1], self.padding[1], self.padding[0], self.padding[0]),
                mode="constant",
                value=self.zero_point,
            )

        output = F.conv2d(
            padded_x,
            decoded_weight,
            self.bias,
            self.stride,
            (0, 0),
            self.dilation,
            self.groups,
        )

        # DPE to VE type cast
        output = output.to(out_dtype)

        return output
