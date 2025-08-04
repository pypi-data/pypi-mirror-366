from typing import Callable

import torch
from torch import Tensor
import torch.nn
import torch.nn.functional as F

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleEmbedding"]


class ModelCompressorModuleEmbedding(ModelCompressorModule, _utils.QuantMixin):
    default_quant_desc_weight = descriptor.QUANT_DESC_DISABLE
    default_quant_desc_input = descriptor.QUANT_DESC_DISABLE

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        **kwargs,
    ):
        super(ModelCompressorModuleEmbedding, self).__init__(org_target, org_args, is_module)
        quant_desc_input, quant_desc_weight = _utils.pop_quant_desc_in_kwargs(
            self.__class__, **kwargs
        )

        self.init_quantizer(
            quant_desc_input, quant_desc_weight, module_type=self.__class__.__name__
        )
        # self.org_module = org_target
        self.output_shape = kwargs.pop("output_shape", None)

    def load_quant_descriptor(self, **quant_desc):
        # re-initialize input quantizer
        self._input_quantizer = TensorQuantizer(quant_desc['quant_desc_input'])
        self._weight_quantizer = TensorQuantizer(quant_desc['quant_desc_weight'])

    def forward(self, input: Tensor) -> Tensor:
        # inputs of embedding are indices, so dtype of embedding input must be int64 or int32
        if input.dtype not in [torch.int64, torch.int32]:
            raise ValueError("input must be long or int type tensor")

        if hasattr(self.org_target, '_hf_hook'):
            args, _ = self.org_target._hf_hook.pre_forward(self.org_target, input)
            input = args[0]

        _input = self._input_quantizer(input)
        quant_weight = self._weight_quantizer(self.org_target.weight)
        output = F.embedding(
            _input,
            quant_weight,
            self.org_target.padding_idx,
            self.org_target.max_norm,
            self.org_target.norm_type,
            self.org_target.scale_grad_by_freq,
            self.org_target.sparse,
        )

        if hasattr(self.org_target, '_hf_hook'):
            output = self.org_target._hf_hook.post_forward(self.org_target, output)

        return output
