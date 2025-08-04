import logging

import torch
from torch import Tensor
import torch.nn

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from ...utils import log_first_n
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleOutput"]


logger = logging.getLogger('quant_output')


class ModelCompressorModuleOutput(ModelCompressorModule, _utils.QuantMixin):
    default_quant_desc_input = descriptor.QUANT_DESC_FP32

    def __init__(
        self,
        **kwargs,
    ):
        super(ModelCompressorModuleOutput, self).__init__(torch.nn.Identity(), is_module=True)
        quant_desc_input = _utils.pop_quant_desc_in_kwargs(
            self.__class__, input_only=True, **kwargs
        )
        self._input_quantizer = TensorQuantizer(quant_desc_input)
        self.output_shape = kwargs.pop("output_shape", None)

    def _init_quantizer(self, **quant_desc):
        quant_desc_input = _utils.pop_quant_desc_in_kwargs(
            self.__class__, input_only=True, **quant_desc
        )
        self._input_quantizer = TensorQuantizer(quant_desc_input)

    def load_quant_descriptor(self, **quant_desc):
        self._init_quantizer(**quant_desc)

    def forward(self, input: Tensor) -> Tensor:
        if isinstance(input, list):
            log_first_n(
                logger,
                logging.WARNING,
                f"'{self._get_name()}' bypass input because it received unexpected data format.",
                1,
            )
            return input

        quant_input = self._input_quantizer(input)
        return quant_input
