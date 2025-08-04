from abc import abstractmethod
from typing import Any, Dict, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F

from furiosa_models.architecture.layers.ops import WeightedOpBase


class VocabEmbeddingOpBase(WeightedOpBase):
    """Abstract base class for vocabulary embedding operations in inference-only mode.

    This class serves as the foundation for all embedding operations using fixed
    weights. Subclasses must implement the `embedding()` method to define the
    lookup logic for the embedding.

    Methods:
        embedding(x, weight): Abstract method for embedding lookup.
        compute(*args, **kwargs): Disabled method since embeddings do not use linear computations.
    """

    @abstractmethod
    def embedding(self, x: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
        """Executes the embedding lookup operation for the input indices.

        Args:
            x (torch.Tensor): Input tensor containing token indices of shape
                              `(batch_size, sequence_length)`.
            weight (torch.Tensor): Fixed embedding weight matrix of shape
                                   `(num_embeddings, embedding_dim)`.

        Returns:
            torch.Tensor: Embedded representation of input indices with shape
                          `(batch_size, sequence_length, embedding_dim)`.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `embedding()`.")

    def compute(self, *args: Any, **kwargs: Any) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        """Overridden to prevent accidental calls since embeddings do not use `compute()`.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.

        Returns:
            Union[torch.Tensor, Tuple[torch.Tensor, ...]]: Not applicable for this class.

        Raises:
            RuntimeError: If called, as embeddings use the `embedding()` method instead.
        """
        _ = args
        _ = kwargs
        raise RuntimeError(
            "`compute()` is not supported for VocabEmbedding operations. Use `embedding()` instead."
        )


class VocabEmbeddingOp(VocabEmbeddingOpBase):
    """Concrete implementation of a vocabulary embedding operation for inference-only scenarios.

    This class provides an embedding lookup mechanism using fixed weights.
    It does not create or update learnable weights since the framework is designed
    for inference purposes only.

    Example:
        op = VocabEmbeddingOp()
        weights = op.load_weights(pretrained_weights)
        output = op.embedding(input_tokens, weights["weight"])
    """

    def create_weights(
        self, embedding_dim: int, num_embeddings: int, params_dtype: torch.dtype
    ) -> Dict[str, nn.Parameter]:
        """Creates and initializes the embedding weight matrix.

        Args:
            embedding_dim (int): The dimensionality of the embedding vectors.
            num_embeddings (int): The size of the vocabulary (number of unique tokens).
            params_dtype (torch.dtype): Data type for the embedding weights (e.g., `torch.float32`).

        Returns:
            Dict[str, nn.Parameter]: A dictionary containing:
                - weight (torch.nn.Parameter): Embedding weight matrix of shape
                `(num_embeddings, embedding_dim)`. The weights are initialized
                with empty values and are non-trainable (`requires_grad=False`).

        Shapes:
            - Weight tensor:
                - Shape `(num_embeddings, embedding_dim)` representing the embedding
                vector for each token in the vocabulary.
        """
        return {
            "weight": nn.Parameter(
                torch.empty(num_embeddings, embedding_dim, dtype=params_dtype),
                requires_grad=False,
            )
        }

    def embedding(self, x: torch.Tensor, weight: torch.Tensor) -> torch.Tensor:
        """Performs embedding lookup using PyTorch's `F.embedding()`.

        Args:
            x (torch.Tensor): Input tensor containing token indices of shape
                              `(batch_size, sequence_length)`.
            weight (torch.Tensor): Fixed embedding weight matrix of shape
                                   `(num_embeddings, embedding_dim)`.

        Returns:
            torch.Tensor: Embedded representation of input indices with shape
                          `(batch_size, sequence_length, embedding_dim)`.
        """
        return F.embedding(x, weight)
