from abc import abstractmethod
from typing import Any, Dict, Optional

import torch
import torch.nn as nn

from furiosa_models.architecture.layers.ops import OpBase


class LayerNormOpBase(OpBase):
    """Abstract base class for LayerNorm operations.

    This class serves as the foundation for LayerNorm operations, defining
    the interface that all LayerNorm operations must implement.

    Methods:
        compute(): Defines how the LayerNorm operation is applied to the input tensor.
    """

    @abstractmethod
    def compute(self, x: torch.Tensor, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Applies the LayerNorm operation to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_size)`.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            torch.Tensor: Output tensor after applying the LayerNorm operation
                with shape `(batch_size, sequence_length, hidden_size)`.

        Raises:
            NotImplementedError: Must be implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute()`.")


class RMSNormOp(LayerNormOpBase):
    """Concrete implementation of the RMSNorm operation.

    This class applies RMSNorm using PyTorch's `F.rms_norm` function.
    """

    def create_weights(
        self, hidden_size: int, params_dtype: torch.dtype, use_weight: bool = True
    ) -> Dict[str, Optional[nn.Parameter]]:
        """Creates and initializes the scaling weight for RMSNorm.

        Args:
            hidden_size (int): Size of the last dimension of the input tensor.
            params_dtype (torch.dtype): Data type for the weight parameter.
            use_weight (bool, optional): Whether to use a learnable weight. Defaults to True.

        Returns:
            Dict[str, Optional[nn.Parameter]]: A dictionary containing:
                - "weight" (nn.Parameter, optional): Scaling parameter of shape `(hidden_size,)`.
        """
        weight = None
        if use_weight:
            weight = nn.Parameter(torch.ones(hidden_size, dtype=params_dtype), requires_grad=False)
        return {"weight": weight}

    def compute(
        self,
        x: torch.Tensor,
        weight: Optional[torch.Tensor] = None,
        eps: float = 1e-6,
    ) -> torch.Tensor:
        """Applies RMSNorm to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape (batch_size, seq_len, hidden_size).
            weight (Optional[torch.Tensor]): Optional scaling weight of shape (hidden_size,).
            eps (float, optional): Small constant for numerical stability. Defaults to 1e-6.

        Returns:
            torch.Tensor: Normalized output of shape (batch_size, seq_len, hidden_size).
        """
        orig_dtype = x.dtype
        x = x.to(torch.float32)

        variance = x.pow(2).mean(dim=-1, keepdim=True)
        x = x * torch.rsqrt(variance + eps)
        x = x.to(orig_dtype)

        if weight is not None:
            x = x * weight

        return x


class LayerNormOp(LayerNormOpBase):
    """Concrete implementation of the standard LayerNorm operation."""

    def create_weights(
        self,
        hidden_size: int,
        params_dtype: torch.dtype,
        use_weight: bool = True,
        use_bias: bool = True,
    ) -> Dict[str, Optional[nn.Parameter]]:
        """Creates and initializes the weight and bias for LayerNorm.

        Args:
            hidden_size (int): Size of the last dimension of the input tensor.
            params_dtype (torch.dtype): Data type for the parameters.
            use_weight (bool, optional): Whether to use a learnable weight. Defaults to True.
            use_bias (bool, optional): Whether to use a learnable bias. Defaults to True.

        Returns:
            Dict[str, Optional[nn.Parameter]]: A dictionary containing:
                - "weight" (nn.Parameter, optional): Scaling parameter of shape `(hidden_size,)`.
                - "bias" (nn.Parameter, optional): Bias parameter of shape `(hidden_size,)`.
        """
        weight = (
            nn.Parameter(torch.ones(hidden_size, dtype=params_dtype), requires_grad=False)
            if use_weight
            else None
        )
        bias = (
            nn.Parameter(torch.zeros(hidden_size, dtype=params_dtype), requires_grad=False)
            if use_bias
            else None
        )
        return {"weight": weight, "bias": bias}

    def compute(
        self,
        x: torch.Tensor,
        weight: Optional[torch.Tensor] = None,
        bias: Optional[torch.Tensor] = None,
        eps: float = 1e-5,
    ) -> torch.Tensor:
        """Manually computes LayerNorm.

        Args:
            x (torch.Tensor): Input tensor of shape (..., hidden_size).
            weight (Optional[torch.Tensor]): Learnable scale tensor.
            bias (Optional[torch.Tensor]): Learnable bias tensor.
            eps (float): Numerical stability term.

        Returns:
            torch.Tensor: Normalized tensor of the same shape.
        """
        orig_dtype = x.dtype
        x = x.to(torch.float32)

        # Mean and variance over last dimension
        mean = x.mean(dim=-1, keepdim=True)
        mean_sq = (x * x).mean(dim=-1, keepdim=True)
        var = mean_sq - mean * mean

        x = (x - mean) * torch.rsqrt(var + eps)

        x = x.to(orig_dtype)

        if weight is not None:
            x = x * weight
        if bias is not None:
            x = x + bias

        return x
