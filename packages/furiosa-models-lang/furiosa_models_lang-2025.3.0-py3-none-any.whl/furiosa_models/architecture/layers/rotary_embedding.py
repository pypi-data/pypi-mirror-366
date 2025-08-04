from typing import Any, Dict, Optional, Tuple

import torch

from furiosa_models.architecture.layers import LayerBase
from furiosa_models.architecture.layers.ops.rotary_embedding import (
    DeepseekScalingRotaryEmbeddingOp,
    DynamicNTKScalingRotaryEmbeddingOp,
    LinearScalingRotaryEmbeddingOp,
    Llama3RotaryEmbeddingOp,
    Llama4VisionRotaryEmbeddingOp,
    MRotaryEmbeddingOp,
    Phi3LongRoPEScaledRotaryEmbeddingOp,
    RotaryEmbeddingOp,
    RotaryEmbeddingOpBase,
    YaRNScalingRotaryEmbeddingOp,
)


class RotaryEmbeddingLayerBase(LayerBase):
    """Base class for rotary positional embedding layers.

    This abstract base class defines the common structure for all rotary embedding layers.
    Subclasses must implement their own specific behavior.
    """

    pass


class RotaryEmbeddingLayer(RotaryEmbeddingLayerBase):
    """Rotary positional embedding layer for transformer models.

    This layer applies rotary positional embeddings to query and key tensors during the
    attention computation.

    Args:
            head_size (int): Size of each attention head.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position (int): Maximum number of position embeddings.
            base (float): Base frequency for positional encoding.
            is_neox_style (bool): If True, uses Neox-style rotary embeddings. Defaults to True.
            rope_scaling (Optional[Dict[str, Any]]): Scaling configuration for advanced
                embeddings. Defaults to None.
            dtype (Optional[torch.dtype]): Data type for internal operations. Defaults to None.
            partial_rotary_factor (float): Fraction of dimensions for rotary embedding.
                Defaults to 1.0.
    """

    def __init__(
        self,
        head_size: int,
        rotary_dim: int,
        max_position: int,
        base: float,
        is_neox_style: bool = True,
        rope_scaling: Optional[Dict[str, Any]] = None,
        dtype: Optional[torch.dtype] = None,
        partial_rotary_factor: float = 1.0,
    ) -> None:
        super().__init__()

        if dtype is None:
            dtype = torch.get_default_dtype()

        if partial_rotary_factor < 1.0:
            rotary_dim = int(rotary_dim * partial_rotary_factor)

        self.head_size = head_size
        self.rotary_dim = rotary_dim
        self.max_position = max_position
        self.base = base
        self.is_neox_style = is_neox_style
        self.dtype = dtype

        self.op = self.select_op(rope_scaling)

        # Register the cosine and sine cache buffer
        self.register_buffer(
            "cos_sin_cache",
            self.op.compute_cos_sin(self.base, self.rotary_dim, self.max_position, rope_scaling).to(
                dtype
            ),
            persistent=False,
        )

    def select_op(self, rope_scaling: Optional[Dict[str, Any]] = None) -> RotaryEmbeddingOpBase:
        """Selects the appropriate rotary embedding operation based on scaling configuration.

        Args:
            rope_scaling (Optional[Dict[str, Any]]): Scaling configuration.

        Returns:
            RotaryEmbeddingOpBase: An instance of the selected rotary embedding operation.

        Raises:
            ValueError: If the scaling type is unknown.
        """
        if rope_scaling is None:
            return RotaryEmbeddingOp()

        scaling_type = rope_scaling.get("rope_type")

        if scaling_type == "llama3":
            return Llama3RotaryEmbeddingOp()

        elif scaling_type == "default":
            if "mrope_section" in rope_scaling:
                return MRotaryEmbeddingOp()
            return RotaryEmbeddingOp()

        elif scaling_type == "linear":
            return LinearScalingRotaryEmbeddingOp()

        elif scaling_type == "dynamic":
            return DynamicNTKScalingRotaryEmbeddingOp()

        elif scaling_type == "yarn":
            return YaRNScalingRotaryEmbeddingOp()

        elif scaling_type == "deepseek_yarn":
            return DeepseekScalingRotaryEmbeddingOp()

        elif scaling_type == "longrope":
            return Phi3LongRoPEScaledRotaryEmbeddingOp()

        elif scaling_type == "llama4":
            return Llama4VisionRotaryEmbeddingOp()

        raise ValueError(f"Unknown RoPE scaling type: {scaling_type}")

    def forward(
        self,
        positions: torch.Tensor,
        query: torch.Tensor,
        key: torch.Tensor,
        offsets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies rotary positional embedding to the query and key tensors.

        Args:
            positions (torch.Tensor): Input tensor of shape
                `(batch_size, sequence_length)` containing positional indices.
            query (torch.Tensor): Input tensor of shape
                `(batch_size, num_heads, sequence_length, hideen_size)` for queries.
            key (torch.Tensor): Input tensor of shape
                `(batch_size, num_heads, sequence_length, hideen_size)` for keys.
            offsets (Optional[torch.Tensor], optional): Offset positions for embeddings.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Transformed query and key tensors with the same
                shapes as inputs.
        """
        return self.op.compute(
            positions,
            query,
            key,
            head_size=self.head_size,
            rotary_dim=self.rotary_dim,
            cos_sin_cache=self.cos_sin_cache,
            is_neox_style=self.is_neox_style,
            offsets=offsets,
        )

    def extra_repr(self) -> str:
        """Provides a string representation for debugging.

        Returns:
            str: A formatted string summarizing the layer configuration.
        """
        return (
            f"OpType={self.op.__class__.__name__}, "
            f"head_size={self.head_size}, "
            f"rotary_dim={self.rotary_dim}, "
            f"max_position={self.max_position}, "
            f"base={self.base}, "
            f"is_neox_style={self.is_neox_style}"
        )
