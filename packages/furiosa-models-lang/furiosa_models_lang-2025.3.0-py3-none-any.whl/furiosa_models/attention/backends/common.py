from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import torch

from furiosa_models.attention.backends.base import (
    AttentionBackendBase,
    AttentionImplBase,
    AttentionMetadataBase,
)


class PagedAttentionBackend(AttentionBackendBase):
    """Backend for paged attention operations."""

    pass


@dataclass
class PagedAttentionMetadata(AttentionMetadataBase):
    """Metadata structure for paged attention operations.

    This class provides a generalized metadata structure for managing
    key-value (KV) cache mappings across various attention mechanisms.

    It supports configurable block sizes and includes slot offsets,
    making it suitable for both decoder-based and other types of attention models.

    Attributes:
        prefill_seq_lens (List[int]): Number of tokens in each sequence in the batch.
        block_size (int): Number of slots per cache block.
        write_block_mapping (Tuple[torch.Tensor, torch.Tensor]):
            - Block indices and slot offsets for writing new key-value pairs to the KV cache.
        load_block_mapping (Optional[Tuple[torch.Tensor, torch.Tensor]]):
            - Block indices and slot offsets for loading stored key-value pairs from the KV cache.
            If `None`, loading is skipped.
        max_seq_len (Optional[int]): Maximum sequence length. Defaults to `None`.
    """

    prefill_seq_lens: List[int]
    block_size: int

    # NOTE:
    # - `write_block_mapping` is intentionally kept as `init=True` to ensure compatibility with
    # `torch.export`.
    # - `torch._pytree.tree_unflatten()` requires all dataclass fields to be constructor arguments
    # during unflattening.
    # - Setting `init=False` breaks this contract and causes `TypeError` during export.
    # - The field is computed and overwritten in `__post_init__()`, so user input is ignored.
    write_block_mapping: Tuple[torch.Tensor, torch.Tensor] = field(
        default_factory=lambda: (torch.empty(0), torch.empty(0))
    )
    load_block_mapping: Optional[Tuple[torch.Tensor, torch.Tensor]] = None

    max_seq_len: Optional[int] = None

    def __post_init__(self) -> None:
        """Post-initialization for PagedAttentionMetadata.

        Raises:
            ValueError: If any input parameter is invalid (e.g., non-positive values).
        """
        if any(seq_len <= 0 for seq_len in self.prefill_seq_lens):
            raise ValueError("All values in prefill_seq_lens must be positive integers.")
        if self.block_size <= 0:
            raise ValueError("Block size must be a positive integer.")

        batch_size = len(self.prefill_seq_lens)
        max_query_len = max(self.prefill_seq_lens)

        self.write_block_mapping = self._compute_write_block_mapping(
            seq_len=max_query_len, block_size=self.block_size, batch_size=batch_size
        )

    def update(self, seq_len: int, past_seq_len: Optional[int] = None) -> None:
        """Update metadata for the decoding or continuous attention phase.

        This method updates the KV cache mappings by transferring previously written
        keys/values to `load_block_mapping`, ensuring their availability in
        subsequent attention computations.

        Args:
            seq_len (int): Number of new tokens to allocate in the KV cache.
            past_seq_len (Optional[int]): Number of tokens already stored in the KV cache.
        """
        self.load_block_mapping = (
            (
                torch.cat([self.load_block_mapping[0], self.write_block_mapping[0]], dim=1),
                torch.cat([self.load_block_mapping[1], self.write_block_mapping[1]], dim=1),
            )
            if self.load_block_mapping
            else self.write_block_mapping
        )

        batch_size = len(self.prefill_seq_lens)
        if past_seq_len is None:
            past_seq_len = self.write_block_mapping[0].size(1)  # (batch_size, past_seq_len)
        self.write_block_mapping = self._compute_write_block_mapping(
            seq_len=seq_len,
            block_size=self.block_size,
            batch_size=batch_size,
            past_seq_len=past_seq_len,
        )

    @staticmethod
    def _compute_write_block_mapping(
        seq_len: int, block_size: int, batch_size: int, past_seq_len: int = 0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute block indices and slot offsets for writing to the KV cache.

        This function determines where new keys/values should be stored in the KV cache.

        Args:
            seq_len (int): Number of new tokens to allocate.
            block_size (int): Number of tokens per cache block.
            batch_size (int): Number of sequences in the batch.
            past_seq_len (int, optional): Number of previously stored tokens.
                Defaults to 0.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Block indices and slot offsets.

        Raises:
            ValueError: If any of the input parameters are invalid.
        """
        if block_size <= 0:
            raise ValueError("Block size must be a positive integer.")
        if seq_len <= 0:
            raise ValueError("Sequence length must be a positive integer.")
        if batch_size <= 0:
            raise ValueError("Batch size must be a positive integer.")
        if past_seq_len < 0:
            raise ValueError("Past sequence length must be non-negative.")

        # Compute global slot indices
        start_idx = past_seq_len * batch_size
        end_idx = start_idx + (seq_len * batch_size)
        slot_indices = torch.arange(start_idx, end_idx, dtype=torch.int32).reshape(
            batch_size, seq_len
        )

        # Compute block indices & slot offsets
        block_indices = torch.div(slot_indices, block_size, rounding_mode="floor")
        slot_offsets = slot_indices % block_size

        return block_indices, slot_offsets

    def __repr__(self) -> str:
        """Return a formatted string representation of the metadata."""
        write_repr = (self.write_block_mapping[0].tolist(), self.write_block_mapping[1].tolist())
        load_repr = (
            (self.load_block_mapping[0].tolist(), self.load_block_mapping[1].tolist())
            if self.load_block_mapping
            else None
        )
        return (
            f"PagedAttentionMetadata(prefill={self.load_block_mapping is None}, "
            f"write_block_mapping={write_repr}, "
            f"load_block_mapping={load_repr})"
        )


class PagedAttentionImpl(AttentionImplBase):
    """Implementation of paged attention operations."""

    pass
