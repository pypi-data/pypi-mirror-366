from typing import TYPE_CHECKING, Any, Callable, Dict

import torch
from torch import nn

if TYPE_CHECKING:
    from ...quant_op import TensorQuantizer  # pragma: no cover


__all__ = ["ModelCompressorModule"]


class ModelCompressorModule(torch.nn.Module):
    def __init__(self, org_target: Callable, org_args: dict = None, is_module: bool = True) -> None:
        super(ModelCompressorModule, self).__init__()

        self.num_inputs = 0
        self.input_shape = []
        self.input_dtype = []
        self.output_shape = None
        self.output_dtype = 'auto'

        # TODO: 추가 필요
        self.device = None

        self.org_target = org_target
        self.is_module = is_module

        if is_module:
            self.org_target_type = type(org_target)
        else:
            self.org_target_type = org_target

        # if is_module:
        #     self.org_module = org_target
        # else:
        #     self._set_org_forward(org_target)

        self.dummy_forwarding = True

    # def _set_org_forward(self, org_target):
    #     self.org_forward = org_target

    def _collect_in_info(self, *args, **kwargs):
        self.num_inputs = len(args)
        for input in args:
            if isinstance(input, torch.Tensor):
                _input_dtype = str(input.dtype)
                _input_shape = input.shape
            else:
                _input_dtype = 'int' if isinstance(input, int) else 'float'
                _input_shape = [0]

            self.input_dtype.append(_input_dtype)
            self.input_shape.append(_input_shape)

        return

    def _collect_out_info(self, output):
        # TODO : 현재 output 은 항상 한개라고 가정하고 있으며, tuple 일 경우에 대해서 제한적으로 예외처리 되어 있음
        if isinstance(output, tuple):
            if isinstance(output[0], int):
                self.output_dtype = 'int'
                self.output_shape = [0] * len(output)
            elif isinstance(output[0], float):
                self.output_dtype = 'int'
                self.output_shape = [0] * len(output)
            else:  # for Llamarotary embedding
                self.output_shape = torch.concat(output, 0).shape
                self.output_dtype = torch.concat(output, 0).dtype
            return

        if isinstance(output, torch.Tensor):
            self.output_dtype = str(output.dtype)
            self.output_shape = output.shape
        else:
            self.output_dtype = 'int' if isinstance(output, int) else 'float'
            self.output_shape = [0]

        return

    # @abstractmethod
    # def forward(self, *args, **kwargs):

    #     raise NotImplementedError

    def dummy_forward(self, *args, **kwargs):
        """
        실제 dummy forwarding만 하는 과정... 연산은 해야겠지만, 주 목적은
        datatype 을 잘 골라내고, 의미 있는 quantizer 를 붙이기 위한 과정
        """
        self._collect_in_info(*args, **kwargs)
        output = super().__call__(*args, **kwargs)
        self._collect_out_info(output)

        self.dummy_forwarding = False

        return output

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.dummy_forwarding:
            output = self.dummy_forward(*args, **kwargs)
            return output

        return super().__call__(*args, **kwargs)

    def get_qmeta(self) -> Dict:
        from ...quant_op import TensorQuantizer

        qmeta = {}
        tensor_quantizers = _find_tensor_quantizers(self)

        for tq_name, tq in tensor_quantizers.items():
            tq: TensorQuantizer
            tq_meta = {}
            tq_meta['quant_descriptor'] = tq.quant_desc.get_static_data()
            tq_meta['path_config'] = tq.get_path_config()

            qmeta[tq_name.split('.')[-1]] = tq_meta

        return qmeta

    def get_tensor_quantizers(self) -> Dict[str, 'TensorQuantizer']:
        return _find_tensor_quantizers(self)

    def get_weight_tensor_quantizers(self) -> Dict[str, 'TensorQuantizer']:
        tq_modules = _find_tensor_quantizers(self)
        weight_tq_modules = {
            tq_name: tq_modules[tq_name] for tq_name in tq_modules if '_weight_quantizer' in tq_name
        }
        return weight_tq_modules

    def get_input_tensor_quantizers(self) -> Dict[str, 'TensorQuantizer']:
        tq_modules = _find_tensor_quantizers(self)
        input_tq_modules = {
            tq_name: tq_modules[tq_name] for tq_name in tq_modules if '_input' in tq_name
        }
        return input_tq_modules

    def calibrate_weight_only(self):
        for _, tq_module in self.get_weight_tensor_quantizers().items():
            tq_module(self.org_target.weight)


def _find_tensor_quantizers(torch_module: nn.Module) -> Dict[str, 'TensorQuantizer']:
    """
    input torch_module안에 있는 모든 TensorQuantizer를 찾아서 return합니다.

    Return
       - {attribute_name : TensorQuantizer}
    """
    from ...quant_op import TensorQuantizer

    results = {}
    for tq_name, tq_module in torch_module.named_modules():
        if isinstance(tq_module, TensorQuantizer):
            results[tq_name] = tq_module

    return results
