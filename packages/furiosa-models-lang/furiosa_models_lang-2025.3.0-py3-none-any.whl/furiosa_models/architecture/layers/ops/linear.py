from abc import abstractmethod
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from furiosa_models.architecture.layers.ops import WeightedOpBase


class LinearOpBase(WeightedOpBase):
    """Abstract base class for linear operations with learnable weights.

    This class serves as the foundation for linear operations, including the creation of
    learnable weights (such as weight matrices and biases) and the definition of
    computation logic using these weights.

    Methods:
        create_weights(): Initializes the learnable weights for the operation.
        compute(): Defines how the input tensor interacts with the weights during computation.
    """

    @abstractmethod
    def create_weights(
        self,
        input_size: int,
        output_size: int,
        params_dtype: torch.dtype,
        use_bias: bool = False,
        **extra_weight_attrs: Any,
    ) -> Dict[str, nn.Parameter]:
        """Initializes the learnable weights for the linear operation.

        Args:
            input_size (int): The size of each input feature.
            output_size (int): The size of each output feature.
            params_dtype (torch.dtype): The data type for the parameters.
            use_bias (bool, optional): Whether to include a bias term. Defaults to False.
            **extra_weight_attrs (Any): Additional keyword arguments for custom weight
                initialization.

        Returns:
            Dict[str, nn.Parameter]: A dictionary containing initialized weights. Typically:
                {
                    "weight": torch.nn.Parameter,  # Shape `(output_size, input_size)`
                    "bias": torch.nn.Parameter (optional)  # Shape `(output_size,)` if use_bias=True
                }

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `create_weights()`.")

    @abstractmethod
    def compute(
        self, x: torch.Tensor, weight: torch.Tensor, bias: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Performs the linear computation using the input tensor and weights.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, input_size)` or
                `(batch_size, sequence_length, input_size)` for LLM models.
            weight (torch.Tensor): Weight matrix of shape `(output_size, input_size)`.
            bias (Optional[torch.Tensor]): Bias vector of shape `(output_size,)` if present.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, output_size)` or
                `(batch_size, sequence_length, output_size)` depending on the input shape.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute()`.")


class LinearOp(LinearOpBase):
    """Concrete implementation of a linear operation.

    Implements both the creation of learnable weights and the actual linear transformation
    using PyTorch's `F.linear()` function.
    """

    def create_weights(
        self,
        input_size: int,
        output_size: int,
        params_dtype: torch.dtype,
        use_bias: bool = False,
        **extra_weight_attrs: Any,
    ) -> Dict[str, nn.Parameter]:
        """Creates and initializes the weight matrix and optional bias.

        Args:
            input_size (int): Number of input features.
            output_size (int): Number of output features.
            params_dtype (torch.dtype): Data type for the weights and bias.
            use_bias (bool, optional): Whether to include a learnable bias term. Defaults to False.
            **extra_weight_attrs (Any): Additional keyword arguments for custom initialization.

        Returns:
            Dict[str, nn.Parameter]: A dictionary containing:
                - "weight" (torch.nn.Parameter): Weight matrix of shape `(output_size, input_size)`.
                - "bias" (torch.nn.Parameter, optional): Bias term of shape `(output_size,)` if
                    `use_bias=True`.
        """
        _ = extra_weight_attrs

        weight = nn.Parameter(
            torch.empty(output_size, input_size, dtype=params_dtype), requires_grad=False
        )
        if use_bias:
            bias = nn.Parameter(torch.empty(output_size, dtype=params_dtype), requires_grad=False)
            return {"weight": weight, "bias": bias}
        return {"weight": weight}

    def compute(
        self, x: torch.Tensor, weight: torch.Tensor, bias: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Applies the linear transformation using PyTorch's built-in `F.linear()` function.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, input_size)` or
                `(batch_size, sequence_length, input_size)` for transformer-based models.
            weight (torch.Tensor): Weight matrix of shape `(output_size, input_size)`.
            bias (Optional[torch.Tensor]): Optional bias term of shape `(output_size,)`.

        Returns:
            torch.Tensor: Output tensor with shape `(batch_size, output_size)` or
                `(batch_size, sequence_length, output_size)` depending on the input shape.
        """
        return F.linear(x, weight, bias)
