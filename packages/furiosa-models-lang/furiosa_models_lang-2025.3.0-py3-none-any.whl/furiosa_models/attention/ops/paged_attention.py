from typing import Optional, Tuple

import torch

from furiosa_models.attention.ops.base import AttentionOpBase
from furiosa_models.attention.ops.scaled_dot_product import scaled_dot_product_attention


class PagedAttention(AttentionOpBase):
    """Implements paged attention for efficient key-value cache management.

    Paged attention segments long sequences into smaller blocks for more efficient computation,
    reducing memory overhead. This method is especially useful for managing KV cache in large-scale
    transformer models.
    """

    @staticmethod
    def get_kv_cache_shape(
        batch_size: int,
        max_seq_len: int,
        block_size: int,
        num_kv_heads: int,
        head_size: int,
    ) -> Tuple[int, ...]:
        """Computes the shape of the key-value cache tensor for paged attention.

        Args:
            batch_size (int): Number of sequences in a batch.
            max_seq_len (int): Maximum length of input sequences.
            block_size (int): Number of tokens per block.
            num_kv_heads (int): Number of key-value heads.
            head_size (int): Dimensionality of each attention head.

        Returns:
            Tuple[int, ...]: Shape of the KV cache tensor as:
                `(num_blocks, block_size, num_kv_heads, head_size)`,
                where `num_blocks = (batch_size * max_seq_len + block_size) // block_size`.
        """
        assert block_size > 0, "Block size must be a positive integer."
        assert num_kv_heads > 0, "Number of key-value heads must be a positive integer."
        assert head_size > 0, "Head size must be a positive integer."
        assert batch_size > 0, "Batch size must be a positive integer."

        num_blocks = (batch_size * max_seq_len + block_size) // block_size
        return (num_blocks, block_size, num_kv_heads, head_size)

    @staticmethod
    def write_to_paged_cache(
        input_tensor: torch.Tensor,
        cache_tensor: torch.Tensor,
        block_indices: torch.Tensor,
        slot_offsets: Optional[torch.Tensor] = None,
    ) -> None:
        """Writes key and value tensors into the KV cache using advanced indexing.

        Args:
            input_tensor (torch.Tensor): Input tensor to write to cache, of shape
                `(batch_size, seq_len, num_kv_heads, head_dim)`.
            cache_tensor (torch.Tensor): Cache tensor to write to, of shape
                `(num_blocks, block_size, num_kv_heads, head_dim)`.
            block_indices (torch.Tensor): Block indices to write to, of shape
                `(batch_size * seq_len,)`.
            slot_offsets (Optional[torch.Tensor]): Slot offsets within each block, of shape
                `(batch_size * seq_len,)`.

        Raises:
            ValueError: If block indices or slot offsets exceed cache dimensions.
        """
        assert block_indices.ndim == 1, (
            f"Block indices must be 1D tensor. Got block_indices.ndim={block_indices.ndim}"
        )

        if slot_offsets is not None:
            assert slot_offsets.ndim == 1, (
                f"Slot offsets must be 1D tensor. Got slot_offsets.ndim={slot_offsets.ndim}"
            )

        if not torch.compiler.is_compiling():
            if cache_tensor.shape[0] <= block_indices.max().item():
                raise ValueError(
                    f"Block index {block_indices.max()} exceeds available blocks "
                    f"{input_tensor.shape[0]}."
                )

            if slot_offsets is not None:
                if cache_tensor.shape[1] <= slot_offsets.max().item():
                    raise ValueError(
                        f"Slot offset {slot_offsets.max()} exceeds available "
                        f"slots per block {cache_tensor.shape[1]}."
                    )

        if cache_tensor.shape[1] > 1 and slot_offsets is None:
            raise ValueError(
                f"Slot offsets must be provided when block_size > 1. "
                f"Got cache_tensor.shape[1]={cache_tensor.shape[1]}."
            )

        assert cache_tensor.dtype == input_tensor.dtype, (
            f"Key cache dtype must match key dtype. "
            f"Got key_cache.dtype={cache_tensor.dtype}, key.dtype={input_tensor.dtype}"
        )

        if slot_offsets is not None:
            # flatten as (batch_size * seq_len, num_kv_heads, head_dim)
            cache_tensor[block_indices, slot_offsets] = input_tensor.flatten(0, 1)
        else:
            # flatten and unsqueeze to (batch_size * seq_len, 1, num_kv_heads, head_dim)
            cache_tensor[block_indices] = input_tensor.flatten(0, 1).unsqueeze(1)

    @staticmethod
    def load_from_paged_cache(
        cache_tensor: torch.Tensor,
        block_indices: torch.Tensor,
        slot_offsets: Optional[torch.Tensor] = None,
        target_shape: Tuple[int, ...] = (),
    ) -> torch.Tensor:
        """Loads key and value tensors from the KV cache for attention computation.

        Args:
            cache_tensor (torch.Tensor): Cache tensor to read from, of shape
                `(num_blocks, block_size, num_kv_heads, head_dim)`.
            block_indices (torch.Tensor): Block indices to retrieve from, shape
                `(batch_size * seq_len,)`.
            slot_offsets (Optional[torch.Tensor]): Slot offsets within each block, shape
                `(batch_size * seq_len,)`.
            target_shape (Tuple[int, ...]): Target shape for the retrieved key and value tensors,
                of shape `(batch_size, seq_len, num_kv_heads, head_dim)`.

        Returns:
            torch.Tensor: Retrieved key and value tensors reshaped to match
                `target_shape`.

        Raises:
            ValueError: If block indices or slot offsets exceed cache dimensions.
        """
        if not torch.compiler.is_compiling():
            if cache_tensor.shape[0] <= block_indices.max().item():
                raise ValueError(
                    f"Block index {block_indices.max()} exceeds available blocks "
                    f"{cache_tensor.shape[0]}."
                )

            if slot_offsets is not None:
                if cache_tensor.shape[1] <= slot_offsets.max().item():
                    raise ValueError(
                        f"Slot offset {slot_offsets.max()} exceeds available "
                        f"slots per block {cache_tensor.shape[1]}."
                    )

        if cache_tensor.shape[1] > 1 and slot_offsets is None:
            raise ValueError(
                f"Slot offsets must be provided when block_size > 1. "
                f"Got cache_tensor.shape[1]={cache_tensor.shape[1]}."
            )

        if slot_offsets is not None:
            return cache_tensor[block_indices, slot_offsets].contiguous().view(*target_shape)
        else:
            return cache_tensor[block_indices].contiguous().view(*target_shape)

    @staticmethod
    def forward(
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        scale: float,
        attn_mask: Optional[torch.Tensor] = None,
        is_causal: bool = True,
        enable_gqa: bool = False,
        mask_value: float = float("-inf"),
    ) -> torch.Tensor:
        """Computes scaled dot-product attention.

        The computation follows:
        1. Compute raw attention scores: `scores = (Q @ K^T) / scaling_factor`
        2. Apply optional causal masking to prevent future token access.
        3. Apply optional attention mask (e.g., for padding).
        4. Compute attention weights via softmax.
        5. Compute final output as weighted sum of values: `output = softmax(scores) @ V`.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, seq_len, num_heads, head_dim)`.
            key (torch.Tensor): Key tensor of shape `(batch_size, seq_len, num_kv_heads, head_dim)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, seq_len, num_kv_heads, head_dim)`.
            scale (float): Scaling factor for dot product.
            attn_mask (Optional[torch.Tensor], optional): Optional attention mask (default: None).
            is_causal (bool, optional): Whether to apply causal masking (default: True).
            enable_gqa (bool, optional): Whether to enable Grouped Query Attention (default: False).
            mask_value (float, optional): Value to use for masking in the attention scores

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, seq_len, num_heads, head_dim)`.
        """
        query = query.permute(0, 2, 1, 3)
        key = key.permute(0, 2, 1, 3)
        value = value.permute(0, 2, 1, 3)

        if attn_mask is not None:
            assert attn_mask.size(-2) == query.size(-2), (
                f"attn_mask last-2 dim ({attn_mask.size(-2)}) must match query seq_len "
                f"({query.size(-2)})"
            )

            if attn_mask.ndim == 3:
                assert attn_mask.size(0) == query.size(0), (
                    f"attn_mask first dim ({attn_mask.size(0)}) must match query batch size "
                    f"({query.size(0)})"
                )
                attn_mask = attn_mask.unsqueeze(1)

        attn_out = scaled_dot_product_attention(
            query,
            key,
            value,
            attn_mask=attn_mask,
            is_causal=is_causal,
            scale=scale,
            enable_gqa=enable_gqa,
            mask_value=mask_value,
        )

        return attn_out.permute(0, 2, 1, 3)
