import torch

from furiosa_models.architecture.layers import LayerBase
from furiosa_models.architecture.layers.ops.activation import ActivationOpBase, GELUOp, SiLUOp


class ActivationLayerBase(LayerBase):
    """Base class for all activation layers.

    This class serves as a foundation for activation layers that apply
    non-linear transformations to input tensors.
    """

    pass


class SiLULayer(ActivationLayerBase):
    """SiLU (Sigmoid Linear Unit) activation layer using SiLUOp.

    This layer applies the SiLU activation function element-wise:
    `y = x * sigmoid(x)`.
    """

    def __init__(self) -> None:
        super().__init__()
        self.op = self.select_op()

    def select_op(self) -> ActivationOpBase:
        """Selects the SiLU operation instance.

        Returns:
            ActivationOpBase: An instance of the SiLU operation.
        """
        return SiLUOp()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the SiLU activation function to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_dim)`
                or any arbitrary shape.

        Returns:
            torch.Tensor: Output tensor with the same shape as the input tensor.
        """
        return self.op.compute(x)

    def extra_repr(self) -> str:
        """Provides a string representation of the layer for debugging and logging.

        Returns:
            str: A description indicating the activation type.
        """
        return ""


class GELULayer(ActivationLayerBase):
    """GELU (Gaussian Error Linear Unit) activation layer using GELUOp.

    This layer applies the GELU activation function element-wise:
        GELU(x) = x * Φ(x)

    where Φ(x) is the cumulative distribution function (CDF) of the standard normal distribution.

    If `approximate='tanh'`, the GELU is estimated using:
        GELU(x) ≈ 0.5 * x * (1 + tanh(√(2/π) * (x + 0.044715 * x³)))
    """

    def __init__(self, approximate: str = "none") -> None:
        super().__init__()
        if approximate not in ["none", "tanh"]:
            raise ValueError(
                f"Invalid approximation method '{approximate}'. Choose 'none' or 'tanh'."
            )
        self.approximate = approximate

        self.op = self.select_op()

    def select_op(self) -> ActivationOpBase:
        """Selects the GELU operation instance.

        Returns:
            ActivationOpBase: An instance of the GELU operation.
        """
        return GELUOp()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Applies the GELU activation function to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, hidden_dim)`
                or any arbitrary shape.

        Returns:
            torch.Tensor: Output tensor with the same shape as the input tensor.
        """
        return self.op.compute(x, approximate=self.approximate)

    def extra_repr(self) -> str:
        """Provides a string representation of the layer for debugging and logging.

        Returns:
            str: A description indicating the activation type.
        """
        return f"approximate={self.approximate}"
