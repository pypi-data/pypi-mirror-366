from typing import Any, Dict, List, Optional, Tuple

import torch
import torch.nn as nn

from furiosa_models.attention.backends.base import (
    AttentionBackendBase,
    AttentionImplBase,
    AttentionMetadataBase,
    AttentionType,
)
from furiosa_models.attention.backends.llm import LLMAttentionBackend
from furiosa_models.attention.backends.vit import ViTAttentionBackend
from furiosa_models.config import CacheConfig, QuantizationConfig


class AttentionLayer(nn.Module):
    """General interface for attention mechanisms in Transformer-based models.

    This class implements a flexible attention mechanism that supports various
    Transformer-based architectures, including:
      - Large Language Models (LLMs) (e.g., GPT, LLaMA)
      - Encoder-Only models (e.g., BERT, RoBERTa)
      - Encoder-Decoder models (e.g., T5, BART)
      - Multi-modal architectures with cross-modal attention mechanisms
        (planned, not yet fully implemented).

    This interface utilizes a customizable `AttentionBackend`, allowing the application of
    attention mechanisms across different tasks and architectures.

    Args:
        num_heads (int): Number of attention heads.
        head_size (int): Dimensionality of each attention head.
        scale (float): Scaling factor for dot-product attention.
        num_kv_heads (Optional[int]): Number of key-value heads. Defaults to `num_heads`.
        cache_config (Optional[CacheConfig]): Configuration for key-value (KV) cache.
        quant_config (Optional[QuantizationConfig]): Configuration for quantization.
        alibi_slopes (Optional[List[float]]): ALiBi positional bias slopes (not implemented).
        blocksparse_params (Optional[Dict[str, Any]]): Block-sparse attention parameters
            (not implemented).
        logits_soft_cap (Optional[float]): Logit value cap (not implemented).
        per_layer_sliding_window (Optional[int]): Sliding window size for specific layers
            (not implemented).
        prefix (str): Optional prefix for identifying the layer.
        attn_type (AttentionType): Type of attention (e.g., "decoder").

    Raises:
        NotImplementedError: If an unsupported feature (e.g., ALiBi, block-sparse attention) is
            provided.
        ValueError: If the block size is not explicitly defined in `CacheConfig`, or mismatched
            with the backend's default block size.
    """

    def __init__(
        self,
        num_heads: int,
        head_size: int,
        scale: float,
        num_kv_heads: Optional[int] = None,
        cache_config: Optional[CacheConfig] = None,
        quant_config: Optional[QuantizationConfig] = None,
        alibi_slopes: Optional[List[float]] = None,
        blocksparse_params: Optional[Dict[str, Any]] = None,
        logits_soft_cap: Optional[float] = None,
        per_layer_sliding_window: Optional[int] = None,
        prefix: str = "",
        attn_type: AttentionType = AttentionType.DECODER,
    ) -> None:
        super().__init__()

        if alibi_slopes is not None:
            raise NotImplementedError("ALiBi slopes are not implemented yet.")
        if blocksparse_params is not None:
            raise NotImplementedError("Block-sparse attention is not implemented yet.")
        if logits_soft_cap is not None:
            raise NotImplementedError("Logits soft cap is not implemented yet.")
        if per_layer_sliding_window is not None:
            raise NotImplementedError("Per-layer sliding window is not implemented yet.")

        self.kv_cache_dtype = (
            cache_config.cache_dtype if cache_config else torch.get_default_dtype()
        )
        self.num_heads = num_heads
        self.head_size = head_size
        self.num_kv_heads = num_kv_heads or num_heads
        self.attn_type = attn_type
        self.layer_name = prefix

        if attn_type != AttentionType.DECODER:
            raise NotImplementedError(f"Unsupported attention type: {attn_type}")

        self.attn_backend: AttentionBackendBase = self.select_backend(
            alibi_slopes=alibi_slopes,
            blocksparse_params=blocksparse_params,
            logits_soft_cap=logits_soft_cap,
            cache_config=cache_config,
            quant_config=quant_config,
        )

        if isinstance(cache_config, CacheConfig):
            # If the backend enforces `DEFAULT_BLOCK_SIZE`, it must match the `CacheConfig`
            if self.attn_backend.DEFAULT_BLOCK_SIZE is not None:
                if cache_config.block_size != self.attn_backend.DEFAULT_BLOCK_SIZE:
                    raise ValueError(
                        f"[{self.attn_backend.__class__.__name__}] Block size mismatch: "
                        f"Backend enforces {self.attn_backend.DEFAULT_BLOCK_SIZE}, but received "
                        f"{cache_config.block_size} from `CacheConfig`."
                    )
            self.block_size = cache_config.block_size
        else:
            # If `DEFAULT_BLOCK_SIZE` is not set, the user must explicitly define it in
            # `CacheConfig`
            if self.attn_backend.DEFAULT_BLOCK_SIZE is not None:
                self.block_size = self.attn_backend.DEFAULT_BLOCK_SIZE
            else:
                raise ValueError(
                    f"[{self.attn_backend.__class__.__name__}] Block size must be explicitly "
                    "defined in `CacheConfig`. "
                    f"This backend does not provide a default block size."
                )

        self.backend = self.attn_backend.name
        self.impl: AttentionImplBase = self.attn_backend.impl(
            num_heads=self.num_heads,
            head_size=self.head_size,
            scale=scale,
            num_kv_heads=self.num_kv_heads,
            alibi_slopes=alibi_slopes,
            sliding_window=per_layer_sliding_window,
            kv_cache_dtype=self.kv_cache_dtype,
            blocksparse_params=blocksparse_params,
            logits_soft_cap=logits_soft_cap,
            attn_type=self.attn_type,
        )

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: Tuple[torch.Tensor, torch.Tensor],
        attn_metadata: "AttentionMetadataBase",
        attn_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Computes the forward pass of the attention layer.

        This method validates input tensors and invokes the backend implementation
        for actual attention computation.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, seq_len, num_heads * head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            kv_cache (Tuple[torch.Tensor, torch.Tensor]): Tuple of key and value caches of shape
                `(num_blocks, block_size, num_kv_heads, head_size)` for each.
            attn_metadata (AttentionMetadataBase): Metadata for KV cache and computation settings.
            attn_mask (Optional[torch.Tensor]): Attention mask tensor of shape
                `(batch_size, seq_len, seq_len)`.

        Returns:
            torch.Tensor: Output tensor of shape `(seq_len, num_heads * head_size)`.
        """
        return self.impl.forward(
            query,
            key,
            value,
            kv_cache,
            attn_metadata,
            attn_mask,
        )

    def select_backend(
        self,
        alibi_slopes: Optional[List[float]] = None,
        blocksparse_params: Optional[Dict[str, Any]] = None,
        logits_soft_cap: Optional[float] = None,
        cache_config: Optional[CacheConfig] = None,
        quant_config: Optional[QuantizationConfig] = None,
    ) -> AttentionBackendBase:
        """Selects the appropriate attention backend based on configuration parameters.

        Args:
            alibi_slopes (Optional[List[float]]): ALiBi positional bias slopes.
            blocksparse_params (Optional[Dict[str, Any]]): Block-sparse attention parameters.
            logits_soft_cap (Optional[float]): Logits soft cap value.
            cache_config (Optional[CacheConfig]): KV cache configuration.
            quant_config (Optional[QuantizationConfig]): Quantization configuration.

        Returns:
            AttentionBackendBase: The selected backend instance.

        Raises:
            NotImplementedError: If quant_config is provided.
        """
        _ = alibi_slopes
        _ = blocksparse_params
        _ = logits_soft_cap
        _ = cache_config

        if quant_config is not None:
            raise NotImplementedError("Quantization is not yet supported for AttentionLayer.")

        # TODO: Implement backend selection based on configuration parameters.
        return LLMAttentionBackend()

    def extra_repr(self) -> str:
        """Returns the extra representation string for the attention layer."""
        return (
            f"AttnBackend={self.attn_backend.name}, "
            f"num_heads={self.num_heads}, "
            f"num_kv_heads={self.num_kv_heads}, "
            f"head_size={self.head_size}"
        )


class VisionAttentionLayer(nn.Module):
    """General interface for attention mechanisms in Vision Transformer-based models.

    Args:
        num_heads (int): Number of attention heads.
        head_size (int): Dimensionality of each attention head.
        scale (float): Scaling factor for dot-product attention.
        num_kv_heads (Optional[int]): Number of key-value heads. Defaults to `num_heads`.
        quant_config (Optional[QuantizationConfig]): Configuration for quantization.
        prefix (str): Optional prefix for identifying the layer.
        attn_type (AttentionType): Type of attention (e.g., "encoder only").

    Raises:
        NotImplementedError: If unsupported attentino type is provided.
    """

    def __init__(
        self,
        num_heads: int,
        head_size: int,
        scale: float,
        num_kv_heads: Optional[int] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
        attn_type: AttentionType = AttentionType.ENCODER_ONLY,
    ) -> None:
        super().__init__()
        self.num_heads = num_heads
        self.head_size = head_size
        self.num_kv_heads = num_kv_heads or num_heads
        self.attn_type = attn_type
        self.layer_name = prefix

        if attn_type != AttentionType.ENCODER_ONLY:
            raise NotImplementedError(f"Unsupported attention type: {attn_type}")

        self.attn_backend: AttentionBackendBase = self.select_backend(
            quant_config=quant_config,
        )

        self.backend = self.attn_backend.name
        self.impl: AttentionImplBase = self.attn_backend.impl(
            num_heads=self.num_heads,
            head_size=self.head_size,
            scale=scale,
            num_kv_heads=self.num_kv_heads,
            attn_type=self.attn_type,
        )

    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
    ) -> torch.Tensor:
        """Computes the forward pass of the attention layer.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, num_patches, num_heads * head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, num_patches, num_kv_heads * head_size)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, num_patches, num_kv_heads * head_size)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, num_patches, num_heads * head_size)`.
        """
        return self.impl.forward(
            query,
            key,
            value,
            None,  # type: ignore[arg-type] # TODO: This is a design mistake in the backend interface
            None,  # type: ignore[arg-type] # TODO: This is a design mistake in the backend interface
        )

    def select_backend(
        self,
        quant_config: Optional[QuantizationConfig] = None,
    ) -> AttentionBackendBase:
        """Selects the appropriate attention backend based on configuration parameters.

        Args:
            quant_config (Optional[QuantizationConfig]): Quantization configuration.

        Returns:
            AttentionBackendBase: The selected backend instance.

        Raises:
            NotImplementedError: If quant_config is provided.
        """
        if quant_config is not None:
            raise NotImplementedError("Quantization is not yet supported for AttentionLayer.")

        # TODO: Implement backend selection based on configuration parameters.
        return ViTAttentionBackend()

    def extra_repr(self) -> str:
        """Returns the extra representation string for the attention layer."""
        return (
            f"AttnBackend={self.attn_backend.name}, "
            f"num_heads={self.num_heads}, "
            f"num_kv_heads={self.num_kv_heads}, "
            f"head_size={self.head_size}"
        )
