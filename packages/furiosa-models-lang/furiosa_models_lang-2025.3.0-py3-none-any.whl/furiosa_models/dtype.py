from typing import Union

import torch

ALLOWED_MODEL_DTYPE = {
    "half": torch.float16,
    "float16": torch.float16,
    "float": torch.float32,
    "float32": torch.float32,
    "bfloat16": torch.bfloat16,
}


STR_DTYPE_TO_TORCH_DTYPE = {
    **ALLOWED_MODEL_DTYPE,
    "int32": torch.int32,
    "int64": torch.int64,
    "bool": torch.bool,
}


def normalize_dtype(dtype: Union[str, torch.dtype]) -> torch.dtype:
    """Convert dtype from str to torch.dtype if necessary."""
    if isinstance(dtype, torch.dtype):
        return dtype
    if isinstance(dtype, str):
        try:
            return STR_DTYPE_TO_TORCH_DTYPE[dtype]
        except KeyError:
            raise ValueError(f"Invalid dtype string: '{dtype}'")
    raise TypeError(f"Expected str or torch.dtype, got {type(dtype)}")
