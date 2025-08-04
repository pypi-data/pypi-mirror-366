from typing import Optional

import torch

from furiosa_models.architecture.layers import LayerBase
from furiosa_models.architecture.layers.ops.layernorm import LayerNormOp, RMSNormOp


class LayerNormLayerBase(LayerBase):
    """Base class for all layer normalization layers.

    This class serves as a foundation for layer normalization layers that apply
    normalization techniques to input tensors.
    """

    pass


class RMSNormLayer(LayerNormLayerBase):
    """RMSNorm Layer that applies Root Mean Square Normalization.

    This layer normalizes the input tensor based on the root mean square (RMS) of its elements.
    The operation follows the equation:
        y = x / sqrt(mean(x^2) + eps)

    Args:
        hidden_size (int): The size of the last dimension of the input tensor.
        eps (float): Small constant to prevent division by zero.
        var_hidden_size (Optional[int]): Override for variance size computation.
        use_weight (bool): Whether to apply a learnable scaling factor.
        params_dtype (Optional[torch.dtype]): Data type for the weights.
    """

    def __init__(
        self,
        hidden_size: int,
        eps: float = 1e-6,
        var_hidden_size: Optional[int] = None,
        use_weight: bool = True,
        params_dtype: Optional[torch.dtype] = None,
    ) -> None:
        super().__init__()
        if params_dtype is None:
            params_dtype = torch.get_default_dtype()

        self.hidden_size = hidden_size
        self.variance_size_override = None if var_hidden_size == hidden_size else var_hidden_size
        self.eps = eps
        self.use_weight = use_weight

        self.op = self.select_op()
        self.register_weights(params_dtype)

    def select_op(self) -> RMSNormOp:
        """Selects the RMSNorm operation to be used by the layer.

        Returns:
            RMSNormOp: Instance of the RMSNorm operation.
        """
        return RMSNormOp()

    def register_weights(self, params_dtype: torch.dtype = torch.float32) -> None:
        """Initializes and registers the weights for RMSNorm.

        Args:
            params_dtype (torch.dtype): Data type for the weights.
        """
        weights = self.op.create_weights(
            hidden_size=self.variance_size_override or self.hidden_size,
            params_dtype=params_dtype,
            use_weight=self.use_weight,
        )

        for name, param in weights.items():
            self.register_parameter(name, param)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies Root Mean Square Normalization (RMSNorm) to the input tensor.

        This method normalizes the input tensor along the last dimension using
        its root mean square (RMS) value, ensuring numerical stability with
        a small epsilon value. If a learnable weight is provided, it is applied
        as a scaling factor after normalization.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_size)`.

        Returns:
            torch.Tensor: The normalized output tensor of the same shape as the input.

        Raises:
            ValueError: If the input tensor's hidden size does not match the expected `hidden_size`.
        """
        hidden_size = x.shape[-1]

        if hidden_size != self.hidden_size:
            raise ValueError(f"Expected hidden_size {self.hidden_size}, but got {hidden_size}")

        if self.variance_size_override and hidden_size < self.variance_size_override:
            raise ValueError(
                f"Expected hidden_size >= {self.variance_size_override}, but got {hidden_size}"
            )

        if self.variance_size_override is not None:
            x = x[..., : self.variance_size_override]

        return self.op.compute(
            x,
            eps=self.eps,
            **dict(self.named_parameters()),
        )

    def extra_repr(self) -> str:
        """Provides a string representation for debugging.

        Returns:
            str: A description of layer settings for debugging.
        """
        base_repr = f"hidden_size={self.hidden_size}, eps={self.eps}"
        if self.variance_size_override is not None:
            base_repr += f", variance_size_override={self.variance_size_override}"
        return base_repr


class LayerNormLayer(LayerNormLayerBase):
    """Standard LayerNorm Layer that applies mean-variance normalization.

    This layer normalizes the input tensor using both the mean and variance over the last dimension.
    The operation follows the equation:
        y = (x - mean) / sqrt(var + eps) * weight + bias

    Args:
        hidden_size (int): The size of the last dimension of the input tensor.
        eps (float, optional): A small constant to avoid division by zero. Default is 1e-5.
        elementwise_affine (bool, optional): Whether to apply learnable per-element weight and bias.
             Default is True.
        use_bias (bool, optional): If set to False, disables bias term (only valid when
            `elementwise_affine=True`). Default is True.
        params_dtype (Optional[torch.dtype], optional): Data type for the parameters. If None,
            defaults to `torch.get_default_dtype()`.
    """

    def __init__(
        self,
        hidden_size: int,
        eps: float = 1e-5,
        elementwise_affine: bool = True,
        use_bias: bool = True,
        params_dtype: Optional[torch.dtype] = None,
    ) -> None:
        super().__init__()
        if params_dtype is None:
            params_dtype = torch.get_default_dtype()

        self.hidden_size = hidden_size
        self.eps = eps
        self.use_weight = elementwise_affine
        self.use_bias = elementwise_affine and use_bias

        self.op = self.select_op()
        self.register_weights(params_dtype)

    def select_op(self) -> LayerNormOp:
        """Selects the LayerNorm operation to be used by the layer.

        Returns:
            LayerNormOp: Instance of the LayerNorm operation.
        """
        return LayerNormOp()

    def register_weights(self, params_dtype: torch.dtype = torch.float32) -> None:
        """Initializes and registers the weight and bias parameters for LayerNorm.

        Args:
            params_dtype (torch.dtype): Data type of the parameters.
        """
        weights = self.op.create_weights(
            hidden_size=self.hidden_size,
            params_dtype=params_dtype,
            use_weight=self.use_weight,
            use_bias=self.use_bias,
        )
        for name, param in weights.items():
            self.register_parameter(name, param)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies Layer Normalization to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, ..., hidden_size)`.

        Returns:
            torch.Tensor: Normalized tensor with same shape as input.

        Raises:
            ValueError: If the input tensor's last dimension does not match `hidden_size`.
        """
        if x.shape[-1] != self.hidden_size:
            raise ValueError(f"Expected last dimension {self.hidden_size}, got {x.shape[-1]}")
        return self.op.compute(
            x,
            eps=self.eps,
            **dict(self.named_parameters()),
        )

    def extra_repr(self) -> str:
        """Provides a string representation for debugging.

        Returns:
            str: Configuration of the LayerNorm layer.
        """
        return (
            f"hidden_size={self.hidden_size}, eps={self.eps}, "
            f"use_weight={self.use_weight}, use_bias={self.use_bias}"
        )
