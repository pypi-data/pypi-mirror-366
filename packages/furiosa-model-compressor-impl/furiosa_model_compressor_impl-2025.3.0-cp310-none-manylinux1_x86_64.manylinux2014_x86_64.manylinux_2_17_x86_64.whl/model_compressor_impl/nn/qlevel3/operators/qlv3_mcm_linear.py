import torch
from torch import Tensor, nn

from .... import nn as quant_nn
from ..modeling.qlv3_bias_modeling import QLV3_MCM_BIAS_MOD
from ..modeling.qlv3_mcm_linear_modeling import QLV3_ModelCompressorModuleLinear_MOD
from ..precompute import get_precompute_qparams, get_qparams
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = ["QLV3_ModelCompressorModuleLinear"]


class QLV3_ModelCompressorModuleLinear(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleLinear):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        self.weight_quantizer = None
        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)

        self.qlv3_input_pre_quantizer = None
        self.qlv3_output_quantizer = None

        # out_features = self.org_target.out_features

        self.qlv3_linear = QLV3_ModelCompressorModuleLinear_MOD(self.org_target)
        self.qlv3_bias = QLV3_MCM_BIAS_MOD()

    def qlv3_forward(self, *args, **kwargs):
        # linear layer 의 input 은 1개 이기 때문에 첫번째 index 가 tensor
        # input_tensor = args[0]
        # x = self.qlv3_input_quantizer(input_tensor)
        x = self.forward(*args, **kwargs)
        x = self.qlv3_output_quantizer(x)
        # 현재 self.output_quantizer 의 수행은 bias_mod 에 내재되어 있다. 이를 분리해서 끄집어 내야한다.

        return x

    def forward(self, *args, **kwargs) -> Tensor:
        input = args[0]
        output = self.qlv3_linear(input)
        output = self.qlv3_bias(output)

        return output

    def golden_mode(self):
        # TODO : 왜 linaer 는 self.qlv3_linear 에 대한 golden_mode() 가 없지?
        self.qlv3_bias.golden_mode()

    def set_emulation_dtype(self, emul_dtype):
        self.qlv3_linear.set_emulation_dtype(emul_dtype)

    def set_bias_emulation_dtype(self, emul_dtype):
        self.qlv3_bias.set_emulation_dtype(emul_dtype)

    def set_input_quantizer(self, qlv2_mcm):
        self.input_quantizer.append(qlv2_mcm._input_quantizer)
        self.weight_quantizer = qlv2_mcm._weight_quantizer

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': [self.qlv3_input_pre_quantizer],
            'mod': self.qlv3_linear,
            'bias': self.qlv3_bias,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        _input_quantizer = self.input_quantizer[0]
        _weight_quantizer = self.weight_quantizer
        _output_quantizer = self.output_quantizer[0]

        _device = (
            self.org_target.weight.device if self.org_target.weight.device.type != 'meta' else 'cpu'
        )

        if _output_quantizer.quant_desc.num_bits < 8:
            raise NotImplementedError("Not implemented yet!")

        if _input_quantizer.quant_desc.num_bits == 8:

            if not _input_quantizer.quant_desc.dtype == _weight_quantizer.quant_desc.dtype:
                raise ValueError(
                    "if activation is quantized, should so be weight?"
                )  # TODO : W4A8 을 위해 error 수정

            # TODO : 분기별 함수 정리 필요
            if _output_quantizer.quant_desc.num_bits == 8:
                input_qparams = get_qparams(_input_quantizer, if_bcq=False, device=_device)
                weight_qparams = get_qparams(_weight_quantizer, if_bcq=False, device=_device)
                output_qparams = get_qparams(_output_quantizer, if_bcq=False, device=_device)

                # # per-head 일 경우, channel 방향으로 펼치기 TODO : 잘 정리합시다.
                if (
                    not input_qparams[0].shape == output_qparams[0].shape
                    and len(output_qparams[0].shape) != 0
                ):
                    _len_channel = _output_quantizer.quant_desc.input_shape[-1]
                    _head_dim = int(_len_channel / output_qparams[0].shape[0])

                    scale = output_qparams[0].repeat_interleave(_head_dim, dim=0)
                    zero_point = output_qparams[1].repeat_interleave(_head_dim, dim=0)

                    output_qparams = (scale, zero_point)

                # TODO : GQA 처리 hard coding
                if (
                    self.input_quantizer[0].is_shape_changed_by_propagate
                    and not self.input_quantizer[0].rollback
                    and self.input_quantizer[0].quant_desc.axis is not None
                ):
                    input_qparams = list(input_qparams)
                    _num_groups = int(
                        self.input_quantizer[0].quant_desc.org_shape[1]
                        / self.input_quantizer[0].quant_desc.input_shape[1]
                    )
                    if _num_groups > 1:
                        input_qparams[0] = input_qparams[0].repeat_interleave(_num_groups)
                        input_qparams[1] = input_qparams[1].repeat_interleave(_num_groups)

                # TODO : 정말 quantizer 도 넘겨받아야하는가? 그러면... qparam은 왜 따로 받아야 하는가?
                smooth_factor = 1.0
                if (
                    hasattr(_input_quantizer, '_scale_per_channel')
                    and _input_quantizer._scale_per_channel != None
                ):
                    smooth_factor = _input_quantizer._scale_per_channel
                merged_scale, merged_bias, quantized_weight, imbias = get_precompute_qparams(
                    self.org_target,
                    input_qparams,
                    weight_qparams,
                    output_qparams,
                    _input_quantizer,
                    _weight_quantizer,
                    is_output_quantized=True,
                    is_decode=is_decode,
                    smooth_factor=smooth_factor,
                )

                merged_bias = (
                    merged_bias.to(torch.int32)
                    if _input_quantizer.quant_desc.dtype in ['int4', 'int8']
                    else merged_bias.to(torch.float32)
                )

                if self.org_target.weight.device.type != 'meta':
                    # self.org_target 의 parameter update
                    # weight -> quantized weight 으로 변경 >> 이때 dtype이 제대로 들어간다면, runtime 시 input dtype 이 잘못 들어오면 error 발생함
                    self.org_target.register_parameter(
                        'weight', nn.Parameter(quantized_weight, requires_grad=False)
                    )

                # merged_bias load
                self.qlv3_bias.register_buffer('bias', merged_bias, persistent=False)
                self.qlv3_bias.register_parameter(
                    'imbias', nn.Parameter(imbias, requires_grad=False)
                )

                # output_quantizer 제대로 생성
                self.output_quantizer[0].merged_scale = merged_scale
                self.output_quantizer[0].zero_point = torch.tensor(
                    [0.0], dtype=merged_scale.dtype, device=merged_scale.device
                )

                self.output_quantizer[0]._dequantize = False

            else:
                input_qparams = get_qparams(_input_quantizer, if_bcq=False, device=_device)
                weight_qparams = get_qparams(_weight_quantizer, if_bcq=False, device=_device)
                output_qparams = get_qparams(
                    _output_quantizer, if_bcq=False, device=_device
                )  # 항상 1.0, 0.0

                smooth_factor = 1.0
                if (
                    hasattr(_input_quantizer, '_scale_per_channel')
                    and _input_quantizer._scale_per_channel != None
                ):
                    smooth_factor = _input_quantizer._scale_per_channel
                merged_scale, merged_bias, quantized_weight, imbias = get_precompute_qparams(
                    self.org_target,
                    input_qparams,
                    weight_qparams,
                    output_qparams,
                    _input_quantizer,
                    _weight_quantizer,
                    is_output_quantized=False,
                    is_decode=is_decode,
                    smooth_factor=smooth_factor,
                )

                merged_bias = (
                    merged_bias.to(torch.int32)
                    if _input_quantizer.quant_desc.dtype in ['int4', 'int8']
                    else merged_bias.to(torch.float32)
                )
                if self.org_target.weight.device.type != 'meta':
                    # self.org_target 의 parameter update
                    # weight -> quantized weight 으로 변경 >> 이때 dtype이 제대로 들어간다면, runtime 시 input dtype 이 잘못 들어오면 error 발생함
                    self.org_target.register_parameter(
                        'weight', nn.Parameter(quantized_weight, requires_grad=False)
                    )

                # merged_bias load
                self.qlv3_bias.register_buffer('bias', merged_bias, persistent=False)
                self.qlv3_bias.register_parameter(
                    'imbias', nn.Parameter(imbias, requires_grad=False)
                )

                # output_quantizer 제대로 생성
                if self.output_quantizer[0].disabled:
                    self.output_quantizer[0].enable()
                self.output_quantizer[0].merged_scale = 1 / merged_scale
                self.output_quantizer[0].zero_point = output_qparams[1]

                # TODO: int32 -> bf16 or int32 -> fp32 을 위한 dequant 수행 필요!
                self.output_quantizer[0]._dequantize = True
                self.output_quantizer[0].dequant_output_dtype = self.output_quantizer[
                    0
                ].quant_desc.dtype

        elif _input_quantizer.quant_desc.num_bits == 16:
            if _weight_quantizer.quant_desc.num_bits == 4:
                # weight decoding (same with input dtype)
                input_qparams = get_qparams(_input_quantizer, if_bcq=False, device=_device)
                weight_qparams = get_qparams(_weight_quantizer, if_bcq=False, device=_device)
                output_qparams = get_qparams(_output_quantizer, if_bcq=False, device=_device)

                if _output_quantizer.quant_desc.num_bits == 8:
                    # # per-head 일 경우, channel 방향으로 펼치기 TODO : 잘 정리합시다.
                    if (
                        not input_qparams[0].shape == output_qparams[0].shape
                        and len(output_qparams[0].shape) != 0
                    ):
                        _len_channel = _output_quantizer.quant_desc.input_shape[-1]
                        _head_dim = int(_len_channel / output_qparams[0].shape[0])

                        scale = output_qparams[0].repeat_interleave(_head_dim, dim=0)
                        zero_point = output_qparams[1].repeat_interleave(_head_dim, dim=0)

                        output_qparams = (scale, zero_point)

                smooth_factor = 1.0
                if (
                    hasattr(_input_quantizer, '_scale_per_channel')
                    and _input_quantizer._scale_per_channel != None
                ):
                    smooth_factor = _input_quantizer._scale_per_channel
                _, merged_bias, quantized_weight, imbias = get_precompute_qparams(
                    self.org_target,
                    input_qparams,
                    weight_qparams,
                    output_qparams,
                    _input_quantizer,
                    _weight_quantizer,
                    is_output_quantized=False,
                    is_decode=is_decode,
                    smooth_factor=smooth_factor,
                )

                if self.org_target.weight.device.type != 'meta':
                    merged_bias = merged_bias.to(torch.float32)
                else:
                    merged_bias = merged_bias.to('meta')

                # self.org_target 의 parameter update
                # weight -> quantized weight 으로 변경 >> 이때 dtype이 제대로 들어간다면, runtime 시 input dtype 이 잘못 들어오면 error 발생함
                if not is_decode and quantized_weight.device.type != 'meta':
                    quantized_weight = quant_nn.pack_int4_to_int8(quantized_weight)

                if self.org_target.weight.device.type != 'meta':
                    self.org_target.register_parameter(
                        'weight', nn.Parameter(quantized_weight, requires_grad=False)
                    )

                # merged_bias load
                self.qlv3_bias.register_buffer('bias', merged_bias, persistent=False)
                self.qlv3_bias.register_parameter(
                    'imbias', nn.Parameter(imbias, requires_grad=False)
                )

                # output_quantizer 제대로 생성
                self.output_quantizer[0].merged_scale = output_qparams[0]
                self.output_quantizer[0].zero_point = torch.tensor(
                    [0.0], dtype=output_qparams[0].dtype, device=output_qparams[0].device
                )  # bias에 merge
                self.output_quantizer[0]._dequantize = False

                _weight_quantizer.enable_real_quant()
                _weight_quantizer._dequantize = True
                self.qlv3_linear._weight_dequantizer = _weight_quantizer
                self.qlv3_linear._weight_decoding = True

            elif _weight_quantizer.quant_desc.num_bits == 8:
                # weight decoding (same with input dtype)
                input_qparams = get_qparams(_input_quantizer, if_bcq=False, device=_device)
                weight_qparams = get_qparams(_weight_quantizer, if_bcq=False, device=_device)
                output_qparams = get_qparams(_output_quantizer, if_bcq=False, device=_device)

                if _output_quantizer.quant_desc.num_bits == 8:
                    # # per-head 일 경우, channel 방향으로 펼치기 TODO : 잘 정리합시다.
                    if (
                        not input_qparams[0].shape == output_qparams[0].shape
                        and len(output_qparams[0].shape) != 0
                    ):
                        _len_channel = _output_quantizer.quant_desc.input_shape[-1]
                        _head_dim = int(_len_channel / output_qparams[0].shape[0])

                        scale = output_qparams[0].repeat_interleave(_head_dim, dim=0)
                        zero_point = output_qparams[1].repeat_interleave(_head_dim, dim=0)

                        output_qparams = (scale, zero_point)

                _, merged_bias, quantized_weight, imbias = get_precompute_qparams(
                    self.org_target,
                    input_qparams,
                    weight_qparams,
                    output_qparams,
                    _input_quantizer,
                    _weight_quantizer,
                    is_output_quantized=False,
                    is_decode=is_decode,
                )

                merged_bias = merged_bias.to(torch.float32)
                if self.org_target.weight.device.type != 'meta':
                    # self.org_target 의 parameter update
                    # weight -> quantized weight 으로 변경 >> 이때 dtype이 제대로 들어간다면, runtime 시 input dtype 이 잘못 들어오면 error 발생함
                    self.org_target.register_parameter(
                        'weight', nn.Parameter(quantized_weight, requires_grad=False)
                    )

                # bias load
                if self.org_target.bias is not None and _output_quantizer.quant_desc.num_bits < 16:
                    self.qlv3_bias.register_buffer('bias', merged_bias, persistent=False)
                    self.qlv3_bias.register_parameter(
                        'imbias', nn.Parameter(imbias, requires_grad=False)
                    )

                # output_quantizer 제대로 생성
                self.output_quantizer[0].merged_scale = output_qparams[0]
                self.output_quantizer[0].zero_point = torch.tensor(
                    [0.0], dtype=output_qparams[0].dtype, device=output_qparams[0].device
                )
                self.output_quantizer[0]._dequantize = False

                _weight_quantizer.enable_real_quant()
                _weight_quantizer._dequantize = True
                self.qlv3_linear._weight_dequantizer = _weight_quantizer
                self.qlv3_linear._weight_decoding = True

            elif _weight_quantizer.quant_desc.num_bits == 16:
                _weight_quantizer.enable_real_quant()
                _weight_quantizer._dequantize = False

                quantized_weight = _weight_quantizer(self.org_target.weight.data)

                if self.org_target.weight.device.type != 'meta':
                    self.org_target.register_parameter(
                        'weight', nn.Parameter(quantized_weight, requires_grad=False)
                    )

                # bias load
                if self.org_target.bias is not None:
                    self.qlv3_bias.register_buffer(
                        'bias', self.org_target.bias.clone(), persistent=False
                    )
                    self.qlv3_bias.register_parameter(
                        'imbias', nn.Parameter(self.org_target.bias.clone(), requires_grad=False)
                    )

            else:
                raise ValueError("FP32 linear couldn't be calculated with our HW!")

        else:
            # pass
            raise ValueError("FP32 linear couldn't be calculated with our HW!")

        # 모두 공통 output은 항상 real quant (즉 Tensor quantizer 에 정해진 dtype으로 변환해줘야함)
        self.output_quantizer[0].enable_real_quant()

        # 마지막에 해줘야 함
        if not self.input_quantizer[0].rollback:
            self.input_quantizer[0].reset()
            self.input_quantizer[0] = nn.Identity()

        else:
            if self.input_quantizer[0].quant_desc.dtype == 'fp32':
                raise ValueError("fp32 should not be rollback")
            else:
                # real quant 로 변환
                self.input_quantizer[0].enable_real_quant()
                self.input_quantizer[0]._dequantize = False

        self.qlv3_input_pre_quantizer = self.input_quantizer[0]
        self.qlv3_output_quantizer = self.output_quantizer[0]

        del self.input_quantizer
        del self.output_quantizer

    # TODO : 현 qlv4 module 생성을 위한 attribute 임시 구현
    @property
    def _additional_attr(self):
        return {'weight_real_dtype': self.weight_quantizer.quant_desc.dtype}
