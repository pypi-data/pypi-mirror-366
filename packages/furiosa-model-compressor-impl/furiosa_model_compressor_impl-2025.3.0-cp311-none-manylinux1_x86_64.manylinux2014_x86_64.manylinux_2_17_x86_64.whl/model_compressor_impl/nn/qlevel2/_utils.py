#
# Copyright (c) 2021, NVIDIA CORPORATION. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


"""Some helper functions for implementing quantized modules"""
import copy
import inspect
import logging

from torch import nn

from ... import descriptor
from ...quant_op import TensorQuantizer

__all__ = ['QuantMixin', 'pop_quant_desc_in_kwargs']

logger = logging.getLogger("QunatMixin")


class QuantMixin:
    """Mixin class for adding basic quantization logic to quantized modules"""

    default_quant_desc_input = copy.deepcopy(descriptor.QUANT_DESC_DISABLE)
    default_quant_desc_weight = copy.deepcopy(descriptor.QUANT_DESC_DISABLE)

    @classmethod
    def set_default_quant_desc_input(cls, value):
        """
        Args:
            value: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
        """
        if not isinstance(value, descriptor.QuantDescriptor):
            raise ValueError("{} is not an instance of QuantDescriptor!")
        cls.default_quant_desc_input = copy.deepcopy(value)

    @classmethod
    def set_default_quant_desc_weight(cls, value):
        """
        Args:
            value: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
        """
        if not isinstance(value, descriptor.QuantDescriptor):
            raise ValueError("{} is not an instance of QuantDescriptor!")
        cls.default_quant_desc_weight = copy.deepcopy(value)

    def init_quantizer(
        self, quant_desc_input, quant_desc_weight, module_type=None, num_layers=None
    ):
        """Helper function for __init__ of quantized module

        Create input and weight quantizer based on quant_desc passed by kwargs, or default of the class.

        Args:
            quant_desc_input: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
            quant_desc_weight: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
            num_layers: An integer. Default None. If not None, create a list of quantizers.
        """
        if not inspect.stack()[1].function == "__init__":
            raise TypeError(
                "{} should be only called by __init__ of quantized module.".format(__name__)
            )
        self._fake_quant = True
        if (not quant_desc_input.fake_quant) or (not quant_desc_weight.fake_quant):
            raise ValueError("Only fake quantization is supported!")

        # logger.info(
        #     "Input is %squantized to %d bits in %s with axis %s!",
        #     "" if not quant_desc_input.fake_quant else "fake ",
        #     quant_desc_input.num_bits,
        #     self.__class__.__name__,
        #     quant_desc_input.axis,
        # )
        # logger.info(
        #     "Weight is %squantized to %d bits in %s with axis %s!",
        #     "" if not quant_desc_weight.fake_quant else "fake ",
        #     quant_desc_weight.num_bits,
        #     self.__class__.__name__,
        #     quant_desc_weight.axis,
        # )

        quant_desc_input.module_type = module_type
        quant_desc_weight.module_type = module_type
        if num_layers is None:
            self._input_quantizer = TensorQuantizer(quant_desc_input)
            self._weight_quantizer = TensorQuantizer(quant_desc_weight)
        else:
            self._input_quantizers = nn.ModuleList(
                [TensorQuantizer(quant_desc_input) for _ in range(num_layers)]
            )
            self._weight_quantizers = nn.ModuleList(
                [TensorQuantizer(quant_desc_weight) for _ in range(num_layers)]
            )

    # pylint:disable=missing-docstring
    @property
    def input_quantizer(self):
        return self._input_quantizer

    @property
    def weight_quantizer(self):
        return self._weight_quantizer

    # pylint:enable=missing-docstring


#   class QuantInputMixin:
#       """Mixin class for adding basic quantization logic to quantized modules"""
#
#       default_quant_desc_input = copy.deepcopy(descriptor.QUANT_DESC_FP32)
#
#       @classmethod
#       def set_default_quant_desc_input(cls, value):
#           """
#           Args:
#               value: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
#           """
#           if not isinstance(value, descriptor.QuantDescriptor):
#               raise ValueError("{} is not an instance of QuantDescriptor!")
#           cls.default_quant_desc_input = copy.deepcopy(value)
#
#       def init_quantizer(self, quant_desc_input):
#           """Helper function for __init__ of simple quantized module
#
#           Create input quantizer based on quant_desc passed by kwargs, or default of the class.
#
#           Args:
#               quant_desc_input: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`
#           """
#           if not inspect.stack()[1].function == "__init__":
#               raise TypeError(
#                   "{} should be only called by __init__ of quantized module.".format(__name__)
#               )
#           self._fake_quant = True
#           if not quant_desc_input.fake_quant:
#               raise ValueError("Only fake quantization is supported!")
#
#           # logger.info(
#           #     "Input is %squantized to %d bits in %s with axis %s!",
#           #     "" if not quant_desc_input.fake_quant else "fake ",
#           #     quant_desc_input.num_bits,
#           #     self.__class__.__name__,
#           #     quant_desc_input.axis,
#           # )
#
#           self._input_quantizer = TensorQuantizer(quant_desc_input)
#
#       # pylint:disable=missing-docstring
#       @property
#       def input_quantizer(self):
#           return self._input_quantizer
#
#       # pylint:enable=missing-docstring


def pop_quant_desc_in_kwargs(quant_cls, input_only=False, func_type=None, **kwargs):
    """Pop quant descriptors in kwargs

    If there is no descriptor in kwargs, the default one in quant_cls will be used

    Arguments:
       quant_cls: A class that has default quantization descriptors
       input_only: A boolean. If True, pop quant_desc_input only, not quant_desc_weight. Default false.

    Keyword Arguments:
       quant_desc_input: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`.
           Quantization descriptor of input.
       quant_desc_weight: An instance of :class:`QuantDescriptor <pytorch_quantization.tensor_quant.QuantDescriptor>`.
           Quantization descriptor of weight.
    """

    def _init_quant_desc_with_default(default_quant_dest: dict) -> descriptor.QuantDescriptor:
        new_dict = {}
        for k, v in default_quant_dest.__dict__.items():
            if k.startswith('_'):
                new_dict['_'.join(k.split('_')[1:])] = v
            else:
                new_dict[k] = v

        return descriptor.QuantDescriptor(**new_dict)

    # TODO
    if func_type == 1:
        quant_desc_weight = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_weight", quant_cls.default_quant_desc_weight)
        )

        return quant_desc_weight

    if func_type == 2:
        quant_desc_input_0 = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_input_0", quant_cls.default_quant_desc_input)
        )
        quant_desc_input_1 = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_input_1", quant_cls.default_quant_desc_input)
        )

        return quant_desc_input_0, quant_desc_input_1

    # N operend
    if func_type == 3:
        quant_desc_dict = {
            k: _init_quant_desc_with_default(v) for k, v in kwargs.items() if k.startswith('quant')
        }

        return quant_desc_dict

    if func_type == 4:
        # for einsum
        quant_desc_input_1 = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_input_1", quant_cls.default_quant_desc_input)
        )
        quant_desc_input_2 = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_input_2", quant_cls.default_quant_desc_input)
        )

        return quant_desc_input_1, quant_desc_input_2

    quant_desc_input = _init_quant_desc_with_default(
        kwargs.pop("quant_desc_input", quant_cls.default_quant_desc_input)
    )
    if not input_only:
        quant_desc_weight = _init_quant_desc_with_default(
            kwargs.pop("quant_desc_weight", quant_cls.default_quant_desc_weight)
        )

    # # Check if anything is left in **kwargs
    # if kwargs:
    #     raise TypeError("Unused keys: {}".format(kwargs.keys()))

    if input_only:
        return quant_desc_input
    return quant_desc_input, quant_desc_weight
