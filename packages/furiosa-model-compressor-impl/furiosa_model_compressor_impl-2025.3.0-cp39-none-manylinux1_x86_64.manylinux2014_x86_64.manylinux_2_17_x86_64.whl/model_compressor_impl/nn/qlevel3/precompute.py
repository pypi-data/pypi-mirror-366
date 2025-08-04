import torch

from ...quant_op.custom_ops import away_from_zero_round, fp32_to_fp8_cast
from ...quant_op.tensor_quantizer import _reshape_for_group_quantization
from ...utils.datamapper import DATA_MAPPER

__all__ = [
    "get_qparams",
    "get_precompute_qparams",
    "get_matamul_precompute_qparams",
]


def get_qparams(
    quantizer,
    weight=None,
    if_bcq=False,
    device='cpu',
    is_output_node_matmul=False,
    args_idx=None,
    is_attention_matmul_score_by_value=False,
    smooth_factor=1.0,
    cur_node_output_shape=None,
):
    if quantizer.disabled or quantizer.quant_desc.dtype in ['bf16', 'fp32', 'auto']:
        return (torch.tensor(1.0, device=device), torch.tensor(0.0, device=device))

    if if_bcq:
        basis = quantizer._basis

        quantizer.calibrator._levels = quantizer.levels
        quantizer.calibrator._thres = quantizer.thres
        quantizer.calibrator._level_codes = quantizer.level_codes
        quantizer.calibrator._ch = quantizer.ch
        b = quantizer.calibrator._search_binary_tensors(weight)

        tensor_shape = list(weight.shape)
        tensor_shape[0] = weight.shape[0] * quantizer.num_bits
        b = b.permute(1, 0, 2).reshape(tensor_shape)

        return (basis, b)
    else:
        num_bits = quantizer.quant_desc.num_bits
        unsigned = quantizer.quant_desc.unsigned

        if quantizer.quant_desc.asymmetric:
            max, min = quantizer.max, quantizer.min
            scale = (max - min) / (2.0**num_bits - 1)
            scale = torch.where(scale > 1e-7, scale, 1e-7)

            min_bound = -(2.0 ** (num_bits - 1))
            max_bound = 2.0 ** (num_bits - 1) - 1

            zero_point = min_bound - away_from_zero_round(min / scale)
        else:
            amax = quantizer._amax
            # Computation must be in FP32 to prevent potential over flow.
            if amax.dtype == torch.half:
                amax = amax.float()

            if quantizer.quant_desc.dtype == 'fp8-E4M3':
                max_value = torch.tensor(448, dtype=torch.float32, device=amax.device)
                ratio = torch.floor(torch.log2(max_value / amax))
                scale = 1 / torch.pow(2, ratio)
                zero_point = torch.zeros(amax.shape, dtype=amax.dtype, device=amax.device)
            else:
                max_bound = torch.tensor(
                    (2.0 ** (num_bits - 1 + int(unsigned))) - 1.0, device=amax.device
                )
                zero_point = torch.tensor([0.0], dtype=amax.dtype, device=amax.device)

                scale = amax / max_bound

            scale = torch.where(scale > 1e-7, scale, 1e-7)

        if is_output_node_matmul:
            if args_idx == 0 or is_attention_matmul_score_by_value:
                head_dim = quantizer.quant_desc.input_shape[3]
            elif args_idx == 1:
                head_dim = quantizer.quant_desc.input_shape[2]
            else:
                raise ValueError("This case shouldn't occurs")

            if cur_node_output_shape is not None and len(scale.shape) > 0:
                if len(cur_node_output_shape) == 3:
                    n_key_value_heads = cur_node_output_shape[-1] // head_dim
                elif len(cur_node_output_shape) == 4:
                    n_key_value_heads = cur_node_output_shape[1]
                    if scale.shape[-1] // n_key_value_heads == 0:
                        n_key_value_heads = cur_node_output_shape[2]
                elif len(cur_node_output_shape) == 5:
                    # Einsum ROPE case
                    n_key_value_heads = cur_node_output_shape[1]
                else:
                    raise ValueError("Not considered case")

                n_groups = scale.shape[-1] // n_key_value_heads

                scale = (
                    scale.view(-1, n_groups).split(1, dim=1)[0].flatten()
                )  # match with group query attention shape
                zero_point = zero_point.view(-1, n_groups).split(1, dim=1)[0].flatten()

                if len(cur_node_output_shape) == 3:
                    scale = scale.repeat_interleave(head_dim, dim=0)
                    zero_point = zero_point.repeat_interleave(head_dim, dim=0)

        return (scale * smooth_factor, zero_point)


def _adjust_weight_qparam_shape_with_scale(weight_qparams, weight_quantizer, weight):
    scale_weight, zero_weight = weight_qparams
    scale_weight = scale_weight[(...,) + (None,) * (weight.ndim - scale_weight.ndim)]
    if weight_quantizer.quant_desc.asymmetric is not None:
        zero_weight = zero_weight[(...,) + (None,) * (weight.ndim - zero_weight.ndim)]
    return scale_weight, zero_weight


def _merge_perch_scale_to_weight(org_mod, weight, input_quantizer, scale_input, is_decode):
    if weight.device.type == 'meta':
        return weight

    if isinstance(org_mod, torch.nn.Conv2d):
        return _adjust_conv2d_weight(org_mod, weight, input_quantizer, scale_input, is_decode)
    elif isinstance(org_mod, torch.nn.Linear):
        return _adjust_linear_weight(weight, input_quantizer, scale_input, is_decode)
    else:
        raise NotImplementedError(
            "Merged Qparams are not implemented when the operator is neither Linear nor Conv2d"
        )


def _adjust_conv2d_weight(org_mod, weight, input_quantizer, scale_input, is_decode):
    if input_quantizer.quant_desc.per_ch and not is_decode:
        if org_mod.groups == org_mod.out_channels:
            perch_scale = scale_input[(...,) + (None,) * (weight.ndim - scale_input.ndim)]
        else:
            perch_scale = scale_input[
                (None,) + (...,) + (None,) * (weight.ndim - scale_input.ndim - 1)
            ]
        weight = weight * perch_scale
    return weight


def _adjust_linear_weight(weight, input_quantizer, scale_input, is_decode):
    if input_quantizer.quant_desc.per_ch and not is_decode:
        weight = weight * scale_input
        while weight.dim() > 2:
            weight = weight.squeeze(0)
        if weight.dim() != 2:
            raise ValueError("Shape of redefined_weight should be 2D!")
    return weight


def _calculate_quantized_weight_value(
    weight, weight_quantizer, scale_weight, zero_weight, smooth_factor
):
    if weight_quantizer.quant_desc.dtype == 'fp8-E4M3':
        return fp32_to_fp8_cast(weight / scale_weight)

    quantized_weight = weight_quantizer(weight * smooth_factor)
    if weight_quantizer.quant_desc.group_size and weight_quantizer.quant_desc.group_size > 1:
        quantized_weight = (
            _reshape_for_group_quantization(
                weight_quantizer, quantized_weight, weight_quantizer.quant_desc.group_size
            )
            / scale_weight
        )
        if weight_quantizer.quant_desc.asymmetric:
            quantized_weight = quantized_weight + zero_weight
        return quantized_weight.reshape(weight.shape)
    return quantized_weight / scale_weight


def _quantize_weight(weight, weight_quantizer, scale_weight, zero_weight, smooth_factor, is_decode):
    if is_decode or weight.device.type == 'meta':
        return weight

    quantized_weight = _calculate_quantized_weight_value(
        weight, weight_quantizer, scale_weight, zero_weight, smooth_factor
    )
    weight_dtype = (
        torch.float32
        if weight_quantizer.disabled
        else DATA_MAPPER[weight_quantizer.quant_desc.dtype]
    )
    if not weight_dtype.is_floating_point:
        quantized_weight = away_from_zero_round(quantized_weight)

    return quantized_weight.to(weight_dtype)


def _calculate_quantized_weight_sum(weight, zero_input, input_quantizer, org_mod):
    if weight.device.type != 'meta':
        if input_quantizer.quant_desc.per_ch and input_quantizer.quant_desc.dtype != 'fp8-E4M3':
            return _calculate_per_channel_quantized_weight_sum(weight, zero_input, org_mod)
        elif input_quantizer.quant_desc.dtype == 'fp8-E4M3':
            # input qparam에 zero_point가 0이라 별도의 계산이 필요 없음
            return torch.tensor([0.0])
        return weight.reshape(weight.shape[0], -1).sum(-1)
    else:
        return torch.tensor([0.0])


def _calculate_per_channel_quantized_weight_sum(weight, zero_input, org_mod):
    if isinstance(org_mod, torch.nn.Conv2d):
        if org_mod.groups == org_mod.out_channels:
            quantized_weight_sum = weight.to(torch.float64) * zero_input[
                (...,) + (None,) * (weight.ndim - zero_input.ndim)
            ].to(torch.float64)
        else:
            quantized_weight_sum = weight.to(torch.float64) * zero_input[
                (None,) + (...,) + (None,) * (weight.ndim - zero_input.ndim - 1)
            ].to(torch.float64)
    else:
        quantized_weight_sum = weight.to(torch.float64) * zero_input.to(torch.float64)
    return quantized_weight_sum.reshape(weight.shape[0], -1).sum(-1)


def _convert_data_types(scale_weight, scale_input, zero_input, scale_output, weight_sum, bias):
    scale_weight = scale_weight.squeeze().to(torch.float64)
    scale_input = scale_input.squeeze().to(torch.float64)
    zero_input = zero_input.to(torch.float64)
    scale_output = scale_output.squeeze().to(device=scale_weight.device, dtype=torch.float64)
    weight_sum = weight_sum.to(device=scale_weight.device, dtype=torch.float64)
    bias = bias.to(device=scale_weight.device, dtype=torch.float64)
    return scale_weight, scale_input, zero_input, scale_output, weight_sum, bias


def _merge_qparams(
    weight_sum,
    bias,
    scale_weight,
    scale_input,
    zero_input,
    scale_output,
    zero_output,
    is_output_quantized,
    input_quantizer,
    weight_quantizer,
):

    scale_weight, scale_input, zero_input, scale_output, weight_sum, bias = _convert_data_types(
        scale_weight, scale_input, zero_input, scale_output, weight_sum, bias
    )

    if weight_quantizer.quant_desc.group_size and weight_quantizer.quant_desc.group_size > 1:
        return _group_merged_qparams(scale_input, bias, scale_output, zero_output, input_quantizer)
    elif input_quantizer.quant_desc.per_ch:
        # scale of input activation was already merged to weight scale for per_channel case.
        # zero_input was alread merged to weight_sum for per-channel case.
        return _per_channel_merged_qparams(
            weight_sum, bias, scale_weight, scale_output, zero_output, is_output_quantized
        )
    return _per_tensor_merged_qparams(
        weight_sum,
        bias,
        scale_weight,
        scale_input,
        zero_input,
        scale_output,
        zero_output,
        is_output_quantized,
        input_quantizer,
    )


def _group_merged_qparams(scale_input, bias, scale_output, zero_output, input_quantizer):
    if input_quantizer.quant_desc.num_bits == 16:
        merged_scale = scale_output
        merged_bias = bias + zero_output * scale_output
        imbias = bias
    elif input_quantizer.quant_desc.num_bits < 16:
        raise NotImplementedError("Group quantization without decoding is not implemented yet")
    else:
        raise ValueError("FP32 input is not supported")

    return merged_scale, merged_bias, imbias


def _per_channel_merged_qparams(
    weight_sum, bias, scale_weight, scale_output, zero_output, is_output_quantized
):
    imbias = (bias / scale_weight) - weight_sum
    if is_output_quantized:
        # when output tensor of current node is used by only one node, then output zero point can be merged to bias
        merged_scale = scale_output / scale_weight
        merged_bias = imbias + (zero_output * scale_output / scale_weight)
    else:
        merged_scale = 1 / scale_weight
        merged_bias = imbias
    return merged_scale, merged_bias, imbias


def _per_tensor_merged_qparams(
    weight_sum,
    bias,
    scale_weight,
    scale_input,
    zero_input,
    scale_output,
    zero_output,
    is_output_quantized,
    input_quantizer,
):
    imbias = (bias / (scale_weight * scale_input)) - zero_input * weight_sum
    if is_output_quantized:
        if input_quantizer.quant_desc.num_bits == 16:
            merged_scale = scale_output
            merged_bias = bias + zero_output * scale_output
            imbias = bias
        else:
            merged_scale = scale_output / (scale_weight * scale_input)
            merged_bias = imbias + (zero_output * scale_output / (scale_weight * scale_input))
    else:
        merged_scale = 1 / (scale_weight * scale_input)
        merged_bias = imbias
    return merged_scale, merged_bias, imbias


def get_precompute_qparams(
    org_mod,
    input_qparams,
    weight_qparams,
    output_qparams,
    input_quantizer,
    weight_quantizer,
    is_output_quantized=True,
    is_decode=False,
    smooth_factor=1.0,
):
    weight = org_mod.weight
    bias = (
        org_mod.bias
        if hasattr(org_mod, 'bias')
        and org_mod.bias is not None
        and org_mod.weight.device.type != 'meta'
        else torch.tensor(0.0)
    )
    scale_weight, zero_weight = _adjust_weight_qparam_shape_with_scale(
        weight_qparams, weight_quantizer, weight
    )
    scale_input, zero_input = input_qparams
    scale_output, zero_output = output_qparams

    weight = _merge_perch_scale_to_weight(org_mod, weight, input_quantizer, scale_input, is_decode)
    weight = _quantize_weight(
        weight, weight_quantizer, scale_weight, zero_weight, smooth_factor, is_decode
    )
    weight_sum = _calculate_quantized_weight_sum(weight, zero_input, input_quantizer, org_mod)

    merged_scale, merged_bias, imbias = _merge_qparams(
        weight_sum,
        bias,
        scale_weight,
        scale_input,
        zero_input,
        scale_output,
        zero_output,
        is_output_quantized,
        input_quantizer,
        weight_quantizer,
    )

    return merged_scale.to(torch.float32), merged_bias, weight, imbias


def get_matamul_precompute_qparams(
    input0_scale, input1_scale, output_scale, single_op_case=False, smooth_factor=1.0
):
    if single_op_case:
        return output_scale * smooth_factor / input0_scale / input1_scale
    else:
        return 1 / input0_scale / input1_scale
