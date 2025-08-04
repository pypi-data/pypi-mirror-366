from typing import Optional

import torch
import torch.nn as nn

try:
    from transformers import Llama4VisionConfig
except ImportError as e:
    import transformers

    raise ImportError(
        "\n"
        "The module `furiosa_models.architecture.models.mllama4` is currently unavailable.\n"
        "This module is in preview and depends on features introduced in "
        "transformers >= 4.51.0.\n\n"
        "  Required: transformers >= 4.51.0\n"
        f"  Detected: transformers == {transformers.__version__}\n\n"
        "To use this module, it is recommended to manually install the required version:\n"
        "  make install-preview\n"
    ) from e

from furiosa_models.architecture.layers import LinearLayer as Linear
from furiosa_models.architecture.layers.activation import GELULayer as GELU
from furiosa_models.architecture.layers.layernorm import LayerNormLayer as LayerNorm
from furiosa_models.architecture.layers.patch_embedding import PatchEmbeddingBlock as PatchEmbedding
from furiosa_models.architecture.layers.patch_embedding import PixelShuffleLayer as PixelShuffle
from furiosa_models.architecture.layers.rotary_embedding import (
    RotaryEmbeddingLayer as RotaryEmbedding,
)
from furiosa_models.architecture.models.utils import (
    make_layers,
)
from furiosa_models.attention.attention import VisionAttentionLayer as VisionAttention
from furiosa_models.config import QuantizationConfig


class Llama4VisionMLP(nn.Module):
    """Llaama4 Vision MLP block implementation.

    Args:
        input_size (int): Input size of the MLP block.
        intermediate_size (int): Intermediate size of the MLP block.
        output_size (int): Output size of the MLP block.
        bias (bool): Whether to use bias in the linear layers. Defaults to False.
        output_activation (bool): Whether to apply activation on the output. Defaults to False.
        quant_config (Optional[QuantizationConfig], optional): Quantization configuration. Defaults
            to None.
        prefix (str): Prefix for naming layers. Defaults to "".
    """

    def __init__(
        self,
        input_size: int,
        intermediate_size: int,
        output_size: int,
        bias: bool = False,
        output_activation: bool = False,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.fc1 = Linear(
            input_size=input_size,
            output_size=intermediate_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.fc1",
        )
        self.fc2 = Linear(
            input_size=intermediate_size,
            output_size=output_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.fc2",
        )
        self.act_fn = GELU(approximate="none")
        self.output_activation = output_activation

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Forward pass of the MLP block.

        Args:
            hidden_states (torch.Tensor): Input hidden states.

        Returns:
            torch.Tensor: Output hidden states from the MLP block.
        """
        hidden_states = self.fc1(hidden_states)
        hidden_states = self.act_fn(hidden_states)
        hidden_states = self.fc2(hidden_states)
        if self.output_activation:
            hidden_states = self.act_fn(hidden_states)
        return hidden_states


class Llama4VisionPixelShuffleMLP(nn.Module):
    """Llama4 Vision Pixel Shuffle MLP implementation.

    Args:
        input_size (int): Input size of the MLP block.
        intermediate_size (int): Intermediate size of the MLP block.
        output_size (int): Output size of the MLP block.
        bias (bool): Whether to use bias in the linear layers.
        pixel_shuffle_ratio (int): Ratio for pixel shuffling.
        quant_config (Optional[QuantizationConfig]): Quantization configuration.
        prefix (str): Prefix for naming layers. Defaults to "".
    """

    def __init__(
        self,
        input_size: int,
        intermediate_size: int,
        output_size: int,
        bias: bool,
        pixel_shuffle_ratio: int,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.pixel_shuffle_ratio = pixel_shuffle_ratio
        self.pixel_shuffle = PixelShuffle(pixel_shuffle_ratio)

        self.inner_dim = int(intermediate_size / (self.pixel_shuffle_ratio**2))
        self.output_dim = output_size

        # Mapping from config:
        # - intermediate_size  = config.projector_input_dim
        # - output_size        = config.projector_output_dim  (Meta-style: intermediate == output)
        # https://github.com/meta-llama/llama-models/blob/v0.2.0/models/llama4/vision/embedding.py#L60-L72
        assert intermediate_size == output_size, (
            f"Llama4VisionPixelShuffleMLP assumes intermediate_size == output_size, "
            f"but got {intermediate_size} != {output_size}"
        )

        self.mlp = Llama4VisionMLP(
            input_size=input_size,
            intermediate_size=intermediate_size,
            output_size=output_size,
            bias=bias,
            output_activation=True,
            quant_config=quant_config,
            prefix=f"{prefix}.mlp",
        )

    def forward(self, encoded_patches: torch.Tensor) -> torch.Tensor:
        """Forward pass of the pixel shuffle MLP block.

        Args:
            encoded_patches (torch.Tensor): Encoded patches.

        Returns:
            torch.Tensor: Output hidden states from the pixel shuffle MLP block.
        """
        encoded_patches = self.pixel_shuffle(encoded_patches)
        hidden_states: torch.Tensor = self.mlp(encoded_patches)
        return hidden_states


class Llama4VisionAttention(nn.Module):
    """Llama4 Vision Attention block implementation.

    Args:
        config (Llama4VisionConfig): Llama4 Vision configuration.
        hidden_size (int): Hidden size.
        num_heads (int): Number of attention heads.
        quant_config (Optional[QuantizationConfig]): Quantization configuration.
        prefix (str): Prefix for naming layers. Defaults to "".
    """

    def __init__(
        self,
        config: Llama4VisionConfig,
        hidden_size: int,
        num_heads: int,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.embed_dim = hidden_size
        self.num_heads = num_heads
        self.head_dim = self.embed_dim // self.num_heads

        self.q_size = self.num_heads * self.head_dim
        self.kv_size = self.num_heads * self.head_dim
        self.attention_dropout = config.attention_dropout
        self.scaling = self.head_dim**-0.5

        self.rotary_dim = self.head_dim // 2
        # number of image patches
        self.max_positional_embeddings = (config.image_size // config.patch_size) ** 2
        self.rope_theta = config.rope_theta
        self.rope_scaling = {"rope_type": "llama4"}

        self.q_proj = Linear(
            input_size=self.embed_dim,
            output_size=self.num_heads * self.head_dim,
            use_bias=True,
            quant_config=quant_config,
            prefix=f"{prefix}.q_proj",
        )
        self.k_proj = Linear(
            input_size=self.embed_dim,
            output_size=self.num_heads * self.head_dim,
            use_bias=True,
            quant_config=quant_config,
            prefix=f"{prefix}.k_proj",
        )
        self.v_proj = Linear(
            input_size=self.embed_dim,
            output_size=self.num_heads * self.head_dim,
            use_bias=True,
            quant_config=quant_config,
            prefix=f"{prefix}.v_proj",
        )
        self.o_proj = Linear(
            input_size=self.num_heads * self.head_dim,
            output_size=self.embed_dim,
            use_bias=True,
            quant_config=quant_config,
            prefix=f"{prefix}.o_proj",
        )

        self.attn = VisionAttention(self.num_heads, self.head_dim, self.scaling)

        self.rotary_emb = RotaryEmbedding(
            head_size=self.head_dim,
            rotary_dim=self.rotary_dim,
            max_position=self.max_positional_embeddings,
            base=self.rope_theta,
            rope_scaling=self.rope_scaling,
            dtype=torch.complex64,  # important
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of the attention block.

        Args:
            hidden_states (torch.Tensor): Hidden states.

        Returns:
            torch.Tensor: Output hidden states from the attention block.
        """
        input_shape = hidden_states.shape[:-1]
        hidden_shape = (*input_shape, -1, self.head_dim)

        q = self.q_proj(hidden_states).view(hidden_shape)
        k = self.k_proj(hidden_states).view(hidden_shape)
        v = self.v_proj(hidden_states).view(hidden_shape)

        q, k = self.rotary_emb(None, q, k)

        attn_output: torch.Tensor = self.attn(q, k, v).reshape(*input_shape, -1).contiguous()
        attn_output = self.o_proj(attn_output)

        return attn_output


class Llama4VisionEncoderLayer(nn.Module):
    """Llama4 Vision Encoder layer implementation.

    Args:
        config (Llama4VisionConfig): Llama4 Vision configuration.
        quant_config (Optional[QuantizationConfig]): Quantization configuration.
        prefix (str): Prefix for naming layers. Defaults to "".

    """

    def __init__(
        self,
        config: Llama4VisionConfig,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.hidden_size = config.hidden_size
        self.num_attention_heads = config.num_attention_heads
        self.intermediate_size = config.intermediate_size

        self.self_attn = Llama4VisionAttention(
            config,
            hidden_size=config.hidden_size,
            num_heads=config.num_attention_heads,
            quant_config=quant_config,
            prefix=f"{prefix}.self_attn",
        )
        self.mlp = Llama4VisionMLP(
            input_size=config.hidden_size,
            intermediate_size=config.intermediate_size,
            output_size=config.hidden_size,
            bias=True,
            output_activation=False,
            quant_config=quant_config,
            prefix=f"{prefix}.mlp",
        )

        self.input_layernorm = LayerNorm(config.hidden_size)
        self.post_attention_layernorm = LayerNorm(config.hidden_size)

    def forward(
        self,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of the encoder layer.

        Args:
            hidden_states (torch.Tensor): Hidden states.

        Returns:
            torch.Tensor: Output hidden states from the encoder layer.

        """
        # Self Attention
        residual = hidden_states
        hidden_states = self.input_layernorm(hidden_states)
        hidden_states = self.self_attn(hidden_states)
        hidden_states = residual + hidden_states

        # Feed forward
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        return hidden_states


class Llama4VisionEncoder(nn.Module):
    """Llama4 Vision Encoder implementation.

    Args:
        config (Llama4VisionConfig): Llama4 Vision configuration.
        quant_config (Optional[QuantizationConfig]): Quantization configuration.
        prefix (str): Prefix for naming layers. Defaults to "".
    """

    def __init__(
        self,
        config: Llama4VisionConfig,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.layers = make_layers(
            num_layers=config.num_hidden_layers,
            layer_fn=lambda idx: Llama4VisionEncoderLayer(
                config=config,
                quant_config=quant_config,
                prefix=f"{prefix}.layers.{idx}",
            ),
        )

    def forward(
        self,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of the encoder.

        Args:
            hidden_states (torch.Tensor): Hidden states.

        Returns:
            torch.Tensor: Output hidden states from the encoder.
        """
        for encoder_layer in self.layers:
            layer_outputs = encoder_layer(hidden_states)
            hidden_states = layer_outputs

        return hidden_states


class Llama4VisionModel(nn.Module):
    """Llama4 Vision Model implementation.

    Args:
        config (Llama4VisionConfig): Llama4 Vision configuration.
        quant_config (Optional[QuantizationConfig]): Quantization configuration.
        prefix (str): Prefix for naming layers. Defaults to "".
    """

    def __init__(
        self,
        config: Llama4VisionConfig,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.config = config
        self.image_size = config.image_size
        self.patch_size = config.patch_size
        self.hidden_size = config.hidden_size
        self.num_channels = config.num_channels

        self.num_patches = (self.image_size // self.patch_size) ** 2 + 1
        self.scale = config.hidden_size**-0.5

        self.patch_embedding = PatchEmbedding(
            num_channels=config.num_channels,
            hidden_size=config.hidden_size,
            patch_size=config.patch_size,
            quant_config=quant_config,
            prefix=f"{prefix}.patch_embedding",
        )

        self.class_embedding = nn.Parameter(
            self.scale * torch.randn(self.hidden_size), requires_grad=False
        )
        self.positional_embedding_vlm = nn.Parameter(
            self.scale * torch.randn(self.num_patches, self.hidden_size), requires_grad=False
        )

        # layer norms
        self.layernorm_pre = LayerNorm(self.hidden_size, eps=1e-5)
        self.layernorm_post = LayerNorm(self.hidden_size, eps=1e-5)

        # encoders
        self.model = Llama4VisionEncoder(
            config, quant_config=quant_config, prefix=f"{prefix}.model"
        )
        self.vision_adapter = Llama4VisionPixelShuffleMLP(
            input_size=config.intermediate_size,
            intermediate_size=config.projector_input_dim,
            output_size=config.projector_output_dim,
            bias=config.multi_modal_projector_bias,
            pixel_shuffle_ratio=config.pixel_shuffle_ratio,
            quant_config=quant_config,
            prefix=f"{prefix}.vision_adapter",
        )

    def forward(
        self,
        pixel_values: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of the Llama4 Vision Model.

        Args:
            pixel_values (torch.Tensor): Input pixel values.

        Returns:
            torch.Tensor: Output hidden states from the Llama4 Vision Model.
        """
        # Patch embedding
        hidden_state: torch.Tensor = self.patch_embedding(pixel_values)
        num_tiles, num_patches, hidden_dim = hidden_state.shape

        # Add cls token
        class_embedding = self.class_embedding.expand(
            hidden_state.shape[0], 1, hidden_state.shape[-1]
        )
        hidden_state = torch.cat([hidden_state, class_embedding], dim=1)
        num_patches += 1

        # Position embeddings
        hidden_state = hidden_state.reshape(
            num_tiles,
            1,
            num_patches,
            hidden_dim,
        )
        positional_embedding = self.positional_embedding_vlm.to(
            dtype=hidden_state.dtype, device=hidden_state.device
        )
        hidden_state = hidden_state + positional_embedding
        hidden_state = self.layernorm_pre(hidden_state)
        hidden_state = hidden_state.view(num_tiles, -1, hidden_dim)

        # Apply encoder
        hidden_state = self.model(hidden_state)
        hidden_state = self.layernorm_post(hidden_state)

        # Remove CLS token output
        hidden_state = hidden_state[:, :-1, :]

        # now, we use Llama4VisionPixelShuffle + mlp to project embeddings
        hidden_state = self.vision_adapter(hidden_state)

        return hidden_state
