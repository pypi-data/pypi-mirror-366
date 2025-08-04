import re

import torch

from . import qlevel2

__all__ = [
    'get_base_name_of_mod_type',
    'is_fixed_output_type_op',
    'is_weighted_op',
    'is_softmax_op',
    'is_accumulate_op',
    'is_multi_input_qlv2_mcm',
]

'''
torch module 뿐 아니라 qlevel 1~4 module도 포함하기 위해서 basename을 추출해서 비교합니다.
대소문자 구분은 다양할 수 있기 위해서 아래 group은 소문자로만 작성하는 것을 규칙으로 합니다.
'''

EMBEDDING_OP = [
    'embedding',
    'fembedding',
]


# einsum operator는 독특한 특성을 갖기 때문에 별도 list로 관리합니다.
# 개념자체로 보면 dot-product 연산을 수행하는 weigthed operator가 맞지만,
# 연산의 높은 자유도 특성때문에 실제 사용케이스에서는 RoPE apply등 특수연산에서 사용되는 경우가 대부분이기 떄문에
# major_dtype을 적용하지 않는 것이 일반적이라서 weigthed operator가 아닌 것처럼 다룹니다.
EINSUM_OP = [
    'einsum',
]

TRAINABLE_WEIGHTED_OP = EMBEDDING_OP + [
    'linear',
    'conv2d',
    'convtranspose2d',
]

WEIGHTED_OP = (
    TRAINABLE_WEIGHTED_OP
    + EINSUM_OP
    + [
        'bmm',
        'matmul',
    ]
)

SOFTMAX_OP = [
    'softmax',
    'fsoftmax',
]

INTER_CH_NONLINEAR_OP = SOFTMAX_OP + [
    'layernorm',
    'log_softmax',
]

MULTIPLE_INPUT_OP = [
    qlevel2.ModelCompressorModuleConcat,
    qlevel2.ModelCompressorModuleBinary,
    qlevel2.ModelCompressorModuleEinsum,
]


def get_base_name_of_mod_type(module: torch.nn.Module) -> str:

    mod_type = type(module).__name__

    if mod_type == 'ModuleSkeleton':
        mod_type = module.loaded_module_class
        if 'ModelCompressorModule' in mod_type:
            mod_type = module.org_target_type_name
    else:
        if 'ModelCompressorModule' in mod_type:
            mod_type = module.org_target_type.__name__

    mod_type = mod_type.rsplit('.', 1)[-1]

    mod_type = re.sub(r'^_', '', mod_type)
    mod_type = re.sub(r'^QLV[1-4]_', '', mod_type)
    mod_type = re.sub(r'^ModelCompressorModule', '', mod_type)
    mod_type = re.sub(r'_MOD$', '', mod_type)

    return mod_type


def is_weighted_op(module: torch.nn.Module, exclude_einsum=True) -> bool:
    base_name = get_base_name_of_mod_type(module)
    if base_name.lower() in WEIGHTED_OP:
        if exclude_einsum:
            # EINSUM_OP 선언 부분에 있는 주석 참고.
            return base_name.lower() not in EINSUM_OP
        else:
            return True

    return False


def is_softmax_op(module: torch.nn.Module) -> bool:
    base_name = get_base_name_of_mod_type(module)
    return base_name.lower() in SOFTMAX_OP


def is_accumulate_op(module: torch.nn.Module) -> bool:
    base_name = get_base_name_of_mod_type(module)
    if base_name.lower() in WEIGHTED_OP + INTER_CH_NONLINEAR_OP:
        if base_name.lower() not in EMBEDDING_OP:
            return True

    return False


def is_fixed_output_type_op(module: torch.nn.Module) -> bool:
    # input과 무관하게 output data type이 정해지는 node인지 확인합니다.
    # embedding module은 input과 무관하게 weight에 의해 output data type이 정해지고,
    # accumulate_op들은 accumulation data type에 의해 output data type이 결정됩니다.
    # call_module을 대상으로 하기에 MCM이 아닌 모듈(e.g. dropout)이 입력될 수 있습니다.
    # True를 return하는 경우 QLV2 MCM를 가정합니다.

    base_name = get_base_name_of_mod_type(module)
    if base_name.lower() in EMBEDDING_OP:
        if not isinstance(module, qlevel2.ModelCompressorModule):
            raise ValueError("is_fixed_output_type_op() assumes qlevel2 mcm.")
        return True
    else:
        if is_accumulate_op(module):
            if not isinstance(module, qlevel2.ModelCompressorModule):
                raise ValueError("is_fixed_output_type_op() assumes qlevel2 mcm.")
            return True
        else:
            return False


def is_multi_input_qlv2_mcm(module: torch.nn.Module) -> bool:
    return isinstance(module, tuple(MULTIPLE_INPUT_OP))
