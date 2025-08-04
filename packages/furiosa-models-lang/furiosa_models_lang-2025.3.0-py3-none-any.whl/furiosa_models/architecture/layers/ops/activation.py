from abc import abstractmethod
from typing import Any

import torch
import torch.nn.functional as F

from furiosa_models.architecture.layers.ops import OpBase


class ActivationOpBase(OpBase):
    """Abstract base class for activation operations.

    This class serves as the foundation for activation functions, defining
    the interface that all activation operations must implement.

    Methods:
        compute(): Defines how the activation function is applied to the input tensor.
    """

    @abstractmethod
    def compute(self, x: torch.Tensor, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Applies the activation function to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_size)`.
            *args(Any): Additional positional arguments.
            **kwargs(Any): Additional keyword arguments.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, hidden_size)`
                after applying the activation function element-wise.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute()`.")


class SiLUOp(ActivationOpBase):
    """Concrete implementation of the SiLU (Sigmoid Linear Unit) activation function.

    Applies the SiLU activation function element-wise using PyTorch's built-in `F.silu()`.

    The SiLU activation function is defined as:
        SiLU(x) = x * sigmoid(x)

    Methods:
        compute(): Applies the SiLU activation to the input tensor.
    """

    def compute(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the SiLU activation function element-wise.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_size)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, hidden_size)`
                with the SiLU activation applied element-wise.
        """
        return F.silu(x)


class GELUOp(ActivationOpBase):
    """Concrete implementation of the GELU (Gaussian Error Linear Unit) activation function.

    Applies the GELU activation function element-wise using PyTorch's built-in `F.gelu()`.

    The GELU activation function is defined as:
        GELU(x) = x * Φ(x)

    where Φ(x) is the cumulative distribution function of the standard normal distribution.
    """

    def compute(self, x: torch.Tensor, approximate: str = "none") -> torch.Tensor:
        """Applies the GELU activation function element-wise.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_size)`.
            approximate (str): Approximation method for GELU. Default is 'none'.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, hidden_size)`
                with the GELU activation applied element-wise.
        """
        return F.gelu(x, approximate=approximate)
