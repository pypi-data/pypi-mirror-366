from collections import OrderedDict
from typing import Optional
import warnings

import torch
from torch import nn

from ....utils import DATA_MATCHER

__all__ = ["QLV4_Embedding_MOD"]


class QLV4_Embedding_MOD(nn.Module):
    def __init__(
        self,
        org_target,
        weight_real_dtype,
        emul_dtype,
        node_name,
        _weight_dequantizer=None,
        padding_idx: Optional[int] = None,
        max_norm: Optional[float] = None,
        norm_type: float = 2.0,
        scale_grad_by_freq: bool = False,
        sparse: bool = False,
    ):
        super().__init__()
        self.padding_idx = padding_idx
        self.max_norm = max_norm
        self.norm_type = norm_type
        self.scale_grad_by_freq = scale_grad_by_freq
        self.sparse = sparse
        self.weight_real_dtype = weight_real_dtype
        self.org_target = org_target

        if padding_idx is not None:
            if padding_idx > 0:
                assert padding_idx < self.org_target.weight.size(
                    0
                ), "Padding_idx must be within num_embeddings"
            elif padding_idx < 0:
                assert padding_idx >= -self.org_target.weight.size(
                    0
                ), "Padding_idx must be within num_embeddings"
                self.padding_idx = self.org_target.weight.size(0) + padding_idx
        else:
            self.padding_idx = -1

        self.emul_dtype = emul_dtype
        self.weight_scale = (
            _weight_dequantizer['_merged_scale'] if _weight_dequantizer is not None else None
        )
        self.node_name = node_name

    def forward(self, input):
        # inputs of embedding are indices, so dtype of embedding input must be int64 or int32
        if input.dtype not in [torch.int64, torch.int32]:
            raise ValueError("input must be long or int type tensor")

        _input = input
        _weight = self.org_target.weight

        if _weight.dtype != torch.bfloat16:
            if self.weight_real_dtype in ['int4', 'float8']:
                _weight = torch.ops.furiosa.type_emulation_in(
                    _weight, DATA_MATCHER[self.weight_real_dtype], None, torch.float64
                )
                _weight = torch.ops.furiosa.type_emulation_out(_weight, torch.float32, None)
            else:
                _weight = torch.ops.aten._to_copy(_weight, dtype=torch.float32)  # VE type cast

            # decoding weight
            _weight = torch.ops.aten.mul.Tensor(_weight, self.weight_scale)
            _weight = torch.ops.aten._to_copy(_weight, dtype=self.emul_dtype)

        if self.emul_dtype in [torch.float32, torch.float64]:
            _weight = torch.ops.aten._to_copy(_weight, dtype=self.emul_dtype)
            _input = torch.ops.aten._to_copy(_input, dtype=self.emul_dtype)

        if self.max_norm is not None:
            _input = torch.ops.aten.contiguous(_input)
            _weight = torch.ops.aten.detach(_weight)
            torch.ops.aten.embedding_renorm(_weight, _input, self.max_norm, self.norm_type)

        output = torch.ops.aten.embedding(
            _weight,
            _input,
            self.padding_idx,
            self.scale_grad_by_freq,
            self.sparse,
        )

        return output

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
