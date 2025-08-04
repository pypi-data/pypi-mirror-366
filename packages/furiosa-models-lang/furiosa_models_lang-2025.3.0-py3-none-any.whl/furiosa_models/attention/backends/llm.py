from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type

import torch

from furiosa_models.attention.backends.base import (
    AttentionBackendBase,
    AttentionImplBase,
    AttentionMetadataBase,
    AttentionType,
)
from furiosa_models.attention.backends.common import PagedAttentionMetadata
from furiosa_models.attention.ops.paged_attention import PagedAttention


class LLMAttentionBackend(AttentionBackendBase):
    """Backend for LLM-specific attention operations.

    This backend integrates the `PagedAttention` mechanism for managing KV caches
    and optimizing attention computations in large language models (LLMs).
    """

    DEFAULT_BLOCK_SIZE = 1

    @property
    def name(self) -> str:
        """Return the name of the backend."""
        return "LLM_ATTENTION"

    @property
    def impl(self) -> Type["LLMAttentionImpl"]:
        """Return the implementation class (`LLMAttentionImpl`)."""
        return LLMAttentionImpl

    @property
    def metadata(self) -> Type["LLMAttentionMetadata"]:
        """Return the metadata class (`LLMAttentionMetadata`)."""
        return LLMAttentionMetadata

    @staticmethod
    def get_kv_cache_shape(
        batch_size: int,
        max_seq_len: int,
        block_size: int,
        num_kv_heads: int,
        head_size: int,
    ) -> Tuple[int, ...]:
        """Compute the shape of the KV cache.

        Args:
            batch_size (int): Number of sequences in a batch.
            max_seq_len (int): Maximum sequence length.
            block_size (int): Tokens per block.
            num_kv_heads (int): Number of KV heads.
            head_size (int): Size of each attention head.

        Returns:
            Tuple[int, ...]: KV cache shape.

        Raises:
            NotImplementedError: If block size > 1.
        """
        if block_size != LLMAttentionBackend.DEFAULT_BLOCK_SIZE:
            raise NotImplementedError("Block size > 1 is not supported.")

        return PagedAttention.get_kv_cache_shape(
            batch_size, max_seq_len, block_size, num_kv_heads, head_size
        )


@dataclass
class LLMAttentionMetadata(PagedAttentionMetadata):
    """Metadata structure for LLM-specific attention operations.

    This class manages the mapping of key-value (KV) cache blocks during
    prefill and decoding phases.
    """

    block_size: int = LLMAttentionBackend.DEFAULT_BLOCK_SIZE

    def __post_init__(self) -> None:
        """Post-initialization for LLMAttentionMetadata.

        Raises:
            NotImplementedError: If block size > 1.
        """
        if self.block_size != LLMAttentionBackend.DEFAULT_BLOCK_SIZE:
            raise NotImplementedError("Block size > 1 is not supported.")

        super().__post_init__()

    @staticmethod
    def _compute_write_block_mapping(
        seq_len: int, block_size: int, batch_size: int, past_seq_len: int = 0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute key and value block indices for writing to the KV cache.

        This function determines where new keys/values should be stored in the KV cache.

        Args:
            seq_len (int): Number of new tokens to allocate.
            block_size (int): Number of tokens per cache block.
            batch_size (int): Number of sequences in the batch.
            past_seq_len (int, optional): Number of previously stored tokens.
                Defaults to 0.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Tuple of key and value block indices.

        Raises:
            NotImplementedError: If block size > 1.
        """
        if block_size != LLMAttentionBackend.DEFAULT_BLOCK_SIZE:
            raise NotImplementedError("Block size > 1 is not supported.")

        # TODO: Optimize key/value block indexing
        # Currently, key and value block indices are duplicated by cloning `key_block_indices`.
        key_block_indices, _ = PagedAttentionMetadata._compute_write_block_mapping(
            seq_len, block_size, batch_size, past_seq_len
        )
        value_block_indices = key_block_indices.clone()

        return key_block_indices, value_block_indices

    def __repr__(self) -> str:
        """Return a formatted string representation of the metadata."""
        write_repr = (self.write_block_mapping[0].tolist(), self.write_block_mapping[1].tolist())
        load_repr = (
            (self.load_block_mapping[0].tolist(), self.load_block_mapping[1].tolist())
            if self.load_block_mapping
            else None
        )
        return (
            f"LLMAttentionMetadata(prefill={self.load_block_mapping is None}, "
            f"write_block_mapping={write_repr}, "
            f"load_block_mapping={load_repr})"
        )


class LLMAttentionImpl(AttentionImplBase):
    """Implementation of LLM-specific attention using `PagedAttention`.

    This class manages KV cache operations and computes scaled dot-product attention.

    Args:
        num_heads (int): Number of attention heads.
        head_size (int): Size of each attention head.
        scale (float): Scaling factor for dot-product attention.
        num_kv_heads (int): Number of KV heads.
        alibi_slopes (Optional[List[float]]): Slopes for ALiBi attention.
        sliding_window (Optional[int]): Window size for local attention.
        blocksparse_params (Optional[Dict[str, Any]]): Parameters for block-sparse attention.
        logits_soft_cap (Optional[float]): Soft cap for attention logits.
        kv_cache_dtype (torch.dtype): KV cache data type (`"auto"` by default).
        attn_type (AttentionType): Type of attention (default: `"decoder"`).

    Raises:
        ValueError: If `num_heads` is not divisible by `num_kv_heads`.
        NotImplementedError: If ALiBi, sliding window, or block-sparse attention is used.
    """

    def __init__(
        self,
        num_heads: int,
        head_size: int,
        scale: float,
        num_kv_heads: int,
        alibi_slopes: Optional[List[float]] = None,
        sliding_window: Optional[int] = None,
        blocksparse_params: Optional[Dict[str, Any]] = None,
        logits_soft_cap: Optional[float] = None,
        kv_cache_dtype: torch.dtype = torch.float32,
        attn_type: AttentionType = AttentionType.DECODER,
    ) -> None:
        num_kv_heads = num_kv_heads or num_heads
        if num_heads % num_kv_heads != 0:
            raise ValueError(
                f"Number of heads ({num_heads}) must be divisible by number of "
                f"KV heads ({num_kv_heads})."
            )

        if kv_cache_dtype not in [torch.float32, torch.float16, torch.bfloat16]:
            raise ValueError(
                f"Invalid KV cache data type: {kv_cache_dtype}. "
                f"Supported types are torch.float32, torch.float16, torch.bfloat16"
            )

        if attn_type != AttentionType.DECODER:
            raise NotImplementedError(f"Attention type '{attn_type}' is not yet supported.")

        if alibi_slopes is not None:
            raise NotImplementedError("ALiBi attention is not yet supported.")
        if sliding_window is not None:
            raise NotImplementedError("Sliding window attention is not yet supported.")
        if blocksparse_params is not None:
            raise NotImplementedError("Block-sparse attention is not yet supported.")
        if logits_soft_cap is not None:
            raise NotImplementedError("Soft cap for attention logits is not yet supported.")

        super().__init__(
            num_heads=num_heads,
            head_size=head_size,
            scale=scale,
            num_kv_heads=num_kv_heads,
            alibi_slopes=alibi_slopes,
            sliding_window=sliding_window,
            blocksparse_params=blocksparse_params,
            logits_soft_cap=logits_soft_cap,
            kv_cache_dtype=kv_cache_dtype,
            attn_type=attn_type,
        )

        self.attn_op: Type[PagedAttention] = PagedAttention

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: Tuple[torch.Tensor, torch.Tensor],
        attn_metadata: AttentionMetadataBase,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Perform the forward pass of attention using `PagedAttention`.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, seq_len, num_heads * head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            kv_cache (Tuple[torch.Tensor, torch.Tensor]): Tuple of key and value caches of shape
                `(num_blocks, block_size, num_kv_heads, head_size)` for each.
            attn_metadata (AttentionMetadataBase): Metadata for KV cache management.
            attn_mask (Optional[torch.Tensor]): Attention mask tensor of shape
                `(batch_size, seq_len, seq_len)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, seq_len, num_heads * head_size)`.

        Raises:
            TypeError: If metadata is not an instance of `LLMAttentionMetadata`.
            ValueError: If query, key, or value tensors have incorrect shapes.
            NotImplementedError: If block size > 1.
            RuntimeError: If attention mask is required but not provided.
        """
        if type(attn_metadata) is not LLMAttentionMetadata:
            raise TypeError(
                f"Metadata must be exactly `LLMAttentionMetadata`, got {type(attn_metadata)}."
            )

        if query.ndim != 3:
            raise ValueError(
                f"Query tensor must have shape (batch_size, seq_len, num_heads * head_size). "
                f"Got {query.shape}."
            )
        if key.ndim != 3:
            raise ValueError(
                f"Key tensor must have shape (batch_size, seq_len, num_kv_heads * head_size). "
                f"Got {key.shape}."
            )
        if value.ndim != 3:
            raise ValueError(
                f"Value tensor must have shape (batch_size, seq_len, num_kv_heads * head_size). "
                f"Got {value.shape}."
            )

        batch_size, q_len = query.shape[:2]
        batch_size, kv_len = key.shape[:2]

        if key.shape != value.shape:
            raise ValueError(
                f"Key and value tensors must have the same shape. "
                f"Got {key.shape} and {value.shape}."
            )

        # Reshape query, key, value tensors to separate head dimensions
        query = query.view(batch_size, q_len, self.num_heads, self.head_size)
        key = key.view(batch_size, kv_len, self.num_kv_heads, self.head_size)
        value = value.view(batch_size, kv_len, self.num_kv_heads, self.head_size)

        # Unpack KV cache into key and value tensors
        key_cache, value_cache = kv_cache
        assert key_cache.shape == value_cache.shape, "Key and value cache must have the same shape."

        # Validate KV cache capacity
        num_blocks, block_size = key_cache.shape[0], key_cache.shape[1]
        if block_size != LLMAttentionBackend.DEFAULT_BLOCK_SIZE:
            raise NotImplementedError("Block size > 1 is not supported.")

        if num_blocks * block_size < q_len:
            raise ValueError(
                f"KV cache too small: total capacity {num_blocks * block_size} "
                f"< query length {q_len}."
            )

        # Reshape query, key, value tensors to separate head dimensions
        query = query.view(batch_size, q_len, self.num_heads, self.head_size)
        key = key.view(batch_size, kv_len, self.num_kv_heads, self.head_size)
        value = value.view(batch_size, kv_len, self.num_kv_heads, self.head_size)

        # Unbind KV cache into key and value tensors
        key_cache, value_cache = kv_cache

        is_prefill = attn_metadata.load_block_mapping is None
        # Load KV cache if in decode mode
        if not is_prefill:
            assert attn_metadata.load_block_mapping is not None, (
                "Load block mapping is required for decode mode."
            )
            loaded_key = self.attn_op.load_from_paged_cache(
                cache_tensor=key_cache,
                block_indices=attn_metadata.load_block_mapping[0],
                target_shape=(batch_size, -1, self.num_kv_heads, self.head_size),
            )
            loaded_value = self.attn_op.load_from_paged_cache(
                cache_tensor=value_cache,
                block_indices=attn_metadata.load_block_mapping[1],
                target_shape=(batch_size, -1, self.num_kv_heads, self.head_size),
            )

        # Write key and value to KV cache
        self.attn_op.write_to_paged_cache(
            input_tensor=key,
            cache_tensor=key_cache,
            # flatten as (batch_size * seq_len)
            block_indices=attn_metadata.write_block_mapping[0].flatten(0),
        )
        self.attn_op.write_to_paged_cache(
            input_tensor=value,
            cache_tensor=value_cache,
            # flatten as (batch_size * seq_len)
            block_indices=attn_metadata.write_block_mapping[1].flatten(0),
        )

        if not is_prefill:
            key = torch.concat([loaded_key, key], dim=1)
            value = torch.concat([loaded_value, value], dim=1)

        # Compute attention
        use_causal_mask = is_prefill and attn_mask is None
        if use_causal_mask and len(set(attn_metadata.prefill_seq_lens)) > 1:
            raise RuntimeError(
                "Attention mask is required when batch contains sequences of different lengths.\n"
                f"Received sequence lengths: {attn_metadata.prefill_seq_lens}\n"
                "Provide an explicit `attn_mask` to ensure correct attention behavior."
            )
        attn_output = self.attn_op.forward(
            query,
            key,
            value,
            self.scale,
            attn_mask=attn_mask,
            is_causal=use_causal_mask,
            enable_gqa=self.num_heads != self.num_kv_heads,
            mask_value=torch.finfo(torch.bfloat16).min,
        )

        # Reshape back to `(batch_size, seq_len, num_heads * head_size)`
        return attn_output.reshape(batch_size, q_len, self.num_heads * self.head_size)
