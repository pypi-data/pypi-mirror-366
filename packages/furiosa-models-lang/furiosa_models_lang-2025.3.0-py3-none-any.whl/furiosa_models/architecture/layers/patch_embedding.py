import math
from typing import Optional

import torch
import torch.nn as nn

from furiosa_models.architecture.layers import LayerBase
from furiosa_models.architecture.layers.linear import LinearLayer
from furiosa_models.architecture.layers.ops.patch_embedding import PixelShuffleOp, UnfoldOp
from furiosa_models.config import QuantizationConfig


class PatchEmbeddingLayerBase(LayerBase):
    """Base class for all patch embedding layers."""

    pass


class PatchUnfoldingLayer(PatchEmbeddingLayerBase):
    """Applies unfolding operation to extract flattened image patches.

    This layer converts an input image into a sequence of flattened patches using
    a sliding window (unfolding) operation. It is commonly used as the first stage
    in Vision Transformer architectures to tokenize images.

    Args:
        kernel_size (int): Size of each image patch (e.g., 16).
        dilation (int): Dilation factor between patch elements. Default: 1.
        padding (int): Zero-padding added to both sides. Default: 0.
        stride (int): Stride of the sliding window. Default: 1.
        prefix (str): Optional prefix for naming or logging.
    """

    def __init__(
        self,
        kernel_size: int,
        dilation: int = 1,
        padding: int = 0,
        stride: int = 1,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.kernel_size = kernel_size
        self.dilation = dilation
        self.padding = padding
        self.stride = stride

        self.op = self.select_op(prefix=prefix)

    def select_op(self, prefix: str) -> UnfoldOp:
        """Selects the Unfold operation to be used by the layer.

        Args:
            prefix (str): Optional prefix for naming or logging.

        Returns:
            UnfoldOp: Instance of the Unfold operation.
        """
        _ = prefix
        return UnfoldOp()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Extracts and flattens image patches using unfold.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, channels, height, width)`.

        Returns:
            torch.Tensor: Output tensor of shape
                `(batch_size, channels * kernel_size * kernel_size, num_patches)`,
                where `num_patches = (H_out × W_out)` based on stride and padding.
        """
        return self.op.compute(
            x,
            kernel_size=self.kernel_size,
            dilation=self.dilation,
            padding=self.padding,
            stride=self.stride,
        )

    def extra_repr(self) -> str:
        """Provides a string representation of the layer's parameters.

        Returns:
            str: Configuration of the PatchUnfoldingLayer.
        """
        return (
            f"kernel_size={self.kernel_size}, "
            f"dilation={self.dilation}, "
            f"padding={self.padding}, "
            f"stride={self.stride}"
        )


class PatchEmbeddingBlock(nn.Module):
    """Combines patch extraction and projection into embedding space.

    This module first extracts image patches using unfolding, then applies
    a linear projection to each flattened patch. It is typically used
    as the first block in ViT-style vision backbones.

    Args:
        num_channels (int): Number of channels in the input image.
        hidden_size (int): Size of the projected embedding for each patch.
        patch_size (int): Size of each image patch (e.g., 16).
        use_bias (bool): Whether to include a bias term in projection. Default: False.
        quant_config (Optional[QuantizationConfig]): Optional quantization settings.
        prefix (str): Optional prefix for naming or logging.
    """

    def __init__(
        self,
        num_channels: int,
        hidden_size: int,
        patch_size: int,
        use_bias: bool = False,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.unfold = PatchUnfoldingLayer(
            kernel_size=patch_size,
            stride=patch_size,
        )
        self.linear = LinearLayer(
            num_channels * patch_size * patch_size,
            hidden_size,
            use_bias=use_bias,
            quant_config=quant_config,
            prefix=prefix,
        )

    def forward(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """Applies patch extraction followed by linear projection.

        Args:
            pixel_values (torch.Tensor): Input tensor of shape `(B, C, H, W)`.

        Returns:
            torch.Tensor: Output tensor of shape `(B, Num_patches, hidden_size)`.
        """
        # (N, C, H, W) -> (N, C * kernel_size * kernel_size, L)
        # L is the number of patches
        hidden_states: torch.Tensor = self.unfold(pixel_values)
        # (N, C, L) -> (N, L, C)
        hidden_states = hidden_states.permute(0, 2, 1)
        # (N, L, C) -> (N, L, hidden_size)
        hidden_states = self.linear(hidden_states)
        return hidden_states


class PixelShuffleLayer(PatchEmbeddingLayerBase):
    """Applies pixel shuffle to upsample patch sequences.

    This layer reshapes a sequence of patch embeddings into a 2D layout, then upsamples
    the spatial resolution using the PixelShuffle operation. It is commonly used to
    reconstruct higher-resolution visual tokens after encoding.

    Args:
        ps_ratio (int): Upscaling factor for spatial dimensions.
    """

    def __init__(
        self,
        ps_ratio: int,
    ) -> None:
        super().__init__()
        self.ps_ratio = ps_ratio
        self.op = self.select_op()

    def select_op(self) -> PixelShuffleOp:
        """Selects the PixelShuffle operation to be used by the layer.

        Returns:
            PixelShuffleOp: Instance of the PixelShuffle operation.
        """
        return PixelShuffleOp()

    def forward(self, encoded_patches: torch.Tensor) -> torch.Tensor:
        """Applies pixel shuffle operation to reshaped patch embeddings.

        Args:
            encoded_patches (torch.Tensor): Input tensor of shape `(B, N_patches, C)`.

        Returns:
            torch.Tensor: Output tensor of shape `(B, New_patches, C_reduced)`,
                where `New_patches = N_patches * ps_ratio ** 2`, and
                `C_reduced = C // (ps_ratio ** 2)`.
        """
        assert encoded_patches.dim() == 3, "pixel shuffle requires encoded patches [B, N, C]"
        batch_size, num_patches, channels = encoded_patches.shape
        patch_size = int(math.sqrt(num_patches))

        # Reshape into (B, H, W, C)
        input_tensor = encoded_patches.view(batch_size, patch_size, patch_size, channels)

        # Shuffle the pixels into (B, H * ps_ratio, W * ps_ratio, C // (ps_ratio ** 2))
        # and permute to (B, C // (ps_ratio ** 2), H * ps_ratio, W * ps_ratio)
        shuffled = self.op.compute(input_tensor, ps_ratio=self.ps_ratio)
        pixel_shuffle_patches = shuffled.view(batch_size, -1, shuffled.size(-1))
        # Reshape back to (B, C // (ps_ratio ** 2), H * W * (ps_ratio ** 2))
        return pixel_shuffle_patches

    def extra_repr(self) -> str:
        """Provides a string representation of the layer's parameters.

        Returns:
            str: Configuration of the PixelShuffleLayer.
        """
        return f"pixel_shuffle_ratio={self.ps_ratio}"
