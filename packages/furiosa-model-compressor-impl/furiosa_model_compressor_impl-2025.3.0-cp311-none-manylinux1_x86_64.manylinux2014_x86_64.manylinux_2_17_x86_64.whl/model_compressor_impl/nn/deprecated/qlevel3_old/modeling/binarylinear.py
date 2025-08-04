import torch
from torch import nn
import torch.nn.functional as F

from .....utils.datamapper import DATA_MAPPER, DATA_MATCHER

__all__ = ["_BinaryLinear"]


class _BinaryLinear(nn.Module):
    def __init__(
        self,
        in_channel,
        out_channel,
        device=None,
        **kwargs,
    ):
        super(_BinaryLinear, self).__init__()
        self.emul_dtype = torch.float64
        self.in_channel = in_channel
        self.out_channel = out_channel
        device = kwargs.pop("device", None)
        self.weight_real_dtype = DATA_MATCHER[
            kwargs.pop('dtype', 'int8')
        ]  # weight is binary, so dtype could be fixed
        factory_kwargs = {'device': device, 'dtype': DATA_MAPPER[self.weight_real_dtype]}
        # set parameters
        self.weight = nn.Parameter(
            torch.empty((out_channel, in_channel), **factory_kwargs), requires_grad=False
        )
        self.register_parameter('bias', None)

    def forward(self, x):
        _weight = self.weight.data.to(self.emul_dtype)  # Type cast for accumulation
        out_dtype = (
            torch.float32 if x.dtype.is_floating_point else torch.int32
        )  # out_dtype depends on only input type
        x = x.to(device=_weight.device, dtype=_weight.dtype)  # Type cast for accumulation

        # decode binary weight to  1, -1
        m_ones = -1 * torch.ones(_weight.shape).to(device=_weight.device, dtype=_weight.dtype)
        decoded_weight = torch.where(_weight == 1.0, _weight, m_ones)

        # forward linear function
        output = F.linear(x, decoded_weight, self.bias)

        # DPE to VE type cast
        output = output.to(out_dtype)

        return output
