import torch
import torch.nn.functional as F

from furiosa_models.architecture.layers.ops import OpBase


class PatchEmbeddingOpBase(OpBase):
    """Patch embedding operation for vision transformers."""

    pass


class UnfoldOp(PatchEmbeddingOpBase):
    """Concrete implementation of the unfold operation for patch extraction.

    Applies the unfold operation using PyTorch's built-in `F.unfold()`.

    This operation extracts sliding local blocks (patches) from a batched input tensor
    and flattens each patch into a vector. It is commonly used in Vision Transformers (ViT)
    to convert an image into a sequence of patch embeddings.

    The input tensor is typically 4D with shape `(N, C, H, W)`, but more generally it can be
    `(N, C, *)`, where `*` represents arbitrary spatial dimensions.

    Mathematically, the output tensor has shape:
        (N, C × ∏(kernel_size), L)

    where:
        - N: batch size
        - C: number of channels
        - ∏(kernel_size): number of spatial elements per patch
        - L: number of patches extracted per image, calculated as:

            L = ∏ₙ ⌊(spatial_size[n] + 2 × padding[n] − dilation[n] × (kernel_size[n] − 1) − 1)
                / stride[n] + 1⌋

    Each column in the output represents one flattened patch.
    """

    def compute(
        self,
        x: torch.Tensor,
        kernel_size: int,
        dilation: int = 1,
        padding: int = 0,
        stride: int = 1,
    ) -> torch.Tensor:
        """Applies the unfold operation to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, channels, *spatial_dims)`.
            kernel_size (int): Size of the patch to extract.
            dilation (int): Dilation factor between elements in the patch. Default is 1.
            padding (int): Padding added to spatial dimensions. Default is 0.
            stride (int): Stride of the sliding window. Default is 1.

        Returns:
            torch.Tensor: Output tensor of shape
                `(batch_size, channels * ∏(kernel_size), num_patches)`,
            where each column is a flattened patch.
        """
        return F.unfold(
            x,
            kernel_size=kernel_size,
            dilation=dilation,
            padding=padding,
            stride=stride,
        )


class PixelShuffleOp(PatchEmbeddingOpBase):
    """Concrete implementation of the pixel shuffle operation for upsampling.

    Rearranges elements in a tensor of shape `(N, H, W, C)` to spatial dimensions using
    a given pixel shuffle ratio. This is commonly used to upsample patch-level representations
    into a higher-resolution spatial layout, often as part of a Vision Adapter module
    in multimodal models.

    The input tensor is expected to be in NHWC (channel-last) format, where:
        - N: batch size
        - H: height (typically number of patches along height)
        - W: width  (typically number of patches along width)
        - C: hidden/channel dimension

    The pixel shuffle rearranges the `C` channels into spatial dimensions by a factor
    of `ps_ratio`, assuming that:
        C = C_out × (ps_ratio ** 2)

    Mathematically, the output tensor has shape:
        (N, H × ps_ratio, W × ps_ratio, C_out)

    where:
        - C_out = C // (ps_ratio ** 2)

    The operation effectively reverses patchification, restoring higher-resolution spatial layout.

    Example:
        Input shape:  (N, 8, 8, 256), ps_ratio = 2
        Output shape: (N, 16, 16, 64)
    """

    def compute(self, x: torch.Tensor, ps_ratio: int) -> torch.Tensor:
        """Applies the pixel shuffle operation to the input tensor.

        Args:
            x (torch.Tensor): Input tensor of shape `(batch_size, height, width, channels)`.
            ps_ratio (int): Factor by which to upscale the spatial dimensions.

        Returns:
            torch.Tensor: Output tensor of shape `(batch_size, height * ps_ratio, width * ps_ratio,
                channels // (ps_ratio ** 2))`, where the spatial dimensions are upsampled by
                `ps_ratio` and channel dimension is reduced accordingly.
        """
        n, w, h, c = x.size()
        x = x.view(n, w, int(h * ps_ratio), int(c / ps_ratio))
        x = x.permute(0, 2, 1, 3).contiguous()
        x = x.view(
            n,
            int(h * ps_ratio),
            int(w * ps_ratio),
            int(c / (ps_ratio * ps_ratio)),
        )
        return x.permute(0, 2, 1, 3).contiguous()
