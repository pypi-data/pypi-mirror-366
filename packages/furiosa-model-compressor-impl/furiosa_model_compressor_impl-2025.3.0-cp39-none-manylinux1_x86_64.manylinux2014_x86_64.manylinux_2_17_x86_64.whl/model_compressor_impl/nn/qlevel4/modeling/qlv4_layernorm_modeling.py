from collections import OrderedDict
import warnings

import torch
from torch import Tensor, nn

from ...custom_ops.wrap_fucn_with_custom_ops import wrap_func_with_type_emulation

__all__ = [
    "QLV4_LayerNorm_MOD",
]


class QLV4_LayerNorm_MOD(nn.Module):
    def __init__(
        self,
        emul_dtype,
        node_name,
        org_target,
        normalized_shape,
        eps: float = 1e-5,
        elementwise_affine: bool = True,
    ):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.eps = eps
        self.elementwise_affine = elementwise_affine
        self.org_target = org_target
        self.emul_dtype = emul_dtype
        self.node_name = node_name

    def forward(self, input: Tensor) -> Tensor:
        if input.dtype in [torch.bfloat16, torch.int8]:
            _input = torch.ops.aten._to_copy(input, dtype=torch.float32)  # Type cast for VE
        else:
            _input = input

        if self.emul_dtype == torch.float64:
            output = wrap_func_with_type_emulation(
                [_input, self.org_target.weight, self.org_target.bias],
                ['float32', 'float32', 'float32'],
                torch.float32,
                self.node_name + '_layernorm',
                self.emul_dtype,
                lambda x, y, z: torch.ops.aten.layer_norm(x, self.normalized_shape, y, z, self.eps),
            )
        else:
            output = torch.ops.aten.layer_norm(
                _input,
                self.normalized_shape,
                self.org_target.weight,
                self.org_target.bias,
                self.eps,
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
