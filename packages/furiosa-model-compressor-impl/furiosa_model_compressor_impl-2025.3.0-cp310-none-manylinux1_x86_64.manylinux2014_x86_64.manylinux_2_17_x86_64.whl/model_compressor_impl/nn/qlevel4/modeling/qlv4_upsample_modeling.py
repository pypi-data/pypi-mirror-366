import torch
from torch import Tensor, nn
from torch.nn.common_types import _size_any_t, _ratio_any_t
from typing import Optional


__all__ = [
    "QLV4_Upsample2d_MOD",
]


class QLV4_Upsample2d_MOD(nn.Module):
    def __init__(
        self,
        size: Optional[_size_any_t],
        scale_factor: Optional[_ratio_any_t],
        mode: str,
        align_corners: Optional[bool],
        recompute_scale_factor: Optional[bool],
    ):
        super().__init__()
        self.size = size
        if isinstance(scale_factor, (list, tuple)):
            assert len(scale_factor) == 2
            self.scale_factors = scale_factor
        else:
            self.scale_factors = [scale_factor for _ in range(2)]

        if mode != 'nearest':
            raise NotImplementedError("Current Qlevel4 module assumes nearest upsampling as aten implements differnt upsampling methods as distinct functons. Will be addressed soon")
        self.mode = mode
        self.align_conrers = align_corners
        self.recompute_scale_factor = recompute_scale_factor


    def forward(self, input):
        # We have only seen 2d nereast upsample, and aten implements nn.Upsample in numerous functions (e.g., upsample_nearest2d, upsample_bilinear3d,...)
        # Waiting on torch.ops.aten.interpolate to be implemented...
        output = torch.ops.aten.upsample_nearest2d(input, self.size, self.scale_factors)
        return output

