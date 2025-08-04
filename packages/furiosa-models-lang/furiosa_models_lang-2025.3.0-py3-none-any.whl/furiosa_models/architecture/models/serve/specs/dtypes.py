from dataclasses import dataclass, field

import torch

from furiosa_models.dtype import ALLOWED_MODEL_DTYPE, normalize_dtype


@dataclass
class CausalModelInputDtypes:
    """Input tensor dtypes for causal language model export."""

    _INPUT_IDS_DTYPE = torch.int32
    _POSITION_IDS_DTYPE = torch.int32
    _ATTENTION_MASKS_DTYPE = torch.bool

    input_ids: torch.dtype = field(init=False, default=_INPUT_IDS_DTYPE)
    position_ids: torch.dtype = field(init=False, default=_POSITION_IDS_DTYPE)
    attention_masks: torch.dtype = field(init=False, default=_ATTENTION_MASKS_DTYPE)
    kv_cache: torch.dtype = torch.bfloat16  # can be string or torch.dtype

    def __post_init__(self) -> None:
        """Post-initialization for CausalModelInputDtypes."""
        self.kv_cache = normalize_dtype(self.kv_cache)
        if self.kv_cache not in ALLOWED_MODEL_DTYPE.values():
            raise TypeError(
                f"Invalid kv_cache dtype: {self.kv_cache!r}. "
                f"Allowed values are: {ALLOWED_MODEL_DTYPE.values()}."
            )
