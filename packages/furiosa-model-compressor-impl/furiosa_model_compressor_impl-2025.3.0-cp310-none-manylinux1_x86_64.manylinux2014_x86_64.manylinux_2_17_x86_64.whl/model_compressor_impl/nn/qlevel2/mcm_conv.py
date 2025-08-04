from typing import Callable

import torch
import torch.nn
import torch.nn.functional as F
from torch.nn.modules.utils import _pair

from . import _utils
from ... import descriptor
from ...quant_op import TensorQuantizer
from .mcm_base import ModelCompressorModule

__all__ = ["ModelCompressorModuleConv2d"]


class _ModelCompressorModuleConvNd(ModelCompressorModule, _utils.QuantMixin):
    def __init__(
        self,
        org_target: Callable,
        org_args: dict = None,
        is_module: bool = True,
        quant_desc_input=None,
        quant_desc_weight=None,
        **kwargs,
    ):
        super(_ModelCompressorModuleConvNd, self).__init__(org_target, org_args, is_module)

        self.activation_per_channel = False
        if quant_desc_input.axis is not None:
            # activation per-channel
            self.activation_per_channel = True
        self.init_quantizer(quant_desc_input, quant_desc_weight, self.__class__.__name__)

        # self.org_target = org_target

    def load_quant_descriptor(self, **quant_desc):
        # re-initialize input quantizer
        self._input_quantizer = TensorQuantizer(quant_desc['quant_desc_input'])
        self._weight_quantizer = TensorQuantizer(quant_desc['quant_desc_weight'])

    def _quant(self, input):
        """Apply quantization on input and weight

        Function called by the classes lower in the hierarchy, which actually performs the quantization before forward
        in the derivate class the particular Function.

        Arguments:
            input: in_features to quantize
        Returns:
            A tuple: (quant_in_feature, quant_weight)
        """
        quant_input = self._input_quantizer(input)
        quant_weight = self._weight_quantizer(self.org_target.weight)

        return (quant_input, quant_weight)

    def _activation_per_channel_quant(self, input):
        quant_input = self._input_quantizer(input)

        # during activation calibration
        if self._input_quantizer._if_calib:
            return (input, self.org_target.weight)

        max, min = self._input_quantizer.get_minmax(input)
        activation_scale = (max - min) / 255
        activation_scale = torch.where(activation_scale > 0.00001, activation_scale, 0.00001)

        quant_input = quant_input / activation_scale

        # depth wise conv 일때, output channel 방향으로 broad cast 해줌
        # TODO: group size 가 output_channel 과 같지 않은 경우에는.. 잘 처리해줘야함
        if self.org_target.groups == 1:
            pass
        elif self.org_target.groups == self.org_target.out_channels:
            activation_scale = activation_scale.transpose(0, 1)
        else:
            activation_scale = activation_scale.reshape(
                self.org_target.groups,
                int(self.org_target.in_channels / self.org_target.groups),
                1,
                1,
            )
            activation_scale = activation_scale.repeat(
                1,
                int(
                    (self.org_target.in_channels / self.org_target.groups)
                    * (self.org_target.out_channels / self.org_target.in_channels)
                ),
                1,
                1,
            )
            activation_scale = activation_scale.reshape(
                self.org_target.out_channels,
                int(self.org_target.in_channels / self.org_target.groups),
                1,
                1,
            )

        redefined_weight = self.org_target.weight * activation_scale
        quant_weight = self._weight_quantizer(redefined_weight)

        return (quant_input, quant_weight)

    def _search_per_channel_scale_parameter(self, weight):
        if self._input_quantizer._if_calib or self._input_quantizer.disabled:
            return

        auto_scale_method = self._weight_quantizer.auto_scale_method
        best_scales = None
        device = weight.device
        if auto_scale_method == 'SmoothQuant':
            raise NotImplementedError("SmoothQuant method is not supported for CNN yet")

            device, dtype = self.org_target.weight.device, self.org_target.weight.dtype
            alpha = self._weight_quantizer.smq_alpha

            if self._weight_quantizer.calibrator_type == 'max':
                weight_scales = self._weight_quantizer.amax / 128
            elif self._weight_quantizer.calibrator_type == 'minmax':
                weight_scales = (self._weight_quantizer.max - self._weight_quantizer.min) / 255
            else:
                raise NotImplementedError(
                    f"SmoothQuant method is not implemented for {self._weight_quantizer.calibrator_type}"
                )

            if self._input_quantizer.calibrator_type == 'max':
                act_scales = self._input_quantizer.amax / 128
            elif self._input_quantizer.calibrator_type == 'minmax':
                act_scales = (self._input_quantizer.max - self._input_quantizer.min) / 255
            else:
                raise NotImplementedError(
                    f"SmoothQuant method is not implemented for {self._input_quantizer.calibrator_type}"
                )

            # -----------REF----------
            # act_scales = self._input_quantizer.amax
            # weight_scales = self._weight_quantizer.amax

            # max = self._input_quantizer.max
            # min = self._input_quantizer.min
            # act_scales = (max - min) / 255

            # max = self._weight_quantizer.max
            # min = self._weight_quantizer.min
            # weight_scales = (max - min) / 255
            # ------------------------

            def reshape_weight_scales_to_act_scales(weight_scales, act_scales):
                num_act_scales = act_scales.shape[0] if len(act_scales.shape) != 0 else 1
                num_weight_scales = weight_scales.shape[0] if len(weight_scales.shape) != 0 else 1
                if num_act_scales == num_weight_scales:
                    return weight_scales

                weight_cout = self.org_target.out_channels
                weight_cin = self.org_target.in_channels
                if self.org_target.groups == self.org_target.out_channels:
                    weight_cout = int(self.org_target.out_channels / self.org_target.groups)

                weight_refined_cin = num_weight_scales / weight_cout
                if weight_refined_cin == int(weight_refined_cin):
                    group_size = int(weight_cin / weight_refined_cin)

                    weight_scales = weight_scales.view(-1, int(weight_refined_cin)).mean(
                        0, keepdim=True
                    )
                    weight_scales = torch.squeeze(weight_scales.repeat([group_size, 1]).view(-1))
                else:
                    num_to_repeat = int(num_act_scales / num_weight_scales)
                    weight_scales = weight_scales.repeat(num_to_repeat)

                return weight_scales

            weight_scales = reshape_weight_scales_to_act_scales(weight_scales, act_scales)
            act_scales = act_scales.to(device=device, dtype=dtype)
            scales = (
                (act_scales.pow(alpha) / weight_scales.pow(1 - alpha))
                .clamp(min=1e-5)
                .to(device)
                .to(dtype)
            )
            best_scales = scales
        else:
            raise NotImplementedError

        self._input_quantizer.scale_per_channel = best_scales.cpu()

        return

    def match_activation_scale_shape(self, activation_scale):
        # depth wise conv 일때, output channel 방향으로 broad cast 해줌
        # TODO: group size 가 output_channel 과 같지 않은 경우에는.. 잘 처리해줘야함
        if self.org_target.groups == 1:
            pass
        elif self.org_target.groups == self.org_target.out_channels:
            activation_scale = activation_scale.transpose(0, 1)
        else:
            activation_scale = activation_scale.reshape(
                self.org_target.groups, int(self.in_channels / self.org_target.groups), 1, 1
            )
            activation_scale = activation_scale.repeat(
                1,
                int(
                    (self.org_target.in_channels / self.org_target.groups)
                    * (self.org_target.out_channels / self.org_target.in_channels)
                ),
                1,
                1,
            )
            activation_scale = activation_scale.reshape(
                self.org_target.out_channels,
                int(self.org_target.in_channels / self.org_target.groups),
                1,
                1,
            )
        return activation_scale

    def broadcast_scale_per_channnel(self, x, scale, scale_axis):
        shape_to_broadcast = [1] * len(x.shape)
        shape_to_broadcast[scale_axis] = scale.shape[0]

        return scale.view(shape_to_broadcast)

    def _per_channel_scaling(self, input, in_ch_axis=1):
        device = input.device
        scale_per_channel = self._input_quantizer.scale_per_channel.to(device)
        activation_scale = self.broadcast_scale_per_channnel(input, scale_per_channel, in_ch_axis)
        activation_scale = torch.where(activation_scale > 0.00001, activation_scale, 0.00001)

        quant_input = self._input_quantizer(input / activation_scale)
        # depth wise conv 일때, output channel 방향으로 broad cast 해줌
        # TODO: group size 가 output_channel 과 같지 않은 경우에는.. 잘 처리해줘야함
        if self.org_target.groups == 1:
            pass
        elif self.org_target.groups == self.org_target.out_channels:
            activation_scale = activation_scale.transpose(0, 1)
        else:
            activation_scale = activation_scale.reshape(
                self.org_target.groups,
                int(self.org_target.in_channels / self.org_target.groups),
                1,
                1,
            )
            activation_scale = activation_scale.repeat(
                1,
                int(
                    (self.org_target.in_channels / self.org_target.groups)
                    * (self.org_target.out_channels / self.org_target.in_channels)
                ),
                1,
                1,
            )
            activation_scale = activation_scale.reshape(
                self.org_target.out_channels,
                int(self.org_target.in_channels / self.org_target.groups),
                1,
                1,
            )

        redefined_weight = self.org_target.weight * activation_scale

        quant_weight = self._weight_quantizer(redefined_weight)

        return (quant_input, quant_weight)

    def get_output(self, input, weight, bias=None, groups=None):
        if bias is None:
            bias = self.org_target.bias

        if groups is None:
            groups = self.org_target.groups

        if self.org_target.padding_mode == "circular":
            expanded_padding = (
                (self.org_target.padding[1] + 1) // 2,
                self.org_target.padding[1] // 2,
                (self.org_target.padding[0] + 1) // 2,
                self.org_target.padding[0] // 2,
            )
            output = F.conv2d(
                F.pad(input, expanded_padding, mode="circular"),
                weight,
                bias,
                self.stride,
                _pair(0),
                self.dilation,
                groups,
            )
        else:
            output = F.conv2d(
                input,
                weight,
                bias,
                self.org_target.stride,
                self.org_target.padding,
                self.org_target.dilation,
                groups,
            )
        return output


class ModelCompressorModuleConv2d(_ModelCompressorModuleConvNd):
    """Quantized 2D conv"""

    default_quant_desc_weight = descriptor.QUANT_DESC_DISABLE
    default_quant_desc_input = descriptor.QUANT_DESC_DISABLE

    def __init__(
        self, org_target: Callable, org_args: dict = None, is_module: bool = True, **kwargs
    ):
        # TODO : should take qformat for create quant_desc_input
        quant_desc_input, quant_desc_weight = _utils.pop_quant_desc_in_kwargs(
            self.__class__, **kwargs
        )

        super(ModelCompressorModuleConv2d, self).__init__(
            org_target, org_args, is_module, quant_desc_input, quant_desc_weight, **kwargs
        )

    def forward(self, input):
        if hasattr(self.org_target, '_hf_hook'):
            args, _ = self.org_target._hf_hook.pre_forward(self.org_target, input)
            input = args[0]

        if self._input_quantizer._if_calib:
            if self.org_target.groups == self.org_target.out_channels:
                self._weight_quantizer._input_cin_axis = 0

        if self._weight_quantizer.if_auto_get_scale:
            self._search_per_channel_scale_parameter(self.org_target.weight)
            return self.get_output(input, self.org_target.weight)

        if self._weight_quantizer.if_auto_get_clipping_bound:
            # TODO: _serach_clipping_range is not implemented
            self._serach_clipping_range(input, self.org_target.weight)
            return self.get_output(input, self.org_target.weight)

        if self._weight_quantizer.quant_desc.if_per_channel_scaling:
            quant_input, quant_weight = self._per_channel_scaling(input)
        elif self._input_quantizer.quant_desc.per_ch:
            quant_input, quant_weight = self._activation_per_channel_quant(input)
        else:
            quant_input, quant_weight = self._quant(input)

        if self.org_target.padding_mode == "circular":
            expanded_padding = (
                (self.org_target.padding[1] + 1) // 2,
                self.org_target.padding[1] // 2,
                (self.org_target.padding[0] + 1) // 2,
                self.org_target.padding[0] // 2,
            )
            output = F.conv2d(
                F.pad(quant_input, expanded_padding, mode="circular"),
                quant_weight,
                self.org_target.bias,
                self.org_target.stride,
                _pair(0),
                self.org_target.dilation,
                self.org_target.groups,
            )
        else:
            output = F.conv2d(
                quant_input,
                quant_weight,
                self.org_target.bias,
                self.org_target.stride,
                self.org_target.padding,
                self.org_target.dilation,
                self.org_target.groups,
            )

        if hasattr(self.org_target, '_hf_hook'):
            output = self.org_target._hf_hook.post_forward(self.org_target, output)

        return output
