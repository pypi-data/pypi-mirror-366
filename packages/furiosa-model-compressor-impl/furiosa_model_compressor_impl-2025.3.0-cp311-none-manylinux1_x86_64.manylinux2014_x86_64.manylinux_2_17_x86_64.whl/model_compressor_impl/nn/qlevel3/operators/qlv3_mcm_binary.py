import copy
import operator

import torch
from torch import Tensor, nn

from .... import nn as quant_nn
from .... import quant_op

# from ..modeling.qlv3_activation_modeling import *
from ..modeling.qlv3_mcm_binary_modeling import QLV3_ModelCompressorModuleBinary_MOD
from ..precompute import get_matamul_precompute_qparams, get_qparams
from .qlv3_mcm_base import QLV3_ModelCompressorModule

__all__ = [
    "QLV3_ModelCompressorModuleBinary",
]


class QLV3_ModelCompressorModuleBinary(QLV3_ModelCompressorModule):
    def __init__(self, qlv2_mcm):
        super().__init__(qlv2_mcm)

        # mcm compatability check
        if not isinstance(qlv2_mcm, quant_nn.ModelCompressorModuleBinary):
            raise ValueError("Qlevel2 mcm module missmatch with Qlevel3 mcm!")

        # load qlv2 quantizers to qlv3 module
        self.set_input_quantizer(qlv2_mcm)
        self._qlv3_mod = QLV3_ModelCompressorModuleBinary_MOD(self.org_target)

        self.qlv3_input_0_fetch = nn.Identity()
        self.qlv3_input_1_fetch = nn.Identity()

        self.qlv3_input_0_pre_quantizer = None
        self.qlv3_input_1_pre_quantizer = None
        self.qlv3_output_quantizer = None

    def qlv3_forward(self, *args, **kwargs):
        # binary op 이기 때문에 첫번째 index 가 tensor
        input_0 = args[0]
        input_1 = args[1]

        if not isinstance(self.qlv3_input_0_fetch, nn.Identity):
            input_0 = self.qlv3_input_0_fetch(input_0)
        if not isinstance(self.qlv3_input_1_fetch, nn.Identity):
            input_1 = self.qlv3_input_1_fetch(input_1)

        x = self.forward(input_0, input_1, *args[2:], **kwargs)
        x = self.qlv3_output_quantizer(x)

        return x

    def forward(self, *args, **kwargs) -> Tensor:
        output = self._qlv3_mod(*args, **kwargs)

        return output

    def golden_mode(self):
        self._qlv3_mod.golden_mode()

    def set_emulation_dtype(self, emul_dtype):
        self._qlv3_mod.set_emulation_dtype(emul_dtype)

    def set_input_quantizer(self, qlv2_mcm):
        self.input_quantizer.append(qlv2_mcm._input_0_quantizer)
        self.input_quantizer.append(qlv2_mcm._input_1_quantizer)

        return

    def del_pre_quantizer(self):
        del self.qlv3_input_0_pre_quantizer
        del self.qlv3_input_1_pre_quantizer

    @property
    def sub_modules(self):
        return {
            'pre': [self.qlv3_input_0_pre_quantizer, self.qlv3_input_1_pre_quantizer],
            'mod': self._qlv3_mod,
            'output': self.qlv3_output_quantizer,
        }

    def merge_quantizer(self, is_decode=False):
        if self.org_target_type in [torch.matmul, operator.matmul]:
            self.set_emulation_dtype(torch.float64)

            def _matmul_dtype_checker(input_quantizer):
                """
                matmul의 가능한 input dtype 별 종류를 나눔
                """
                dtype1 = input_quantizer[0].quant_desc.dtype
                dtype2 = input_quantizer[1].quant_desc.dtype
                # 두 dtype이 같거나, 둘 중 하나가 'bf16'인 경우 True 반환
                if 'fp32' in [dtype1, dtype2]:
                    raise ValueError("fp32 matmul X")

                if dtype1 == dtype2:
                    return dtype1, None
                else:
                    if 'bf16' in [dtype1, dtype2]:
                        bf16_idx = [dtype1, dtype2].index('bf16')

                        return 'bf16', 1 - bf16_idx

                    else:
                        raise ValueError("잘못된 matmul input")

            matmul_dtype, dq_idx = _matmul_dtype_checker(self.input_quantizer)

            if matmul_dtype == 'bf16':
                self.input_0_dtype = 'bf16'
                self.input_1_dtype = 'bf16'
                # TODO : 한쪽만 decoding 이 라는 가정하에 구현되어 있음
                if dq_idx is not None:
                    # input_quantizer[idx] 를 dequantization 시켜야함
                    _iquantizer = self.input_quantizer[dq_idx]
                    _decoding_dequantizer = copy.deepcopy(self.input_quantizer[dq_idx])
                    if not _iquantizer.rollback:
                        _iquantizer.reset()
                        _iquantizer = nn.Identity()
                    else:
                        if _iquantizer.quant_desc.dtype == 'fp32':
                            raise ValueError("fp32 should not be rollback")
                        else:
                            _iquantizer.enable_real_quant()
                            _iquantizer._dequantize = False

                    # TODO : is_shape_changed_by_propagate 일 경우. (코드 정리 필요)
                    if (
                        _decoding_dequantizer.is_shape_changed_by_propagate
                        and not _decoding_dequantizer.rollback
                    ):
                        if _decoding_dequantizer.quant_desc.org_axis is not None:
                            # TODO : GQA 처리 hard coding
                            _num_groups = int(
                                _decoding_dequantizer.quant_desc.org_shape[1]
                                * _decoding_dequantizer.quant_desc.org_shape[3]
                                / _decoding_dequantizer.quant_desc.input_shape[-1]
                            )
                            if _num_groups > 1:
                                if _decoding_dequantizer.amax is None:
                                    _decoding_dequantizer._max = (
                                        _decoding_dequantizer.max.repeat_interleave(_num_groups)
                                    )
                                    _decoding_dequantizer._min = (
                                        _decoding_dequantizer.min.repeat_interleave(_num_groups)
                                    )
                                else:
                                    _decoding_dequantizer._amax = (
                                        _decoding_dequantizer.amax.repeat_interleave(_num_groups)
                                    )

                        _decoding_dequantizer.quant_desc.axis = (
                            _decoding_dequantizer.quant_desc.org_axis
                        )
                        _decoding_dequantizer.quant_desc.input_shape = (
                            _decoding_dequantizer.quant_desc.org_shape
                        )

                    _decoding_dequantizer.enable_real_quant()
                    _decoding_dequantizer._dequantize = True
                    _decoding_dequantizer.dequant_output_dtype = 'bf16'
                    # dequantizer 는 decoding 에만 사용됨

                    self.input_quantizer[dq_idx] = nn.Sequential(
                        _iquantizer, _decoding_dequantizer
                    )  # TODO: decoding 일 경우 rollback 이 있으면 Q DQ 모두 필요

                    # TODO : 해당 분기가 아닐때
                    _bf16_quantizer = self.input_quantizer[1 - dq_idx]
                    if not _bf16_quantizer.rollback:
                        _bf16_quantizer.reset()
                        self.input_quantizer[1 - dq_idx] = nn.Identity()
                    else:
                        if _bf16_quantizer.quant_desc.dtype == 'fp32':
                            raise ValueError("fp32 should not be rollback")
                        else:
                            _bf16_quantizer.enable_real_quant()
                            _bf16_quantizer._dequantize = False

                else:
                    for i, _iquantizer in enumerate(self.input_quantizer):
                        if not _iquantizer.rollback:
                            _iquantizer.reset()
                            self.input_quantizer[i] = nn.Identity()
                        else:
                            if _iquantizer.quant_desc.dtype == 'fp32':
                                raise ValueError("fp32 should not be rollback")
                            else:
                                _iquantizer.enable_real_quant()
                                _iquantizer._dequantize = False

            elif matmul_dtype in ['int8', 'fp8-E4M3']:
                _input_0_quantizer = self.input_quantizer[0]
                _input_1_quantizer = self.input_quantizer[1]
                _output_quantizer = self.output_quantizer[0]

                self.input_0_dtype = self.input_quantizer[0].quant_desc.dtype
                self.input_1_dtype = self.input_quantizer[1].quant_desc.dtype

                if _output_quantizer.quant_desc.num_bits == 8:
                    input_0_qparams = get_qparams(_input_0_quantizer, if_bcq=False)
                    input_1_qparams = get_qparams(_input_1_quantizer, if_bcq=False)
                    output_qparams = get_qparams(_output_quantizer, if_bcq=False)
                    _device = input_0_qparams[0].device

                    # TODO : GQA 처리 hard coding
                    if (
                        self.input_quantizer[0].is_shape_changed_by_propagate
                        and not self.input_quantizer[0].rollback
                        and self.input_quantizer[0].quant_desc.axis is not None
                    ):
                        input_0_qparams = list(input_0_qparams)
                        _num_groups = int(
                            self.input_quantizer[0].quant_desc.org_shape[1]
                            / self.input_quantizer[0].quant_desc.input_shape[1]
                        )
                        if _num_groups > 1:
                            input_0_qparams[0] = input_0_qparams[0].repeat_interleave(_num_groups)
                            input_0_qparams[1] = input_0_qparams[1].repeat_interleave(_num_groups)
                    if (
                        self.input_quantizer[1].is_shape_changed_by_propagate
                        and not self.input_quantizer[1].rollback
                        and self.input_quantizer[1].quant_desc.axis is not None
                    ):
                        input_1_qparams = list(input_1_qparams)
                        _num_groups = int(
                            self.input_quantizer[1].quant_desc.org_shape[1]
                            / self.input_quantizer[1].quant_desc.input_shape[1]
                        )
                        if _num_groups > 1:
                            input_1_qparams[0] = input_1_qparams[0].repeat_interleave(_num_groups)
                            input_1_qparams[1] = input_1_qparams[1].repeat_interleave(_num_groups)

                    # TODO : 정말 quantizer 도 넘겨받아야하는가? 그러면... qparam은 왜 따로 받아야 하는가?
                    smooth_factor = 1.0
                    if hasattr(_output_quantizer, '_scale_per_channel'):
                        smooth_factor = _output_quantizer._scale_per_channel
                    merged_scale = get_matamul_precompute_qparams(
                        input_0_qparams[0],
                        input_1_qparams[0],
                        output_qparams[0],
                        single_op_case=False,
                        smooth_factor=smooth_factor,
                    )
                    merged_scale = merged_scale.to(torch.float32)

                    # fetch 동작 TODO : fetch 에서 수행됨을 표현하기 위해 별도의 real quantizer 정의 필요
                    if matmul_dtype != 'fp8-E4M3':
                        self.qlv3_input_0_fetch = quant_op.TensorQuantizer(
                            copy.deepcopy(self.input_quantizer[0].quant_desc)
                        )
                        if (
                            self.input_quantizer[0].is_shape_changed_by_propagate
                            and not self.input_quantizer[0].rollback
                        ):
                            self.qlv3_input_0_fetch.quant_desc.axis = (
                                self.qlv3_input_0_fetch.quant_desc.org_axis
                            )
                            self.qlv3_input_1_fetch.quant_desc.input_shape = (
                                self.qlv3_input_1_fetch.quant_desc.org_shape
                            )
                        self.qlv3_input_0_fetch.merged_scale = torch.tensor(1.0, device=_device)
                        self.qlv3_input_0_fetch.zero_point = input_0_qparams[1].to(torch.int8)
                        self.qlv3_input_0_fetch.enable_real_quant()
                        self.qlv3_input_0_fetch._dequantize = True

                        self.qlv3_input_1_fetch = quant_op.TensorQuantizer(
                            copy.deepcopy(self.input_quantizer[1].quant_desc)
                        )
                        if (
                            self.input_quantizer[1].is_shape_changed_by_propagate
                            and not self.input_quantizer[1].rollback
                        ):
                            self.qlv3_input_1_fetch.quant_desc.axis = (
                                self.qlv3_input_1_fetch.quant_desc.org_axis
                            )
                            self.qlv3_input_1_fetch.quant_desc.input_shape = (
                                self.qlv3_input_1_fetch.quant_desc.org_shape
                            )
                        self.qlv3_input_1_fetch.merged_scale = torch.tensor(1.0, device=_device)
                        self.qlv3_input_1_fetch.zero_point = input_1_qparams[1].to(torch.int8)
                        self.qlv3_input_1_fetch.enable_real_quant()
                        self.qlv3_input_1_fetch._dequantize = True

                    # output_quantizer 제대로 생성
                    self.output_quantizer[0].merged_scale = merged_scale
                    self.output_quantizer[0].zero_point = output_qparams[-1]
                    self.output_quantizer[0]._dequantize = False

                else:
                    input_0_qparams = get_qparams(_input_0_quantizer, if_bcq=False)
                    input_1_qparams = get_qparams(_input_1_quantizer, if_bcq=False)
                    output_qparams = get_qparams(_output_quantizer, if_bcq=False)  # 항상 1.0, 0.0
                    _device = input_0_qparams[0].device

                    # TODO : GQA 처리 hard coding
                    if (
                        self.input_quantizer[0].is_shape_changed_by_propagate
                        and not self.input_quantizer[0].rollback
                        and self.input_quantizer[0].quant_desc.axis is not None
                    ):
                        input_0_qparams = list(input_0_qparams)
                        _num_groups = int(
                            self.input_quantizer[0].quant_desc.org_shape[1]
                            / self.input_quantizer[0].quant_desc.input_shape[1]
                        )
                        if (
                            self.input_quantizer[0].quant_desc.input_shape[1] == 1
                            and _num_groups > 1
                        ):
                            # TODO : slice 모델로 calibration 하는 경우, q 의 input shape에 seq len 이 1로 _num_groups 값이 제대로 계산되지 않음, mcp ci 통과를 위해 임시 처리
                            _num_groups = 1
                        if _num_groups > 1:
                            input_0_qparams[0] = input_0_qparams[0].repeat_interleave(_num_groups)
                            input_0_qparams[1] = input_0_qparams[1].repeat_interleave(_num_groups)
                    if (
                        self.input_quantizer[1].is_shape_changed_by_propagate
                        and not self.input_quantizer[1].rollback
                        and self.input_quantizer[1].quant_desc.axis is not None
                    ):
                        input_1_qparams = list(input_1_qparams)
                        _num_groups = int(
                            self.input_quantizer[1].quant_desc.org_shape[1]
                            / self.input_quantizer[1].quant_desc.input_shape[1]
                        )
                        if _num_groups > 1:
                            input_1_qparams[0] = input_1_qparams[0].repeat_interleave(_num_groups)
                            input_1_qparams[1] = input_1_qparams[1].repeat_interleave(_num_groups)

                    merged_scale = get_matamul_precompute_qparams(
                        input_0_qparams[0],
                        input_1_qparams[0],
                        output_qparams[0],
                        single_op_case=False,
                    )
                    merged_scale = merged_scale.to(torch.float32)

                    if matmul_dtype != 'fp8-E4M3':
                        # fetch 동작
                        self.qlv3_input_0_fetch = quant_op.TensorQuantizer(
                            copy.deepcopy(self.input_quantizer[0].quant_desc)
                        )
                        if (
                            self.input_quantizer[0].is_shape_changed_by_propagate
                            and not self.input_quantizer[0].rollback
                        ):
                            self.qlv3_input_0_fetch.quant_desc.axis = (
                                self.qlv3_input_0_fetch.quant_desc.org_axis
                            )
                            self.qlv3_input_0_fetch.quant_desc.input_shape = (
                                self.qlv3_input_0_fetch.quant_desc.org_shape
                            )
                        self.qlv3_input_0_fetch.merged_scale = torch.tensor(1.0, device=_device)
                        self.qlv3_input_0_fetch.zero_point = input_0_qparams[1].to(torch.int8)
                        self.qlv3_input_0_fetch.enable_real_quant()
                        self.qlv3_input_0_fetch._dequantize = True

                        self.qlv3_input_1_fetch = quant_op.TensorQuantizer(
                            copy.deepcopy(self.input_quantizer[1].quant_desc)
                        )
                        if (
                            self.input_quantizer[1].is_shape_changed_by_propagate
                            and not self.input_quantizer[1].rollback
                        ):
                            self.qlv3_input_1_fetch.quant_desc.axis = (
                                self.qlv3_input_1_fetch.quant_desc.org_axis
                            )
                            self.qlv3_input_1_fetch.quant_desc.input_shape = (
                                self.qlv3_input_1_fetch.quant_desc.org_shape
                            )
                        self.qlv3_input_1_fetch.merged_scale = torch.tensor(1.0, device=_device)
                        self.qlv3_input_1_fetch.zero_point = input_1_qparams[1].to(torch.int8)
                        self.qlv3_input_1_fetch.enable_real_quant()
                        self.qlv3_input_1_fetch._dequantize = True

                    # output_quantizer 제대로 생성
                    if self.output_quantizer[0].disabled:
                        self.output_quantizer[0].enable()

                    # TODO: output 이 bf16 일 경우 dequant axis 를 명확히 정의 해야함
                    output_axis = (
                        _input_1_quantizer.quant_desc.axis
                        if not _input_1_quantizer.is_shape_changed_by_propagate
                        else _input_1_quantizer.quant_desc.org_axis
                    )
                    self.output_quantizer[0].quant_desc.axis = output_axis
                    self.output_quantizer[0].merged_scale = 1 / merged_scale.to(
                        _device
                    )  # TODO : int32 를 dequant 할때는 역수를 넣어줘야함... 일반화 할 수 있는 방법을 고민하자!
                    self.output_quantizer[0].zero_point = output_qparams[-1].to(
                        _device
                    )  # TODO: bf16 일 경우 qparam 에 device 정보가 가 전혀 없다...
                    self.output_quantizer[0]._dequantize = (
                        True  # TODO: int32 -> bf16 을 위한 dequant 수행 필요!
                    )
                    self.output_quantizer[0].dequant_output_dtype = self.output_quantizer[
                        0
                    ].quant_desc.dtype

                for i, _iquantizer in enumerate(self.input_quantizer):
                    if not _iquantizer.rollback:
                        _iquantizer.reset()
                        self.input_quantizer[i] = nn.Identity()
                    else:
                        if _iquantizer.quant_desc.dtype == 'fp32':
                            raise ValueError("fp32 should not be rollback")
                        else:
                            _iquantizer.enable_real_quant()
                            _iquantizer._dequantize = False

            else:
                raise ValueError("잘못된 matmul dtype")

            self.output_quantizer[0].enable_real_quant()

        else:
            # 항상 fp32 로 casting 필요!
            # modeling 내에서 fp32 또는 fp64 로 converting 을 명시!
            for i, _iquantizer in enumerate(self.input_quantizer):
                if _iquantizer.quant_desc.dtype not in ['bf16', 'fp32']:
                    raise ValueError(
                        "only ['bf16', 'fp32'] is implemented for binary mcm except for matmul"
                    )

            for i, _iquantizer in enumerate(self.input_quantizer):
                if not _iquantizer.rollback:
                    _iquantizer.reset()
                    self.input_quantizer[i] = nn.Identity()
                else:
                    if _iquantizer.quant_desc.dtype == 'fp32':
                        raise ValueError("fp32 should not be rollback")
                    else:
                        _iquantizer.enable_real_quant()
                        _iquantizer._dequantize = False

            self.output_quantizer[0].enable_real_quant()
            self.output_quantizer[0]._dequantize = False

        self.qlv3_input_0_pre_quantizer = self.input_quantizer[0]
        self.qlv3_input_1_pre_quantizer = self.input_quantizer[1]
        self.qlv3_output_quantizer = self.output_quantizer[0]

        del self.input_quantizer
        del self.output_quantizer
