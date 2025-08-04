from abc import abstractmethod
from typing import Optional, TypeVar

import torch

from furiosa_models.architecture.layers import WeightedLayerBase
from furiosa_models.architecture.layers.ops import OpBase
from furiosa_models.architecture.layers.ops.linear import LinearOp, LinearOpBase
from furiosa_models.architecture.layers.ops.vocab_embedding import (
    VocabEmbeddingOp,
    VocabEmbeddingOpBase,
)
from furiosa_models.config import QuantizationConfig

DEFAULT_VOCAB_PADDING_SIZE = 64

LMHeadLayerType = TypeVar("LMHeadLayerType", bound="LMHeadLayerBase")


# For efficient memory access, we pad the vocabulary size to a multiple of 64.
def pad_vocab_size(vocab_size: int, pad_to: int = DEFAULT_VOCAB_PADDING_SIZE) -> int:
    """Pads the vocabulary size to the nearest multiple of the specified value.

    Args:
        vocab_size (int): The original vocabulary size.
        pad_to (int, optional): Padding multiple (default: 64).

    Returns:
        int: Padded vocabulary size, rounded up to the nearest multiple of `pad_to`.
    """
    return vocab_size + (-vocab_size % pad_to)


class VocabLayerBase(WeightedLayerBase):
    """Base class for vocabulary-related layers using PyTorch.

    This layer handles vocabulary operations such as embedding lookup
    and linear transformations for output projection.

    Args:
        num_embeddings (int): Number of tokens in the vocabulary.
        embedding_dim (int): Dimension of each embedding vector.
        orig_num_embeddings (Optional[int]): Original vocabulary size.
        padding_size (int): Padding size for vocabulary size.
        params_dtype (Optional[torch.dtype]): Data type for the weights. Defaults to None.
        quant_config (Optional[QuantizationConfig]): Configuration for quantization.
        prefix (str): Prefix for layer name.

    Raises:
        ValueError: If the total vocab size is less than the original vocab size.
    """

    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        orig_num_embeddings: Optional[int] = None,
        padding_size: int = DEFAULT_VOCAB_PADDING_SIZE,
        params_dtype: Optional[torch.dtype] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()

        if params_dtype is None:
            params_dtype = torch.get_default_dtype()

        self.num_embeddings = num_embeddings

        if orig_num_embeddings is not None:
            if num_embeddings < orig_num_embeddings:
                raise ValueError(
                    "Total vocab size (num_embeddings) must be greater than or equal to "
                    "the original vocab size (orig_num_embeddings). "
                    f"(num_embeddings={num_embeddings}, orig_num_embeddings={orig_num_embeddings})"
                )

        self.orig_vocab_size = orig_num_embeddings or num_embeddings
        self.orig_vocab_size_padded = pad_vocab_size(
            vocab_size=self.orig_vocab_size, pad_to=padding_size
        )

        self.num_embeddings_padded = pad_vocab_size(
            # padded vocab size + extra tokens
            vocab_size=self.orig_vocab_size_padded + (num_embeddings - self.orig_vocab_size),
            pad_to=padding_size,
        )

        self.embedding_dim = embedding_dim

        self.op = self.select_op(quant_config, prefix)

        self.register_weights(params_dtype)

    @abstractmethod
    def select_op(
        self, quant_config: Optional[QuantizationConfig] = None, prefix: str = ""
    ) -> OpBase:
        """Selects the linear operation for output projection.

        Args:
            quant_config (Optional[QuantizationConfig]): Configuration for quantization.
            prefix (str): Prefix for the operation name.

        Returns:
            OpBase: Operation used for linear transformation.

        Raises:
            NotImplementedError: If ths method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `select_op()`.")

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Abstract method for forward computation.

        Args:
            x (torch.Tensor): Input tensor.

        Returns:
            torch.Tensor: Output tensor after applying the operation.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `forward()`.")


class VocabEmbeddingLayerBase(VocabLayerBase):
    """Base class for vocab embedding layers.

    This layer handles vocabulary embedding operations, such as embedding lookup.

    Args:
        num_embeddings (int): Number of tokens in the vocabulary.
        embedding_dim (int): Dimension of each embedding vector.
        orig_num_embeddings (Optional[int]): Original vocabulary size.
        padding_size (int): Padding size for vocabulary size.
        params_dtype (Optional[torch.dtype]): Data type for the weights. Defaults to None.
        quant_config (Optional[QuantizationConfig]): Configuration for quantization.
        prefix (str): Prefix for layer name.
    """

    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        orig_num_embeddings: Optional[int] = None,
        padding_size: int = DEFAULT_VOCAB_PADDING_SIZE,
        params_dtype: Optional[torch.dtype] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__(
            num_embeddings,
            embedding_dim,
            orig_num_embeddings,
            padding_size,
            params_dtype,
            quant_config,
            prefix,
        )

        self.op: VocabEmbeddingOpBase = self.select_op(quant_config, prefix)

    def select_op(
        self, quant_config: Optional[QuantizationConfig] = None, prefix: str = ""
    ) -> VocabEmbeddingOpBase:
        """Selects the embedding operation.

        Args:
            quant_config (Optional[QuantizationConfig]): Configuration for quantization.
            prefix (str): Prefix for the operation name.

        Returns:
            VocabEmbeddingOpBase: Operation used for embedding lookup.

        Raises:
            NotImplementedError: If quantization is enabled.
        """
        _ = prefix
        if quant_config is not None:
            raise NotImplementedError("Quantization is not yet supported for VocabEmbeddingLayer.")
        return VocabEmbeddingOp()


class LMHeadLayerBase(VocabLayerBase):
    """Base class for language modeling head layers using linear transformation.

    This layer handles output projection operations for language modeling tasks.

    Args:
            num_embeddings (int): Number of tokens in the vocabulary.
            embedding_dim (int): Dimension of each embedding vector.
            orig_num_embeddings (Optional[int]): Original vocabulary size.
            padding_size (int): Padding size for vocabulary size.
            use_bias (bool): Whether to use bias in the linear transformation. Defaults to False.
            params_dtype (Optional[torch.dtype]): Data type for the weights. Defaults to None.
            quant_config (Optional[QuantizationConfig], optional): Configuration for quantization.
            prefix (str): Prefix for layer name.
    """

    def __init__(
        self,
        num_embeddings: int,
        embedding_dim: int,
        orig_num_embeddings: Optional[int] = None,
        padding_size: int = DEFAULT_VOCAB_PADDING_SIZE,
        use_bias: bool = False,
        params_dtype: Optional[torch.dtype] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        self.use_bias = use_bias
        self.quant_config = quant_config

        super().__init__(
            num_embeddings,
            embedding_dim,
            orig_num_embeddings,
            padding_size,
            params_dtype,
            quant_config,
            prefix,
        )

        self.op: LinearOpBase = self.select_op(quant_config, prefix)

    def select_op(
        self, quant_config: Optional[QuantizationConfig] = None, prefix: str = ""
    ) -> LinearOpBase:
        """Selects the linear operation for output projection.

        Args:
            quant_config (Optional[QuantizationConfig]): Configuration for quantization.
            prefix (str): Prefix for the operation name.

        Returns:
            LinearOpBase: Operation used for linear transformation.

        Raises:
            NotImplementedError: If quant_config is given.
        """
        _ = prefix
        if quant_config is not None:
            raise NotImplementedError("Quantization is not yet supported for LMHeadLayer.")
        return LinearOp()

    def tie_weights(self: LMHeadLayerType, layer: VocabEmbeddingLayerBase) -> LMHeadLayerType:
        """Ties the weights with another embedding layer.

        Args:
            layer (VocabEmbeddingLayerBase): Layer whose weights will be shared.

        Returns:
            LMHeadLayerType: Layer with tied weights.

        Raises:
            TypeError: If `layer` is not an instance of `VocabEmbeddingLayerBase`.
            NotImplementedError: If quant_config is given.
        """
        if not isinstance(layer, VocabEmbeddingLayerBase):
            raise TypeError(
                f"Expected an instance of VocabEmbeddingLayerBase, got {type(layer).__name__}."
            )

        if self.quant_config:
            raise NotImplementedError("Quantization is not yet supported for tying weights.")

        self.register_parameter("weight", layer.weight)

        return self


class VocabEmbeddingLayer(VocabEmbeddingLayerBase):
    """Embedding layer that maps token indices to dense vectors."""

    def register_weights(self, params_dtype: torch.dtype) -> None:
        """Registers embedding weights.

        Args:
            params_dtype (torch.dtype): Data type for the weights.
                - Weight tensor shape: `(num_embeddings_padded, embedding_dim)` for embedding
                    lookup.
        """
        weights = self.op.create_weights(
            embedding_dim=self.embedding_dim,
            num_embeddings=self.num_embeddings_padded,
            params_dtype=params_dtype,
        )
        for name, weight in weights.items():
            self.register_parameter(name, weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Converts token indices into dense embeddings.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, embedding_dim)`.
        """
        return self.op.embedding(x, **dict(self.named_parameters()))

    def extra_repr(self) -> str:
        """Returns a string representation for debugging.

        Returns:
            str: Summary of the layer configuration.
        """
        return (
            f"embedding_dim={self.embedding_dim}, "
            f"num_embeddings={self.num_embeddings}, "
            f"num_embeddings_padded={self.num_embeddings_padded}, "
            f"orig_vocab_size={self.orig_vocab_size}, "
        )


class LMHeadLayer(LMHeadLayerBase):
    """Language modeling head layer that projects embeddings to vocabulary logits."""

    def register_weights(self, params_dtype: torch.dtype) -> None:
        """Registers linear transformation weights.

        Args:
            params_dtype (torch.dtype): Data type for the weights.
                - Weight tensor shape: `(vocab_size, embedding_dim)` for output projection.
                - Bias tensor shape (optional): `(vocab_size,)` if `use_bias` is True.
        """
        weights = self.op.create_weights(
            input_size=self.embedding_dim,
            output_size=self.num_embeddings_padded,
            params_dtype=params_dtype,
            use_bias=self.use_bias,
        )
        for name, weight in weights.items():
            self.register_parameter(name, weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Projects embeddings into vocabulary logits.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, embedding_dim)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, vocab_size)`.
        """
        return self.op.compute(x, **dict(self.named_parameters()))

    def extra_repr(self) -> str:
        """Provides a debug-friendly string representation of the layer.

        Returns:
            str: Summary of the layer configuration.
        """
        return (
            f"embedding_dim={self.embedding_dim}, "
            f"num_embeddings={self.num_embeddings}, "
            f"num_embeddings_padded={self.num_embeddings_padded}, "
            f"orig_vocab_size={self.orig_vocab_size}, "
            f"use_bias={self.use_bias}"
        )
