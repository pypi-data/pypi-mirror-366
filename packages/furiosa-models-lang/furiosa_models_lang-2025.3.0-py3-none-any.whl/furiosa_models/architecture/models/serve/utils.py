from contextlib import contextmanager
from typing import Generator, List, Optional, Tuple

import torch
from transformers import PretrainedConfig

from furiosa_models.architecture.models.serve.specs import CausalModelDims
from furiosa_models.attention.backends.llm import LLMAttentionBackend, LLMAttentionMetadata


@contextmanager
def set_default_dtype(dtype: torch.dtype) -> Generator[None, None, None]:
    """Set the torch default dtype within a context.

    Args:
        dtype (torch.dtype): The temporary dtype to set.

    Yields:
        None: A context manager that sets the default dtype.

    Usage:
        with set_default_dtype(torch.bfloat16):
            model = MyModel()
    """
    original_dtype = torch.get_default_dtype()
    try:
        torch.set_default_dtype(dtype)
        yield
    finally:
        torch.set_default_dtype(original_dtype)


class CausalModelUtils:
    """Essential utility functions for causal language model export."""

    @classmethod
    def get_attention_backend(cls) -> LLMAttentionBackend:
        """Get the attention backend from CausalModelServe."""
        from furiosa_models.architecture.models.serve.causal import CausalModelServer

        assert isinstance(CausalModelServer.attention_backend, LLMAttentionBackend), (
            "Attention backend should be LLMAttentionBackend"
        )
        return CausalModelServer.attention_backend

    @staticmethod
    def create_input_ids(
        batch_size: int,
        seq_len: int,
        dtype: torch.dtype = torch.int32,
    ) -> torch.Tensor:
        """Create input IDs for causal language model.

        Args:
            batch_size (int): Batch size for the model.
            seq_len (int): Sequence length for the model.
            dtype (torch.dtype): Data type for the input IDs.

        Returns:
            torch.Tensor: Input IDs tensor of shape (batch_size, seq_len).
        """
        return torch.randint(low=0, high=128, size=(batch_size, seq_len), dtype=dtype)

    @staticmethod
    def create_position_ids(
        batch_size: int,
        seq_len: int,
        dtype: torch.dtype = torch.int32,
    ) -> torch.Tensor:
        """Create position IDs for causal language  model.

        Args:
            batch_size (int): Batch size for the model.
            seq_len (int): Sequence length for the model.
            dtype (torch.dtype): Data type for the position IDs.

        Returns:
            torch.Tensor: Position IDs tensor of shape (batch_size, seq_len).
        """
        return torch.arange(seq_len, dtype=dtype).expand(batch_size, -1)

    @staticmethod
    def create_attention_metadata(
        batch_size: int,
        prefill_seq_len: Optional[int] = None,
        max_seq_len: Optional[int] = None,
        past_seq_len: Optional[int] = None,
        decode_seq_len: Optional[int] = None,
        block_size: int = 1,
        is_prefill: bool = True,
    ) -> LLMAttentionMetadata:
        """Create attention metadata for causal language model.

        Args:
            batch_size (int): Batch size for the model.
            prefill_seq_len (Optional[int]): Sequence length for prefill mode.
            max_seq_len (Optional[int]): Maximum sequence length for the model.
            past_seq_len (Optional[int]): Past sequence length for decode mode.
            decode_seq_len (Optional[int]): Sequence length for decode mode.
            block_size (int): Block size for paged attention.
            is_prefill (bool): Whether to use prefill mode.

        Returns:
            LLMAttentionMetadata: Attention metadata for the model.
        """
        attention_backend = CausalModelUtils.get_attention_backend()
        if is_prefill:
            assert prefill_seq_len is not None, "prefill_seq_len must be provided for prefill mode"
            attention_metadata: LLMAttentionMetadata = attention_backend.metadata(
                prefill_seq_lens=[prefill_seq_len] * batch_size,
                block_size=block_size,
                max_seq_len=max_seq_len,
            )
        else:
            assert past_seq_len is not None, "past_seq_len must be provided for non-prefill mode"
            assert decode_seq_len is not None, (
                "decode_seq_len must be provided for non-prefill mode"
            )
            attention_metadata = attention_backend.metadata(
                prefill_seq_lens=[past_seq_len] * batch_size,
                block_size=block_size,
                max_seq_len=max_seq_len,
            )
            attention_metadata.update(seq_len=decode_seq_len, past_seq_len=past_seq_len)

        return attention_metadata

    @staticmethod
    def create_attention_masks(
        batch_size: int,
        seq_len: int,
        kv_len: Optional[int] = None,
        dtype: torch.dtype = torch.bool,
    ) -> torch.Tensor:
        """Create attention masks for causal language model.

        Args:
            batch_size (int): Batch size for the model.
            seq_len (int): Sequence length(query_len) for the model.
            kv_len (Optional[int]): Key Value length for the model.
            dtype (torch.dtype): Data type for the attention masks.

        Returns:
            torch.Tensor: Attention masks tensor of shape (batch_size, seq_len, seq_len).
        """
        # seq_len is always equal to kv_len for causal language model
        kv_len = kv_len or seq_len
        return torch.ones((batch_size, seq_len, kv_len), dtype=dtype)

    @staticmethod
    def create_kv_caches(
        batch_size: int,
        max_seq_len: int,
        num_layers: int,
        num_kv_heads: int,
        head_dim: int,
        block_size: int = 1,
        num_blocks: Optional[int] = None,
        dtype: torch.dtype = torch.bfloat16,
    ) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """Create KV caches for causal language model.

        Args:
            batch_size (int): Batch size for the model.
            max_seq_len (int): Maximum sequence length for the model.
            num_layers (int): Number of layers in the model.
            num_kv_heads (int): Number of key-value heads in the model.
            head_dim (int): Dimension of each head in the model.
            block_size (int): Block size for paged attention.
            num_blocks (Optional[int]): Number of blocks for paged attention.
            dtype (torch.dtype): Data type for the KV caches.

        Returns:
            List[Tuple[torch.Tensor, torch.Tensor]]: List of KV caches for each layer.
        """
        attention_backend = CausalModelUtils.get_attention_backend()
        kv_cache_shape = attention_backend.get_kv_cache_shape(
            batch_size=batch_size,
            block_size=block_size,
            num_kv_heads=num_kv_heads,
            head_size=head_dim,
            max_seq_len=max_seq_len,
        )
        if num_blocks is not None:
            kv_cache_shape = (num_blocks, *kv_cache_shape[1:])
        kv_caches = []
        for _ in range(num_layers):
            kv_cache = (
                torch.zeros(kv_cache_shape, dtype=dtype),
                torch.zeros(kv_cache_shape, dtype=dtype),
            )
            kv_caches.append(kv_cache)
        return kv_caches

    @staticmethod
    def get_model_dims(config: PretrainedConfig) -> CausalModelDims:
        """Get model dimensions from the configuration for export.

        Args:
            config (PretrainedConfig): Model configuration.

        Returns:
            CausalModelDims: Model dimensions used for export.

        Raises:
            ValueError: If required fields are missing in the configuration.
        """

        def resolve(config: PretrainedConfig, *keys: str) -> Optional[int]:
            return next((getattr(config, k) for k in keys if hasattr(config, k)), None)

        hidden_size = resolve(config, "hidden_size", "n_embd")
        num_heads = resolve(config, "num_attention_heads", "n_head")
        num_layers = resolve(config, "num_hidden_layers", "n_layer")
        num_kv_heads = resolve(config, "num_key_value_heads")

        if hidden_size is None:
            raise ValueError(
                f"Missing required field 'hidden_size or n_embd' in {config.__class__.__name__}"
            )
        if num_heads is None:
            raise ValueError(
                "Missing required field 'num_attention_heads or n_head' "
                f"in {config.__class__.__name__}"
            )
        if num_layers is None:
            raise ValueError(
                "Missing required field 'num_hidden_layers or n_layer' "
                f"in {config.__class__.__name__}"
            )

        if num_kv_heads is None:
            num_kv_heads = 1 if getattr(config, "multi_query", False) else num_heads

        head_dim = hidden_size // num_heads

        return CausalModelDims(
            num_layers=num_layers,
            num_kv_heads=num_kv_heads,
            head_dim=head_dim,
        )
