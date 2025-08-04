from abc import abstractmethod
from typing import Optional

import torch

from furiosa_models.architecture.layers import WeightedLayerBase
from furiosa_models.architecture.layers.ops import LinearOp, LinearOpBase
from furiosa_models.config import QuantizationConfig


class LinearLayerBase(WeightedLayerBase):
    """Base class for a fully connected linear layer using PyTorch's functional API.

    This layer performs a linear transformation on the input tensor:
    `y = xW^T + b`, where `W` is the weight matrix and `b` is an optional bias.

    Args:
        input_size (int): Size of each input feature (last dimension of input tensor).
        output_size (int): Size of each output feature (last dimension of output tensor).
        use_bias (bool, optional): If True, includes a learnable bias term. Defaults to True.
        params_dtype (Optional[torch.dtype]): Data type for the weights. Defaults to None.
        quant_config (Optional[QuantizationConfig]): Configuration for quantization.
        prefix (str, optional): Prefix for the layer name (default: "").
    """

    def __init__(
        self,
        input_size: int,
        output_size: int,
        use_bias: bool = True,
        params_dtype: Optional[torch.dtype] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()

        if params_dtype is None:
            params_dtype = torch.get_default_dtype()

        self.input_size = input_size
        self.output_size = output_size
        self.use_bias = use_bias

        self.op = self.select_op(quant_config, prefix)

        self.register_weights(params_dtype)

    def select_op(
        self, quant_config: Optional[QuantizationConfig] = None, prefix: str = ""
    ) -> LinearOpBase:
        """Selects the default operation for the linear layer.

        By default, this method returns a standard linear operation without quantization.

        Args:
            quant_config (Optional[QuantizationConfig]): Configuration for quantization.
            prefix (str, optional): Prefix for the layer name.

        Returns:
            LinearOpBase: A standard linear operation instance.

        Raises:
            NotImplementedError: If quantization is requested, as it is not supported for this
                layer.
        """
        _ = prefix
        if quant_config is not None:
            raise NotImplementedError("Quantization is not yet supported for LinearLayer.")
        return LinearOp()

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Abstract method for forward computation.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, input_size)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, output_size)`.

        Raises:
            NotImplementedError: Must be implemented in subclasses.
        """
        raise NotImplementedError("Subclasses must implement `forward()`.")


class LinearLayer(LinearLayerBase):
    """Fully connected linear layer implementation using the registered operation.

    This class extends `LinearLayerBase` to perform linear transformations with optional bias.
    """

    def register_weights(self, params_dtype: torch.dtype) -> None:
        """Creates and registers weights for the linear layer using the LinearOp instance.

        Args:
            params_dtype (torch.dtype): Data type for the weights.

        Shapes:
            - Weight tensor: Shape `(output_size, input_size)`
            - Bias tensor (optional): Shape `(output_size,)` if `use_bias` is True
        """
        weights = self.op.create_weights(
            input_size=self.input_size,
            output_size=self.output_size,
            params_dtype=params_dtype,
            use_bias=self.use_bias,
        )

        for name, weight in weights.items():
            self.register_parameter(name, weight)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Computes the forward pass of the linear layer.

        The input tensor is multiplied by the transposed weight matrix, and the bias
        is added if present.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, sequence_length, input_size)`.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, sequence_length, output_size)`.
        """
        return self.op.compute(x, **dict(self.named_parameters()))

    def extra_repr(self) -> str:
        """Provides a string representation for debugging.

        Returns:
            str: Formatted string with layer details.
        """
        return (
            f"in_features={self.input_size}, "
            f"output_features={self.output_size}, "
            f"bias={self.use_bias}"
        )
