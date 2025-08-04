import torch

DATA_MAPPER = {
    "int4": torch.int8,
    "fp8": torch.float64,
    'fp8-E4M3': torch.int8,
    "int8": torch.int8,
    "bf16": torch.bfloat16,
    'bfloat16': torch.bfloat16,
    "fp32": torch.float32,
    'float32': torch.float32,
    "fp64": torch.float64,
    'float64': torch.float64,
}

DATA_MATCHER = {
    "int4": "int4",
    "int5": "int5",
    "int8": "int8",
    "int9": "int9",
    "fp8-E4M3": "fp8-E4M3",
    "bfloat16": "bfloat16",
    "bf16": "bfloat16",
    "float32": "float32",
    "fp32": "float32",
    "fp64": "float64",
}


def real_dtype_map(input):
    REAL_DTYPE_MAP = {
        torch.int8: 'int8',
        torch.bfloat16: 'bfloat16',
        torch.float32: 'float32',
        torch.float64: 'float64',
    }
    return REAL_DTYPE_MAP[input.dtype]


FETCH_DTYPE_MAP = {
    "int4": "int5",
    "int8": "int9",
}
