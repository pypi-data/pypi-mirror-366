from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Union

import torch
import torch.nn as nn


class OpBase(ABC):
    """Base class for all operations (with or without weights).

    This class serves as the foundation for both weighted and non-weighted operations.
    All subclasses must implement the `compute()` method to define the core logic of the operation.

    Methods:
        compute(*args, **kwargs): Executes the core computation logic of the operation.
    """

    @abstractmethod
    def compute(self, *args: Any, **kwargs: Any) -> Union[torch.Tensor, Tuple[torch.Tensor, ...]]:
        """Executes the core computation for the operation.

        This method should be overridden by all subclasses to define
        the specific computation (e.g., matrix multiplication, activation).

        Args:
            *args(Any): Variable length positional arguments specific to the operation.
            **kwargs(Any): Arbitrary keyword arguments specific to the operation.

        Returns:
            Union[torch.Tensor, Tuple[torch.Tensor, ...]]: A single tensor or a tuple of tensors,
            depending on the specific operation.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute()`.")


class WeightedOpBase(OpBase):
    """Base class for operations involving learnable weights (e.g., Linear, MoE).

    This class extends `OpBase` by adding methods for creating and processing weights.
    It should be used for operations where weights are essential for computation.

    Methods:
        create_weights(*args, **kwargs): Abstract method to create and initialize weights.
        process_weights(*args, **kwargs): Optional method to process weights after initialization.
    """

    @abstractmethod
    def create_weights(self, *args: Any, **kwargs: Any) -> Dict[str, nn.Parameter]:
        """Creates and registers the weights required for the operation.

        This method must be overridden by subclasses to initialize any
        learnable parameters specific to the operation.

        Args:
            *args(Any): Variable length positional arguments for weight creation.
            **kwargs(Any): Arbitrary keyword arguments for additional weight attributes.

        Returns:
            Dict[str, nn.Parameter]: A dictionary containing the initialized weights, typically in
            the form:
                {
                    "weight": torch.nn.Parameter,
                    "bias": torch.nn.Parameter (optional)
                }

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `create_weights()`.")

    def process_weights(self, *args: Any, **kwargs: Any) -> None:
        """Processes weights after their creation or loading.

        This method can be overridden by subclasses to perform additional processing on the weights,
        such as transposing matrices, applying normalization, or scaling values.

        Args:
            *args(Any): Variable length positional arguments for processing.
            **kwargs(Any): Arbitrary keyword arguments for specific processing options.
        """
        pass  # Optional to override depending on the operation
