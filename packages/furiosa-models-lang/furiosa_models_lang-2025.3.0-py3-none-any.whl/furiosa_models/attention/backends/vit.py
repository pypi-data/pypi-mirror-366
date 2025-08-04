from typing import Callable, Optional, Tuple, Type

import torch

from furiosa_models.attention.backends.base import (
    AttentionBackendBase,
    AttentionImplBase,
    AttentionMetadataBase,
    AttentionType,
)
from furiosa_models.attention.ops.scaled_dot_product import scaled_dot_product_attention


class ViTAttentionBackend(AttentionBackendBase):
    """Backend for Vision Transformer (ViT) attention operations."""

    @property
    def name(self) -> str:
        """Return the name of the backend."""
        return "VIT_ATTENTION"

    @property
    def impl(self) -> Type["ViTAttentionImpl"]:
        """Return the implementation class (`ViTAttentionImpl`)."""
        return ViTAttentionImpl

    @property
    def metadata(self) -> Type["AttentionMetadataBase"]:
        """Return the metadata class (`ViTAttentionMetadata`)."""
        raise NotImplementedError("ViTAttentionBackend does not support metadata.")

    @staticmethod
    def get_kv_cache_shape(
        batch_size: int, max_seq_len: int, block_size: int, num_kv_heads: int, head_size: int
    ) -> Tuple[int, ...]:
        """Compute the shape of the KV cache."""
        raise NotImplementedError(
            "ViTAttentionBackend does not support KV cache shape computation."
        )


class ViTAttentionImpl(AttentionImplBase):
    """Implementation of ViT-specific attention.

    Args:
        num_heads (int): Number of attention heads.
        head_size (int): Size of each attention head.
        scale (float): Scaling factor for dot-product attention.
        num_kv_heads (Optional[int]): Number of KV heads.
        attn_type (AttentionType): Type of attention (default: `"encoder only"`).

    Raises:
        ValueError: If `num_heads` is not divisible by `num_kv_heads`, or if `attn_type` is not
            `"encoder only"`.
        NotImplementedError: If `attn_type` is not supported.
    """

    def __init__(
        self,
        num_heads: int,
        head_size: int,
        scale: float,
        num_kv_heads: Optional[int] = None,
        attn_type: AttentionType = AttentionType.ENCODER_ONLY,
    ) -> None:
        num_kv_heads = num_kv_heads or num_heads
        if num_heads % num_kv_heads != 0:
            raise ValueError(
                f"Number of heads ({num_heads}) must be divisible by number of "
                f"KV heads ({num_kv_heads})."
            )

        if attn_type != AttentionType.ENCODER_ONLY:
            raise NotImplementedError(f"Attention type '{attn_type}' is not supported.")

        super().__init__(
            num_heads=num_heads,
            head_size=head_size,
            scale=scale,
            num_kv_heads=num_kv_heads,
            attn_type=attn_type,
        )

        self.attn_op: Callable[..., torch.Tensor] = scaled_dot_product_attention

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
        attn_metadata: Optional[AttentionMetadataBase] = None,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Perform the forward pass of attention using scaled dot product attention.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, num_patches, num_heads, head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, num_patches, num_kv_heads, head_size)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, num_patches, num_kv_heads, head_size)`.
            kv_cache (Optional[Tuple[torch.Tensor, torch.Tensor]], optional): List of KV caches.
                Each cache is a tuple of key and value tensors of shape
                `(num_blocks, block_size, num_kv_heads, head_size)`.
            attn_metadata (Optional[AttentionMetadataBase], optional): Metadata structure
                containing KV cache mappings.
            attn_mask (Optional[torch.Tensor], optional): Attention mask tensor of shape
                `(batch_size, num_patches, num_patches)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, num_patches, num_heads, head_size)`.

        Raises:
            ValueError: If query, key, or value tensors have incorrect shapes.

        """
        _ = kv_cache
        _ = attn_metadata
        _ = attn_mask
        if query.ndim != 4:
            raise ValueError(
                f"Query tensor must have shape (batch_size, num_patches, num_heads, head_size). "
                f"Got {query.shape}."
            )
        if key.ndim != 4:
            raise ValueError(
                f"Key tensor must have shape (batch_size, num_patches, num_kv_heads, head_size). "
                f"Got {key.shape}."
            )
        if value.ndim != 4:
            raise ValueError(
                f"Value tensor must have shape (batch_size, num_patches, num_kv_heads, head_size). "  # noqa: E501
                f"Got {value.shape}."
            )

        if key.shape != value.shape:
            raise ValueError(
                f"Key and value tensors must have the same shape. "
                f"Got {key.shape} and {value.shape}."
            )

        # Compute attention
        query = query.permute(0, 2, 1, 3)
        key = key.permute(0, 2, 1, 3)
        value = value.permute(0, 2, 1, 3)

        attn_output = self.attn_op(
            query,
            key,
            value,
            scale=self.scale,
            enable_gqa=self.num_heads != self.num_kv_heads,
        )

        attn_output = attn_output.permute(0, 2, 1, 3)

        # Reshape back to `(batch_size, seq_len, num_heads, head_size)`
        return attn_output.contiguous()
