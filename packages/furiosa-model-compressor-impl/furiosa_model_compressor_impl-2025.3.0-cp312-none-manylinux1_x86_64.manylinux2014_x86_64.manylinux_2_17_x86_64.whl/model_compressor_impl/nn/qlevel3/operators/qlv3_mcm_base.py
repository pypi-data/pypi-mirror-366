from typing import Any, Dict

from torch import Tensor, nn

__all__ = [
    "QLV3_ModelCompressorModule",
]


class QLV3_ModelCompressorModule(nn.Module):
    def __init__(self, qlv2_mcm):
        super().__init__()

        def _identity_func(x: Tensor) -> Tensor:
            return x

        self.input_quantizer = nn.ModuleList([])  # this space is reserved for qlv2
        self.output_quantizer = nn.ModuleList([])

        self.output_dtype = qlv2_mcm.output_dtype
        self.output_shape = qlv2_mcm.output_shape

        self.org_target = qlv2_mcm.org_target
        self.org_target_type = qlv2_mcm.org_target_type

    def qlv3_forward(self, *args, **kwargs):
        raise NotImplementedError

    def _call_impl(self, *args: Any, **kwargs: Any) -> Any:
        output = self.qlv3_forward(*args, **kwargs)

        return output

    def set_input_quantizer(self, *args, **kwargs):
        raise NotImplementedError

    def set_output_quantizer(self, *args, **kwargs):
        raise NotImplementedError

    @property
    def get_attr_for_qlv4(self):
        return dict(self.__dict__, self._additional_attr)

    @property
    def _additional_attr(self):
        return {}

    def get_qmeta(self) -> Dict:
        from ....quant_op import TensorQuantizer

        qmeta = {}
        tensor_quantizers = self._find_tensor_quantizers()

        for tq_name, tq in tensor_quantizers.items():
            tq: TensorQuantizer
            tq_meta = {}
            tq_meta['quant_descriptor'] = tq.quant_desc.get_static_data()
            tq_meta['path_config'] = tq.get_path_config()
            for child in self.children():
                if hasattr(child, 'weight_real_dtype'):
                    tq_meta['weight_real_dtype'] = child.weight_real_dtype

            qmeta[tq_name] = tq_meta

        return qmeta

    def _find_tensor_quantizers(self):
        from ....quant_op import TensorQuantizer

        """
        모든 TensorQuantizer를 찾아서 return합니다.

        Return
        - {attribute_name : TensorQuantizer}
        """
        results = {}

        def recursive_search(mod: nn.Module):

            for child_name, child in mod.named_children():
                if isinstance(child, TensorQuantizer):
                    results[child_name] = child
                else:
                    recursive_search(child)

        recursive_search(self)
        return results
