from typing import Callable

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleEinsum"]


# TODO: gpt-j/huggingface_rope 의 apply_rotary_pos_emb() 내부 einsum 만을 위한 특수 구현
class ModelCompressorModuleEinsum(ModelCompressorModule):
    default_quant_desc_input = descriptor.QUANT_DESC_BF16_PER_TENSOR

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        **kwargs,
    ):
        super(ModelCompressorModuleEinsum, self).__init__(org_target, org_args, is_module)
        self._init_quantizer(**kwargs)

    def _init_quantizer(self, **quant_desc):
        quant_desc_input_1, quant_desc_input_2 = _utils.pop_quant_desc_in_kwargs(
            self.__class__, func_type=4, **quant_desc
        )
        # TODO : legacy convert_q2_to_q3 사용을 위해 mcm_insum 의 quanizer index는 1 부터 시작한다.
        self._input_1_quantizer = TensorQuantizer(quant_desc_input_1)
        self._input_2_quantizer = TensorQuantizer(quant_desc_input_2)

    def load_quant_descriptor(self, **quant_desc):
        self._init_quantizer(**quant_desc)

    def forward(self, equation, input_1, input_2, **kwargs):
        quant_input_1 = self._input_1_quantizer(input_1)
        quant_input_2 = self._input_2_quantizer(input_2)
        output = self.org_target(equation, quant_input_1, quant_input_2, **kwargs)

        return output
