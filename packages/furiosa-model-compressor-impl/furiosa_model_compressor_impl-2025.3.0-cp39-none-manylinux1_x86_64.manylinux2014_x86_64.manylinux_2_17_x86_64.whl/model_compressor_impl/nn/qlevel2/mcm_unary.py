from typing import Callable

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleUnary"]


class ModelCompressorModuleUnary(ModelCompressorModule):
    default_quant_desc_input = descriptor.QUANT_DESC_FP32

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        **kwargs,
    ):
        super(ModelCompressorModuleUnary, self).__init__(org_target, org_args, is_module)
        self._init_quantizer(**kwargs)

    def _init_quantizer(self, **quant_desc):
        quant_desc_input = _utils.pop_quant_desc_in_kwargs(
            self.__class__, input_only=True, **quant_desc
        )
        self._input_quantizer = TensorQuantizer(quant_desc_input)

    def load_quant_descriptor(self, **quant_desc):
        self._init_quantizer(**quant_desc)

    def forward(self, input, *args, **kwargs):
        quant_input = self._input_quantizer(input)
        output = self.org_target(quant_input, *args, **kwargs)
        # if hasattr(self, 'org_module'):
        #     output = self.org_module(quant_input, *args, **kwargs)
        # elif hasattr(self, 'org_forward'):
        #     output = self.org_forward(quant_input, *args, **kwargs)
        # else:
        #     raise ValueError('Forward function cannot be performed. Recommended to check __init__.')

        return output
