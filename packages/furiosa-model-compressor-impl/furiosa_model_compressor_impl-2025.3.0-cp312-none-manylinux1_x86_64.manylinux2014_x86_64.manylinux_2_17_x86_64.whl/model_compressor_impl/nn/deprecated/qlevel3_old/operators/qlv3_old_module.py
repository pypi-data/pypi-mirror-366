from typing import Dict

from torch import nn

__all__ = [
    'QLV3_OldModule',
]


class QLV3_OldModule(nn.Module):
    def get_qmeta(self) -> Dict:
        from .....quant_op import TensorQuantizer

        qmeta = {}
        tensor_quantizers = _find_tensor_quantizers(self)

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


def _find_tensor_quantizers(torch_module: nn.Module):
    from .....quant_op import TensorQuantizer

    """
    input torch_module안에 있는 모든 TensorQuantizer를 찾아서 return합니다.

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

    recursive_search(torch_module)
    return results
