from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import torch


class AttentionType(Enum):
    """Enumeration of different attention types used in transformer models.

    This enum provides well-defined constants to specify different attention mechanisms,
    improving type safety and readability.

    Attributes:
        DECODER: Decoder self-attention, where queries attend to previous positions.
        ENCODER: Encoder self-attention for processing input sequences.
        ENCODER_ONLY: Encoder-only self-attention, used in models like BERT.
        ENCODER_DECODER: Cross-attention, where decoder queries attend to encoder outputs.
    """

    DECODER = "decoder"
    ENCODER = "encoder"
    ENCODER_ONLY = "encoder_only"
    ENCODER_DECODER = "encoder_decoder"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


@dataclass
class AttentionMetadataBase(ABC):
    """Base class for managing metadata related to attention mechanisms.

    This class provides an abstract interface for handling key-value (KV) cache mappings,
    distinguishing between prefill and decode stages in attention computation.
    """

    @abstractmethod
    def update(self, seq_len: int, past_seq_len: Optional[int] = None) -> None:
        """Updates the metadata structure with new information.

        This method modifies existing metadata to accommodate changes in KV cache mappings
        as attention computation progresses.

        Args:
            seq_len (int): Number of tokens in the current attention step.
            past_seq_len (Optional[int]): Number of tokens processed in previous attention steps.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("`update()` method must be implemented in derived classes.")


class AttentionBackendBase(ABC):
    """Abstract base class for defining attention backends.

    An attention backend provides a framework-specific implementation of attention
    mechanisms, including KV cache management and metadata handling.

    Properties:
        name (str): Name of the attention backend.
        impl (AttentionImplBase): Implementation class for the backend.
        metadata (AttentionMetadataBase): Metadata structure for the backend.
    """

    DEFAULT_BLOCK_SIZE: Optional[int] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the attention backend."""
        pass

    @property
    @abstractmethod
    def impl(self) -> Type["AttentionImplBase"]:
        """Return the implementation class for the backend."""
        pass

    @property
    @abstractmethod
    def metadata(self) -> Type["AttentionMetadataBase"]:
        """Return the metadata structure for the backend."""
        pass

    @staticmethod
    @abstractmethod
    def get_kv_cache_shape(
        batch_size: int,
        max_seq_len: int,
        block_size: int,
        num_kv_heads: int,
        head_size: int,
    ) -> Tuple[int, ...]:
        """Compute the shape of the key-value cache.

        Args:
            batch_size (int): Number of sequences in a batch.
            max_seq_len (int): Maximum sequence length.
            block_size (int): Number of slots per block.
            num_kv_heads (int): Number of key-value heads.
            head_size (int): Size of each attention head.


        Returns:
            Tuple[int, ...]: Shape of the key-value cache tensor.
        """
        pass


class AttentionImplBase(ABC):
    """Abstract base class for implementing specific attention mechanisms.

    This class provides an interface for custom attention implementations,
    including initialization and forward computation.

    Args:
        num_heads (int): Number of attention heads.
        head_size (int): Dimensionality of each attention head.
        scale (float): Scaling factor for attention logits, often `1 / sqrt(head_size)`.
        num_kv_heads (int): Number of key-value heads, which may differ from `num_heads`
            in architectures like grouped-query attention.
        alibi_slopes (Optional[List[float]]): List of slopes for ALiBi attention (optional).
        sliding_window (Optional[int]): Window size for local attention (optional).
        blocksparse_params (Optional[Dict[str, Any]]): Parameters for block-sparse attention
            (optional).
        logits_soft_cap (Optional[float]): Soft cap for logits to prevent extreme values
            (optional).
        kv_cache_dtype (Union[str, torch.dtype]): Data type for the KV cache (`"auto"` by default).
        attn_type (AttentionType): Type of attention mechanism (`"decoder"`, `"encoder"`, etc.).
    """

    @abstractmethod
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
        kv_cache_dtype: Union[str, torch.dtype] = "auto",
        attn_type: AttentionType = AttentionType.DECODER,
    ) -> None:
        self.num_heads = num_heads
        self.head_size = head_size
        self.scale = float(scale)
        self.num_kv_heads = num_kv_heads
        self.kv_cache_dtype = kv_cache_dtype
        self.alibi_slopes = alibi_slopes
        self.sliding_window = sliding_window
        self.blocksparse_params = blocksparse_params
        self.logits_soft_cap = logits_soft_cap
        self.attn_type = attn_type

    @abstractmethod
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        kv_cache: Tuple[torch.Tensor, torch.Tensor],
        attn_metadata: AttentionMetadataBase,
        attn_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Perform the forward pass of attention.

        This function computes the attention output using the provided query, key, and value
        tensors.
        If the KV cache is used, it loads and writes values based on the provided metadata.

        Args:
            query (torch.Tensor): Query tensor of shape
                `(batch_size, seq_len, num_heads * head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            value (torch.Tensor): Value tensor of shape
                `(batch_size, seq_len, num_kv_heads * head_size)`.
            kv_cache (Tuple[torch.Tensor, torch.Tensor]): Tuple of key and value caches of shape
                `(num_blocks, block_size, num_kv_heads, head_size)` for each.
            attn_metadata (AttentionMetadataBase): Metadata structure containing KV cache mappings.
            attn_mask (Optional[torch.Tensor]): Attention mask tensor of shape
                `(batch_size, seq_len, seq_len)`.

        Returns:
            torch.Tensor: Attention output tensor of shape
                `(batch_size, seq_len, num_heads * head_size)`.
        """
        pass
