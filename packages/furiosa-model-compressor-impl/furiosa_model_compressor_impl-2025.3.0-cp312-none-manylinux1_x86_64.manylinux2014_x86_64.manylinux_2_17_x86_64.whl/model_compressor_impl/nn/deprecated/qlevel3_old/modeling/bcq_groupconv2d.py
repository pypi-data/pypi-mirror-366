import torch
from torch import nn
from torch.nn import functional as F

from .....quant_op.custom_ops import away_from_zero_round
from .....utils import DATA_MAPPER

__all__ = ["_BCQ_GroupConv2d"]


class _BCQ_GroupConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, bias=True, out_dtype=None, **kwargs):
        super(_BCQ_GroupConv2d, self).__init__()
        self.emul_dtype = torch.float32
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.kernel_size = 1
        self.groups = out_channels
        device = kwargs.pop("device", None)
        factory_kwargs = {'device': device, 'dtype': torch.float32}
        factory_kwargs_bias = {'device': device, 'dtype': torch.float32}

        # set parameters
        self.basis = nn.Parameter(
            torch.empty((out_channels, in_channels // out_channels, 1, 1), **factory_kwargs),
            requires_grad=False,
        )
        if bias:
            self.bias = nn.Parameter(
                torch.empty(out_channels, **factory_kwargs_bias), requires_grad=False
            )
        else:
            self.register_buffer('bias', None)

        quant_desc_output = kwargs.pop("quant_desc_output", None)
        if quant_desc_output is not None:
            self._o_dtype = DATA_MAPPER[quant_desc_output.dtype]
        else:
            # layer test mode
            self._o_dtype = out_dtype

    def forward(self, x):
        _basis = self.basis.data.to(self.emul_dtype)  # basis type casting
        _bias = self.bias.data.to(self.emul_dtype)  # bias type casting

        out = x.to(torch.float32)  # Type casting in Vector Engine input interface: int32 -> fp32
        out = out.to(self.emul_dtype)  # For using emul_dtype operator
        out = F.conv2d(out, _basis, _bias, stride=1, groups=self.groups)

        if not self._o_dtype.is_floating_point:
            # quantize
            out = away_from_zero_round(out)
        out = out.to(self._o_dtype)

        return out

    def golden_mode(self):
        self.emul_dtype = torch.float64
