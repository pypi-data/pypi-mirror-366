from dataclasses import dataclass, field, fields
from typing import Optional


@dataclass
class CausalModelContexts:
    """Runtime contexts for causal language model export and execution.

    Attributes:
        batch_size (int): Batch size for the model.
        attention_size (int): Size of the attention input.
        kv_cache_size (int): Size of the key-value cache.
        paged_attention_block_size (int): Block size for paged attention.
        paged_attention_num_blocks (int): Number of blocks for paged attention.
        max_seq_len (int): Maximum sequence length for the model.
        is_prefill (bool): Whether the model is in prefill mode.
        prefill_seq_len (Optional[int]): Sequence length for prefill mode.
        past_seq_len (Optional[int]): Past sequence length for decode mode.
        decode_seq_len (Optional[int]): Sequence length for decode mode.
    """

    batch_size: int
    attention_size: int
    kv_cache_size: int
    paged_attention_block_size: int
    paged_attention_num_blocks: int

    # Derived fields
    max_seq_len: int = field(init=False)
    is_prefill: bool = field(init=False)
    prefill_seq_len: Optional[int] = field(init=False)
    past_seq_len: Optional[int] = field(init=False)
    decode_seq_len: Optional[int] = field(init=False)

    def __post_init__(self) -> None:
        """Post-initialization for CausalModelSequenceInfo."""
        for f in fields(self):
            # Skip Optional and derived (init=False) fields
            if f.init is False:
                continue

            value = getattr(self, f.name)
            expected_type = f.type

            if isinstance(expected_type, type):
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"{f.name} must be of type {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )

            # Positive value check (only for int)
            if expected_type is int:
                if f.name == "paged_attention_block_size":
                    if value != 1:
                        raise ValueError(f"{f.name} must be 1, but got {value}")
                if f.name == "kv_cache_size":
                    if value < 0:
                        raise ValueError(f"{f.name} must be a non-negative integer, got {value}")
                elif value <= 0:
                    raise ValueError(f"{f.name} must be a positive integer, got {value}")

        if self.attention_size <= self.kv_cache_size:
            raise ValueError("kv_cache_size cannot exceed attention_size")

        self.max_seq_len = self.paged_attention_block_size * self.paged_attention_num_blocks
        self.is_prefill = self.kv_cache_size == 0

        if self.is_prefill:
            self.prefill_seq_len = self.attention_size
            self.past_seq_len = None
            self.decode_seq_len = None
        else:
            self.prefill_seq_len = None
            self.past_seq_len = self.kv_cache_size
            self.decode_seq_len = self.attention_size - self.kv_cache_size
