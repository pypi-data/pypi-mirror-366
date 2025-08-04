import torch

from ...quant_op.custom_ops import away_from_zero_round
from .furiosa_lib import define, impl_abstract_custom_op, impl_custom_op


@define()
def away_from_zero_fp2fxp(x: torch.Tensor) -> torch.Tensor:
    iinfo = torch.iinfo(torch.int32)
    x = torch.ops.prims.trunc(x + torch.ops.aten.mul.Scalar(torch.ops.prims.sign(x), 0.5))
    x = torch.ops.aten.clamp(x, iinfo.min, iinfo.max)
    x = torch.ops.aten._to_copy(x, dtype=torch.int32)

    return x


impl_custom_op(away_from_zero_fp2fxp, ['CUDA'], away_from_zero_fp2fxp)


@impl_abstract_custom_op(away_from_zero_fp2fxp)
def away_from_zero_fp2fxp_abstract(x):
    return x.new_empty(x.shape, dtype=torch.int32)


@define()
def fp32_to_fp8_cast(inputs: torch.Tensor) -> torch.Tensor:
    mantissa_bits = 3
    max_value = 448
    exponent_bias = 7
    exponent_bits = 4

    output = torch.clip(inputs, -max_value, max_value)

    _exponent = torch.floor(torch.log2(torch.abs(output)))
    _exponent = torch.where(
        _exponent > 1 - exponent_bias, _exponent, torch.tensor(1 - exponent_bias)
    )

    s_i = torch.pow(2, _exponent - mantissa_bits)

    # output = away_from_zero_round(output / s_i) * s_i  # fakequant 연산
    _cnt = away_from_zero_round(torch.abs(output) / s_i)
    # ==============================================================================
    sign = torch.where(output >= 0.0, 0, 1)

    # subnormal 영역 처리
    mantissa = torch.where(_cnt < pow(2, mantissa_bits), _cnt, _cnt - pow(2, mantissa_bits))
    exponent = torch.where(_cnt < pow(2, mantissa_bits), _exponent - 1, _exponent)

    # mantissa 가 2^mantissa_bits 인 경우, exponent 를 1 더하고, mantissa 값을 0으로 맞춰준다.
    exponent = torch.where(mantissa == 8, exponent + 1, exponent)
    mantissa = torch.where(mantissa == 8, 0, mantissa)

    # encoding fp8 to int8
    result_tensor = torch.zeros(sign.shape, dtype=torch.int8)

    exponent = exponent + exponent_bias

    sign_bin = sign.to(torch.uint8) & 0x01  # 1 bit for sign
    exponent_bin = exponent.to(torch.uint8) & 0x0F  # 4 bits for exponent
    mantissa_bin = mantissa.to(torch.uint8) & 0x07  # 3 bits for mantissa

    combined_bin = (sign_bin << 7) | (exponent_bin << 3) | mantissa_bin

    # Convert binary tensor to integer tensor
    result_tensor = combined_bin.to(torch.int8)

    # Handle negative values based on the sign bit
    result_tensor[result_tensor >= 128] -= 256

    return result_tensor.to(torch.int8)


impl_custom_op(fp32_to_fp8_cast, ['CUDA'], fp32_to_fp8_cast)


@impl_abstract_custom_op(fp32_to_fp8_cast)
def fp32_to_fp8_cast_abstract(x):
    return x.new_empty(x.shape, dtype=torch.int8)
