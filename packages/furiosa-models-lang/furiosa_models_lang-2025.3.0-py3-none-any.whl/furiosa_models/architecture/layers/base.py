from abc import ABC, abstractmethod
from typing import Any

import torch
import torch.nn as nn

from furiosa_models.architecture.layers.ops import OpBase


class LayerBase(nn.Module, ABC):
    """Base class for layers without learnable weights (e.g., activation functions).

    Provides a unified interface for non-weighted layers. Subclasses must implement
    the core computation logic using `forward()` and select the appropriate operation via
    `select_op()`.

    Methods:
        select_op(): Abstract method for selecting an operation for this layer.
        extra_repr(): Provides additional string representation for debugging.
    """

    @abstractmethod
    def select_op(self, *args: Any, **kwargs: Any) -> OpBase:
        """Selects the operation associated with this layer.

        This method should be overridden by subclasses to return an instance of `OpBase`
        or its subclasses (e.g., activation, linear operation).

        Args:
            *args(Any): Variable length positional arguments for selecting the operation.
            **kwargs(Any): Arbitrary keyword arguments for selecting the operation.

        Returns:
            OpBase: An instance of the operation associated with this layer.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `select_op()`.")

    @abstractmethod
    def extra_repr(self) -> str:
        """Provides an additional string representation for debugging and logging purposes.

        Returns:
            str: A formatted string representing key attributes of the layer.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `extra_repr()`.")


class WeightedLayerBase(LayerBase):
    """Base class for layers with learnable weights (e.g., Linear, MoE).

    Extends `LayerBase` to handle learnable weights. Subclasses must implement
    `register_weights()` to initialize and register weights.

    Methods:
        register_weights(params_dtype): Abstract method to register learnable weights.
    """

    @abstractmethod
    def register_weights(self, params_dtype: torch.dtype) -> None:
        """Registers and initializes learnable weights for the layer.

        This method should be overridden by subclasses to create and register
        learnable parameters (e.g., weights, biases) needed by the operation.

        Args:
            params_dtype(torch.dtype): The data type used to initialize weights.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
        raise NotImplementedError("Subclasses must implement `register_weights()`.")
