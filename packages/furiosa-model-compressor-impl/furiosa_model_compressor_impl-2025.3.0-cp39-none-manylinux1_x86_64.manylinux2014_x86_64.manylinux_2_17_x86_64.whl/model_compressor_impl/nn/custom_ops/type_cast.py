from typing import Optional

import torch

from .furiosa_lib import define, impl_abstract_custom_op, impl_custom_op


def decode_int8_to_fp8(x: torch.Tensor, scope_dtype) -> torch.Tensor:
    exponent_bias = 7
    mantissa_bits = 3
    num_grid = 8

    if x.dtype != torch.int8:
        raise ValueError("input dtype of decode_int8_to_fp8 must be int8 tensor")

    unsigned_inputs = x.to(torch.int16) & 0xFF  # Use int16 to avoid overflow
    sign = ((unsigned_inputs & 0x80).to(torch.uint8) >> 7).to(scope_dtype)
    exponent = ((unsigned_inputs & 0x78) >> 3).to(scope_dtype) - exponent_bias
    mantissa = (unsigned_inputs & 0x07).to(scope_dtype)

    converted_fp8 = torch.where(
        exponent > -exponent_bias,
        torch.pow(-1, sign) * torch.pow(2, exponent - mantissa_bits) * (num_grid + mantissa),
        torch.pow(-1, sign) * torch.pow(2, exponent + 1 - mantissa_bits) * mantissa,
    )

    return converted_fp8


def pack_int4_to_int8(inputs):
    # int4 element 두 개를 합쳐 한개의 int8 element 한 개로 변환하는 함수
    assert inputs.shape[1] % 2 == 0, "Tensor's second dimension must be even."

    first_int4 = inputs[..., ::2] & 0x0F
    second_int4 = inputs[..., 1::2] & 0x0F
    combined = (first_int4 << 4) | second_int4

    return combined


def unpack_int8_to_int4(inputs, scope_dtype=torch.int8):
    # int4 element 두 개가 합쳐진 int8 element를 int4 element 2개로 변환하는 함수
    *rest_dims, half_length = inputs.shape  # 마지막 축의 길이 추출
    full_length = half_length * 2

    first_int4 = ((inputs >> 4) & 0x0F).to(torch.int8)
    first_int4_signed = torch.where(first_int4 >= 8, first_int4 - 16, first_int4)  # 부호 반영
    second_int4 = (inputs & 0x0F).to(torch.int8)
    second_int4_signed = torch.where(second_int4 >= 8, second_int4 - 16, second_int4)  # 부호 반영

    result_tensor = torch.stack([first_int4_signed, second_int4_signed], dim=-1).view(
        *rest_dims, full_length
    )
    result_tensor = result_tensor.to(scope_dtype)

    return result_tensor


@define()
def type_emulation_in(
    x: torch.Tensor, cast_type: str, scope: Optional[str], scope_dtype: torch.dtype
) -> torch.Tensor:
    if scope_dtype not in [torch.float32, torch.float64]:
        raise ValueError("scope_dtype is only valid for float32 and float64")

    if cast_type == 'fp8-E4M3':
        a = decode_int8_to_fp8(x, scope_dtype)
    elif cast_type == 'int4':
        a = unpack_int8_to_int4(x, scope_dtype)
    else:
        a = x.to(scope_dtype)
    return a


impl_custom_op(type_emulation_in, ['CUDA'], type_emulation_in)


@impl_abstract_custom_op(type_emulation_in)
def type_emulation_in_abstract(x, cast_type, scope, scope_dtype):
    if cast_type == 'int4':
        *rest_dims, half_length = x.shape  # 마지막 축의 길이 추출
        full_length = half_length * 2
        return x.new_empty((*rest_dims, full_length), dtype=scope_dtype)
    return x.new_empty(x.shape, dtype=scope_dtype)


@define()
def type_emulation_out(
    x: torch.Tensor, out_type: torch.dtype, scope: Optional[str]
) -> torch.Tensor:
    if out_type not in [torch.int32, torch.float32]:
        raise f"invalid type ({out_type})"
    a = x.to(out_type)
    return a


impl_custom_op(type_emulation_out, ['CUDA'], type_emulation_out)


@impl_abstract_custom_op(type_emulation_out)
def type_emulation_out_abstract(x, out_type, scope):
    return x.new_empty(x.shape, dtype=out_type)
