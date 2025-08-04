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


"""Quantized Linear"""
from collections import OrderedDict
import warnings

import torch
from torch import nn

from ....utils import DATA_MATCHER, real_dtype_map
from ...custom_ops.wrap_fucn_with_custom_ops import wrap_func_with_type_emulation

__all__ = ["QLV4_Linear_MOD"]


class QLV4_Linear_MOD(nn.Module):
    def __init__(
        self,
        emul_dtype,
        node_name,
        org_target,
        weight_real_dtype,
        weight_quantizer,
        in_features,
        out_features,
    ):
        super().__init__()
        self.weight_real_dtype = weight_real_dtype
        self.emul_dtype = emul_dtype
        self.org_target = org_target

        self.register_buffer(
            'weight_scale',
            (weight_quantizer['_merged_scale'] if weight_quantizer['_dequantize'] else None),
            persistent=False,
        )
        self.register_buffer(
            'weight_zero_point',
            (weight_quantizer['_zero_point'] if weight_quantizer['_dequantize'] else None),
            persistent=False,
        )
        self.weight_asymmetric = (
            weight_quantizer['quant_desc'].asymmetric if weight_quantizer['_dequantize'] else False
        )
        self.group_size = getattr(weight_quantizer["quant_desc"], "group_size", None)
        self.in_features = in_features
        self.out_features = out_features
        self.node_name = node_name

    def forward(self, input):

        _input = input
        _weight = self.org_target.weight

        weight_decoding_flag, _weight = self.decoding_weight(_input, _weight)

        input_real_dtype = (
            'fp8-E4M3'
            if _input.dtype == torch.int8 and self.weight_real_dtype == 'fp8-E4M3'
            else real_dtype_map(_input)
        )
        weight_real_dtype = (
            real_dtype_map(_weight) if weight_decoding_flag else self.weight_real_dtype
        )

        out_dtype = (
            torch.float32
            if input.dtype.is_floating_point or input_real_dtype == 'fp8-E4M3'
            else torch.int32
        )
        output = wrap_func_with_type_emulation(
            [_input, _weight],
            [DATA_MATCHER[input_real_dtype], DATA_MATCHER[weight_real_dtype]],
            out_dtype,
            self.node_name + '_linear',
            self.emul_dtype,
            lambda x, y: torch.ops.aten.linear(x, y, bias=None),
        )

        return output

    def decoding_weight(self, input, weight):
        weight_decoding_flag = False
        if weight.dtype == torch.float32:
            raise ValueError("Some type casting exists after create_quantsim_model")

        if input.dtype == torch.bfloat16 and weight.dtype != torch.bfloat16:
            if self.weight_real_dtype in ['int4', 'fp8-E4M3']:
                weight = torch.ops.furiosa.type_emulation_in(
                    weight, DATA_MATCHER[self.weight_real_dtype], None, torch.float64
                )
                weight = torch.ops.furiosa.type_emulation_out(weight, torch.float32, None)
            else:
                weight = torch.ops.aten._to_copy(weight, dtype=torch.float32)  # VE type cast

            # decoding weight
            if self.weight_real_dtype == 'int4':
                weight = torch.ops.aten.view(weight, [-1, self.group_size])
            if self.weight_asymmetric:
                weight = torch.ops.aten.sub(weight, self.weight_zero_point)
            weight = torch.ops.aten.mul.Tensor(weight, self.weight_scale)
            if self.weight_real_dtype == 'int4':
                weight = torch.ops.aten.view(weight, [self.out_features, self.in_features])
            weight = torch.ops.aten._to_copy(weight, dtype=input.dtype)
            weight_decoding_flag = True

        return weight_decoding_flag, weight

    def state_dict(self, *args, destination=None, prefix='', keep_vars=False):
        r"""Return a dictionary containing references to the whole state of the module.

        Both parameters and persistent buffers (e.g. running averages) are
        included. Keys are corresponding parameter and buffer names.
        Parameters and buffers set to ``None`` are not included.

        .. note::
            The returned object is a shallow copy. It contains references
            to the module's parameters and buffers.

        .. warning::
            Currently ``state_dict()`` also accepts positional arguments for
            ``destination``, ``prefix`` and ``keep_vars`` in order. However,
            this is being deprecated and keyword arguments will be enforced in
            future releases.

        .. warning::
            Please avoid the use of argument ``destination`` as it is not
            designed for end-users.

        Args:
            destination (dict, optional): If provided, the state of module will
                be updated into the dict and the same object is returned.
                Otherwise, an ``OrderedDict`` will be created and returned.
                Default: ``None``.
            prefix (str, optional): a prefix added to parameter and buffer
                names to compose the keys in state_dict. Default: ``''``.
            keep_vars (bool, optional): by default the :class:`~torch.Tensor` s
                returned in the state dict are detached from autograd. If it's
                set to ``True``, detaching will not be performed.
                Default: ``False``.

        Returns:
            dict:
                a dictionary containing a whole state of the module

        Example::

            >>> # xdoctest: +SKIP("undefined vars")
            >>> module.state_dict().keys()
            ['bias', 'weight']

        """
        # TODO: Remove `args` and the parsing logic when BC allows.
        if len(args) > 0:
            # DeprecationWarning is ignored by default
            warnings.warn(
                "Positional args are being deprecated, use kwargs instead. Refer to "
                "https://pytorch.org/docs/main/generated/torch.nn.Module.html#torch.nn.Module.state_dict"
                " for details.",
                FutureWarning,
                stacklevel=2,
            )
            if destination is None:
                destination = args[0]
            if len(args) > 1 and prefix == '':
                prefix = args[1]
            if len(args) > 2 and keep_vars is False:
                keep_vars = args[2]

        if destination is None:
            destination = OrderedDict()
            destination._metadata = OrderedDict()

        local_metadata = dict(version=self._version)
        if hasattr(destination, "_metadata"):
            destination._metadata[prefix[:-1]] = local_metadata

        for hook in self._state_dict_pre_hooks.values():
            hook(self, prefix, keep_vars)
        self._save_to_state_dict(destination, prefix, keep_vars)
        for name, module in self._modules.items():
            if name == 'org_target':
                continue
            if module is not None:
                module.state_dict(
                    destination=destination, prefix=prefix + name + '.', keep_vars=keep_vars
                )
        for hook in self._state_dict_hooks.values():
            hook_result = hook(self, destination, prefix, local_metadata)
            if hook_result is not None:
                destination = hook_result
        return destination
