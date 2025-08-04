from typing import Callable

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleBinary"]


class ModelCompressorModuleBinary(ModelCompressorModule):
    default_quant_desc_input = descriptor.QUANT_DESC_BF16_PER_TENSOR

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        **kwargs,
    ):
        super(ModelCompressorModuleBinary, self).__init__(org_target, org_args, is_module)
        # quant_desc_input_0 = _utils.pop_quant_desc_in_kwargs(
        #     self.__class__, input_only=True, **kwargs
        # )
        self._init_quantizer(**kwargs)

    def _init_quantizer(self, **quant_desc):
        quant_desc_input_0, quant_desc_input_1 = _utils.pop_quant_desc_in_kwargs(
            self.__class__, func_type=2, **quant_desc
        )
        self._input_0_quantizer = TensorQuantizer(quant_desc_input_0)
        self._input_1_quantizer = TensorQuantizer(quant_desc_input_1)

    def load_quant_descriptor(self, **quant_desc):
        self._init_quantizer(**quant_desc)

    def forward(self, input_0, input_1, **kwargs):
        quant_input_0 = self._input_0_quantizer(input_0)
        quant_input_1 = self._input_1_quantizer(input_1)
        output = self.org_target(quant_input_0, quant_input_1, **kwargs)
        # if not hasattr(self, 'org_module'):
        #     output = self.org_forward(quant_input_0, quant_input_1, **kwargs)
        # else:
        #     raise ValueError('Binary module with org_module has not been implemented yet')

        return output
