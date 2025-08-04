from typing import Callable

import torch
from torch import nn

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleConcat"]


class ModelCompressorModuleConcat(ModelCompressorModule):
    default_quant_desc_input = descriptor.QUANT_DESC_DISABLE

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        num_inputs: int = 0,
        axis: int = 1,
        **kwargs,
    ):
        super(ModelCompressorModuleConcat, self).__init__(org_target, org_args, is_module, **kwargs)
        self._input_quantizer = nn.ModuleList([])
        self.num_inputs = num_inputs
        self._init_quantizer(**kwargs)

    def _init_quantizer(self, **quant_desc):
        self._input_quantizer = nn.ModuleList([])
        if len(quant_desc) == 0:
            quant_desc = {}
            for i in range(self.num_inputs):
                # quant_desc 를 하나씩 생성한다.
                _quant_desc = _utils.pop_quant_desc_in_kwargs(self.__class__, input_only=True)
                quant_desc[i] = _quant_desc
        else:
            quant_desc = _utils.pop_quant_desc_in_kwargs(
                self.__class__, input_only=True, func_type=3, **quant_desc
            )

        for _, desc in quant_desc.items():
            if not isinstance(desc, descriptor.QuantDescriptor):
                continue
            self._input_quantizer.append(TensorQuantizer(desc))

    def load_quant_descriptor(self, **quant_desc):
        # re-initialize input quantizer
        self._init_quantizer(**quant_desc)

    def dummy_forward(self, *args, **kwargs):
        if not len(self._input_quantizer) == 0:
            # raise RuntimeError("input quantizer for concat is already created")
            # This code is to pypass the problem that dummy_forwarding is unexpectedly performed at initial validation
            return super().dummy_forward(*args, **kwargs)

        raise RuntimeError("mcm concat doesen't have input_quantizer")

    def forward(self, *args, **kwargs):
        quant_input = []
        input_tensor = args[0]
        for i, tensor in enumerate(input_tensor):
            if isinstance(tensor, torch.Tensor):
                quant_input.append(self._input_quantizer[i](tensor))

        if len(args) > 1:
            if len(args) == 2:
                kwargs["dim"] = args[1]
            else:
                raise NotImplementedError("Not Expected case.")

        args = (tuple(quant_input),)
        output = self.org_target(*args, **kwargs)

        return output
