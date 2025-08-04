import gc
import logging
from typing import Callable

import torch
import torch.nn
import torch.nn.functional as F

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from ...quant_op.autoscaler.awq_processor import AWQ_Processor
from ...quant_op.autoscaler.gptq_processor import GPTQ_Processor
from ...quant_op.autoscaler.smq_processor import SMQ_Processor
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleLinear"]

logger = logging.getLogger('mcm_linear')


class ModelCompressorModuleLinear(ModelCompressorModule, _utils.QuantMixin):
    default_quant_desc_weight = descriptor.QUANT_DESC_DISABLE
    default_quant_desc_input = descriptor.QUANT_DESC_DISABLE

    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        **kwargs,
    ):
        super(ModelCompressorModuleLinear, self).__init__(org_target, org_args, is_module)

        quant_desc_input, quant_desc_weight = _utils.pop_quant_desc_in_kwargs(
            self.__class__, **kwargs
        )

        self.activation_per_channel = False
        if quant_desc_input.axis is not None:
            # activation per-channel
            self.activation_per_channel = True
            quant_desc_input.axis = -1

        # TODO: module type 은 기존과 호환되지 않을 수 있음
        self.init_quantizer(
            quant_desc_input, quant_desc_weight, module_type=self.__class__.__name__
        )

        # self.org_module = org_target
        # _org_parameters = kwargs.pop("_parameters")
        # self.weight = _org_parameters["weight"]
        # self.bias = _org_parameters["bias"]

        # self.out_features = self.org_target.out_features
        self.each_out_features = kwargs.pop("each_out_features", [self.org_target.out_features])
        self.module2inspect = kwargs.pop("module2inspect", None)
        self.modulekwargs = kwargs.pop("layer_kwargs", {})
        self.node_name = kwargs.pop("node_name", None)
        self.output_shape = kwargs.pop("output_shape", None)
        self.each_node_name = kwargs.pop("each_node_name", None)
        self.layers2inspect = kwargs.pop("layers2inspect", None)

    def load_qformat_to_tq(self, tq, quant_desc):
        tq.change_quant_desc(quant_desc)

    def load_quant_descriptor(self, **quant_desc):
        _re_init_tq = quant_desc.pop('re_init_tq', True)
        quant_desc_input, quant_desc_weight = _utils.pop_quant_desc_in_kwargs(
            self.__class__, **quant_desc
        )
        self.activation_per_channel = False
        if quant_desc_input.axis is not None:
            # activation per-channel
            self.activation_per_channel = True
            quant_desc_input.axis = -1

        # re-initialize input quantizer
        if _re_init_tq:
            self._input_quantizer = TensorQuantizer(quant_desc_input)
            self._weight_quantizer = TensorQuantizer(quant_desc_weight)
        else:
            self.load_qformat_to_tq(self._input_quantizer, quant_desc_input)
            self.load_qformat_to_tq(self._weight_quantizer, quant_desc_weight)

    def reset(self):
        self.module2inspect = None
        self.modulekwargs = {}
        self._input_quantizer = None
        self._weight_quantizer = None

    # TODO : 해당 method는 이 class 에 종속된 method일 필요 없음 utils 로 분리 가능
    def _get_top_percentile_mask_along(self, tensor, percentile):
        if percentile == 0:
            return torch.zeros_like(tensor, dtype=torch.bool)
        if percentile == 100:
            return torch.ones_like(tensor, dtype=torch.bool)

        to_ratio = percentile / 100
        mask = torch.zeros_like(tensor, dtype=torch.bool)
        top_percent = int(tensor.numel() * to_ratio)
        if top_percent == 0:
            return torch.zeros_like(tensor, dtype=torch.bool)

        sorted_tensor, _ = tensor.flatten().sort()
        threshold_value = sorted_tensor[-top_percent]
        mask[tensor >= threshold_value] = True
        return mask

    def _search_outlier_ch(self, input, deviation_ratio=-1):
        # ----------------------------------------------------------------------------
        # 1. _calibrator_type == 'max'
        #    outlier 선정 기준 (LLM.int8() 참조)
        #    MAX값 기준 0.6 배 이상인 값을 포함하고 있는 채널을 모두 OUTLIER LAYER로 정의
        # ----------------------------------------------------------------------------

        if self._input_quantizer._if_calib:
            # TODO : do not need to return
            quant_input = self._input_quantizer(input)
            return

        if hasattr(self._weight_quantizer, "outlier_cin_idx"):
            return self.outlier_cin_idx

        _calibrator_type = self._input_quantizer.calibrator_type
        _asymmetric = self._input_quantizer.quant_desc.asymmetric
        _outlier_percentile = self._input_quantizer._outlier_percentile

        if _asymmetric:
            amaxs_along_cin_axis = self._input_quantizer.max
            raise NotImplementedError(
                f"Invalid calibrator_type {_calibrator_type} for searching outlier ch."
            )
        else:
            amaxs_along_cin_axis = self._input_quantizer.amax
            amax_along_cin_axis = amaxs_along_cin_axis.max()
            if _outlier_percentile >= 0:
                is_outlier_ch = self._get_top_percentile_mask_along(
                    amaxs_along_cin_axis, percentile=_outlier_percentile
                )
            else:
                threshold = deviation_ratio * amax_along_cin_axis
                is_outlier_ch = amaxs_along_cin_axis >= threshold

            outlier_cin_idx = torch.where(is_outlier_ch)

        self.outlier_cin_idx = outlier_cin_idx[0]
        self._weight_quantizer.outlier_cin_idx = self.outlier_cin_idx.cpu()
        self.outlier_ratio = (self.outlier_cin_idx.shape[0] / input.shape[-1]) * 100

        return

    def forward(self, input):
        if hasattr(self.org_target, '_skip_during_calibration'):
            # Linear module들을 integration 후, org moduel에 대해서는 weight/bias=None인 상태로 F.linear 계산이 불가하여 아래처럼 pass.
            return input

        if hasattr(self.org_target, '_hf_hook'):
            args, _ = self.org_target._hf_hook.pre_forward(self.org_target, input)
            input = args[0]

        if self._input_quantizer._if_outlier_searching:
            self._search_outlier_ch(input)
            return F.linear(input, self.org_target.weight, bias=self.org_target.bias)

        if self._weight_quantizer.if_auto_get_scale:
            self._do_autoscale(input)
            return F.linear(input, self.org_target.weight, bias=self.org_target.bias)

        if self._weight_quantizer.if_auto_get_clipping_bound:
            self._serach_clipping_range(input, self.org_target.weight)
            return F.linear(input, self.org_target.weight, bias=self.org_target.bias)

        if self._weight_quantizer.quant_desc.if_per_channel_scaling:
            quant_input, quant_weight = self._per_channel_scaling(input)
        elif self._input_quantizer.quant_desc.per_ch:
            quant_input, quant_weight = self._activation_per_channel_quant(input)
        else:
            quant_input = self._input_quantizer(input)
            quant_weight = self._weight_quantizer(self.org_target.weight)

        output = F.linear(quant_input, quant_weight, bias=self.org_target.bias)

        if hasattr(self.org_target, '_hf_hook'):
            output = self.org_target._hf_hook.post_forward(self.org_target, output)
        return output

    def _activation_per_channel_quant(self, input):
        quant_input = self._input_quantizer(input)

        # during calibration
        if self._input_quantizer._if_calib:
            return (input, self.org_target.weight)

        if self._input_quantizer.calibrator_type == 'max':
            max = self._input_quantizer.get_amax(input)
            activation_scale = max / 128
        else:
            max, min = self._input_quantizer.get_minmax(input)
            activation_scale = (max - min) / 255

        activation_scale = torch.where(activation_scale > 0.00001, activation_scale, 0.00001)
        # activation_scale = torch.where(activation_scale.abs() > 0.001, activation_scale, 0.001)

        device = quant_input.device
        activation_scale = activation_scale.to(device=device)
        quant_input = quant_input / activation_scale

        redefined_weight = self.org_target.weight * activation_scale

        while redefined_weight.dim() > 2:
            redefined_weight = redefined_weight.squeeze(0)

        if not redefined_weight.dim() == 2:
            raise ValueError("Shape of redefined_weight should be 2D!")

        quant_weight = self._weight_quantizer(redefined_weight)

        return (quant_input, quant_weight)

    @torch.no_grad()
    def _do_autoscale(self, x, n_grid=20):  # do_advanced_ptq
        if self._input_quantizer._if_calib or self._input_quantizer.disabled:
            return

        best_scales = None
        output = self._weight_quantizer.auto_scale_method.do_autoscale(
            self._input_quantizer,
            self._weight_quantizer,
            self.org_target,
            best_scales,
            x=x,
            module2inspect=self.module2inspect,
            layers2inspect=self.layers2inspect,
            each_out_features=self.each_out_features,
            each_node_name=self.each_node_name,
            node_name=self.node_name,
            modulekwargs=self.modulekwargs,
            n_grid=n_grid,
            outlier_ratio=hasattr(self, 'outlier_ratio'),
        )
        if output is None:
            return
        else:
            best_scales = output

        # postprocessing for OSQ  / 뒤에 더 깔끔하게 정리하면 좋을것 같음.
        if hasattr(self, 'outlier_pair'):
            _outlier_cin_idx = self.outlier_cin_idx.tolist()
            best_scales[_outlier_cin_idx] = 0

        self._input_quantizer.scale_per_channel = best_scales
        if hasattr(self, 'majority_pair'):
            self.majority_pair._input_quantizer.scale_per_channel_outlier = best_scales

        if self.module2inspect is not None:
            modulekwargs = dict(
                [
                    (key, value.cpu()) if torch.is_tensor(value) else (key, value)
                    for key, value in self.modulekwargs.items()
                ]
            )

        self.module2inspect = None
        self.modulekwargs = {}

        gc.collect()
        torch.cuda.empty_cache()

        return

    def _per_channel_scaling(self, input):
        def _generate_mask(outlier_ch_idx, org_weight_shape):
            num_cin = org_weight_shape[-1]
            mask_1d = [1] * num_cin
            for idx in outlier_ch_idx:
                mask_1d[idx] = 0
            mask_1d = torch.tensor(mask_1d)
            weight_mask = mask_1d.expand(org_weight_shape)
            return weight_mask

        if self._weight_quantizer.quant_desc.dtype in ['int8', 'int4']:
            device = input.device
            scale_per_channel = self._input_quantizer.scale_per_channel.to(device)
            scale_per_channel = torch.where(scale_per_channel > 0.00001, scale_per_channel, 0.00001)

            # AMAX일 경우에는 별도 처리 필요 없음.
            # weight의 경우, MINMAX이더라도 일반적으로 0 기준 대칭 분포를 가질 것이므로, masking 처리만 해주어도 문제가 발생하지 않을 것으로 보임.

            _input = input / scale_per_channel
            if self._input_quantizer._if_calib:
                if hasattr(self, 'outlier_pair'):
                    _outlier_cin_idx = self.outlier_cin_idx.tolist()
                    _mask = _generate_mask(_outlier_cin_idx, _input.shape)
                    _input_min = torch.min(_input)
                    _input = _input * _mask.to(_input.device)

                    if _input_min > 0:
                        _flipped_mask = abs(_mask - 1)
                        _offset_mask = _flipped_mask * _input_min
                        _input = _input + _offset_mask

            quant_input = self._input_quantizer(_input)
            quant_weight = self._weight_quantizer(self.org_target.weight * scale_per_channel)
        else:
            if not hasattr(self, "majority_pair"):
                raise ValueError(
                    "BF16 per chennal scaling is only supported when args.outlier_percentile > 0"
                )
            quant_input = self._input_quantizer(input)
            quant_weight = self._weight_quantizer(self.org_target.weight)

        while quant_weight.dim() > 2:
            quant_weight = quant_weight.squeeze(0)

        if not quant_weight.dim() == 2:
            raise ValueError("Shape of redefined_weight should be 2D!")

        if self._weight_quantizer._if_calib or self._input_quantizer._if_calib:
            return (input, self.org_target.weight)

        return (quant_input, quant_weight)

    @torch.no_grad()
    def _serach_clipping_range(self, x, weight, n_grid=20, max_shrink=0.5, n_sample_token=512):
        # w           [co, ci]      -> [co, 1, n_group, group size]
        # input_feat  [n_token, ci] -> [1, n_token, n_group, group size]

        device = self.org_target.weight.device

        if hasattr(self._input_quantizer, "_scale_per_channel"):
            scale_per_channel = self._input_quantizer.scale_per_channel.to(device)
            x = x / scale_per_channel
            weight = weight * scale_per_channel

        group_size = self._weight_quantizer.quant_desc.group_size
        group_size = group_size if group_size is not None else weight.shape[1]

        x = x.view(-1, x.shape[-1])
        x = x.reshape(1, x.shape[0], -1, group_size)

        if x.shape[1] % n_sample_token == 0:
            # Only for LLM model
            x = x[:, 0 :: x.shape[1] // n_sample_token]
        weight = weight.reshape(weight.shape[0], 1, -1, group_size)

        oc_batch_size = 256 if weight.shape[0] % 256 == 0 else 64  # prevent OOM
        if weight.shape[0] % oc_batch_size != 0:
            logger.warning(
                f"Cout dim {weight.shape[0]} is not divisible by oc_batch_size {oc_batch_size}. Clipping range would be searched for whole Cout dim at once. It mignt cause OOM."
            )
            oc_batch_size = weight.shape[0]
        w_all = weight
        best_max_val_all = []

        for i_b in range(weight.shape[0] // oc_batch_size):
            weight = w_all[i_b * oc_batch_size : (i_b + 1) * oc_batch_size]

            org_max_val = weight.abs().amax(dim=-1, keepdim=True)  # co, 1, n_group, 1

            best_max_val = org_max_val.clone()
            min_errs = torch.ones_like(org_max_val) * 1e9
            x = x.to(weight.device)
            org_out = (x * weight).sum(dim=-1)  # co, n_token, n_group

            for i_s in range(int(max_shrink * n_grid)):
                max_val = org_max_val * (1 - i_s / n_grid)
                min_val = -max_val
                cur_w = torch.clamp(weight, min_val, max_val)
                org_cur_w_shape = cur_w.shape

                if self._weight_quantizer.calibrator_type == 'max':
                    w_to_check = cur_w.abs()
                else:
                    w_to_check = cur_w

                _max = w_to_check.amax(dim=-1, keepdim=True)
                _min = w_to_check.amin(dim=-1, keepdim=True)

                _max = _max.reshape(-1, 1)
                _min = _min.reshape(-1, 1)

                # calibrator type
                if self._weight_quantizer.calibrator_type == 'max':
                    if not hasattr(self._weight_quantizer, "_amax"):
                        self._weight_quantizer.register_buffer("_amax", _max.data)
                    else:
                        self._weight_quantizer._amax = _max

                elif self._weight_quantizer.calibrator_type == 'minmax':
                    if not hasattr(self._weight_quantizer, "_max"):
                        self._weight_quantizer.register_buffer("_max", _max.data)
                        self._weight_quantizer.register_buffer("_min", _min.data)
                    else:
                        self._weight_quantizer._max = _max
                        self._weight_quantizer._min = _min

                q_w = self._weight_quantizer(cur_w.reshape(cur_w.shape[0], -1))
                q_w = q_w.reshape(org_cur_w_shape)
                cur_out = (x * q_w).sum(dim=-1)

                # co, 1, n_group, 1
                err = (cur_out - org_out).pow(2).mean(dim=1).view(min_errs.shape)
                del cur_w
                del cur_out
                cur_best_idx = err < min_errs
                min_errs[cur_best_idx] = err[cur_best_idx]

                best_max_val[cur_best_idx] = max_val[cur_best_idx]

            best_max_val_all.append(best_max_val)

        best_max_val = torch.cat(best_max_val_all, dim=0)

        del x
        del org_out

        gc.collect()
        torch.cuda.empty_cache()

        weight = torch.clamp(w_all, -best_max_val, best_max_val)
        if self._weight_quantizer.calibrator_type == 'max':
            weight = weight.abs()

        _max = weight.amax(dim=-1, keepdim=True)
        _min = weight.amin(dim=-1, keepdim=True)

        _max = _max.reshape(-1, 1)
        _min = _min.reshape(-1, 1)

        if self._weight_quantizer.calibrator_type == 'max':
            self._weight_quantizer._amax = _max
        else:
            self._weight_quantizer._max = _max
            self._weight_quantizer._min = _min
        self._weight_quantizer.clipping_bound = best_max_val.reshape(-1, 1).squeeze(1)
        return
