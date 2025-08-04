from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

import torch
import torch.nn as nn
from transformers import LlamaConfig

from furiosa_models.architecture.layers import LinearLayer as Linear
from furiosa_models.architecture.layers.activation import SiLULayer as SiLU
from furiosa_models.architecture.layers.layernorm import RMSNormLayer as RMSNorm
from furiosa_models.architecture.layers.logits_processor import LogitsProcessor
from furiosa_models.architecture.layers.rotary_embedding import (
    RotaryEmbeddingLayer as RotaryEmbedding,
)
from furiosa_models.architecture.layers.vocab_embedding import (
    DEFAULT_VOCAB_PADDING_SIZE,
)
from furiosa_models.architecture.layers.vocab_embedding import (
    LMHeadLayer as LMHead,
)
from furiosa_models.architecture.layers.vocab_embedding import (
    VocabEmbeddingLayer as VocabEmbedding,
)
from furiosa_models.architecture.model_loader.weight_utils import default_weight_loader
from furiosa_models.architecture.models.serve import CausalModelServer
from furiosa_models.architecture.models.utils import (
    AutoWeightsLoader,
    append_prefix,
    make_layers,
)
from furiosa_models.attention import AttentionMetadataBase
from furiosa_models.attention.attention import AttentionLayer as Attention
from furiosa_models.config import CacheConfig, LLMConfig, QuantizationConfig


class LlamaMLP(nn.Module):
    """Llama MLP block implementation.

    Args:
        hidden_size (int): Hidden size of hidden states.
        intermediate_size (int): Intermediate size of hidden states.
        hidden_act (str): Activation function for the hidden states.
        bias (bool): Whether to use bias in the linear layers. Defaults to False.
        quant_config (Optional[QuantizationConfig]): Quantization configuration. Defaults to None.
        prefix (str): Prefix for the model. Defaults to "".

    Raises:
        ValueError: If the hidden activation function is not SiLU.
    """

    def __init__(
        self,
        hidden_size: int,
        intermediate_size: int,
        hidden_act: str,
        bias: bool = False,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.gate_proj = Linear(
            input_size=hidden_size,
            output_size=intermediate_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.gate_proj",
        )
        self.up_proj = Linear(
            input_size=hidden_size,
            output_size=intermediate_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.up_proj",
        )
        self.down_proj = Linear(
            input_size=intermediate_size,
            output_size=hidden_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.down_proj",
        )
        if hidden_act != "silu":
            raise ValueError(
                f"Only SiLU activation is supported for LlamaMLP, but got {hidden_act}."
            )
        self.act_fn = SiLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass of the MLP block.

        Args:
            x (torch.Tensor): Input hidden states.

        Returns:
            torch.Tensor: Output hidden states from the MLP block.
        """
        x = self.act_fn(self.gate_proj(x)) * self.up_proj(x)
        x = self.down_proj(x)
        return x


class LlamaAttention(nn.Module):
    """Llama attention block implementation.

    Args:
        config (LlamaConfig): Llama configuration.
        hidden_size (int): Hidden size.
        num_heads (int): Number of attention heads.
        num_kv_heads (int): Number of key-value heads.
        head_dim (Optional[int]): Head dimension of the attention heads. Defaults to None.
        max_position_embeddings (int): Maximum position embeddings. Defaults to 8192.
        rope_theta (float): Rope theta. Defaults to 10000.
        rope_scaling (Optional[Dict[str, Any]]): Rope scaling. Defaults to None.
        bias (bool): Whether to use bias in the linear layers. Defaults to False.
        cache_config (Optional[CacheConfig]): Cache configuration. Defaults to None.
        quant_config (Optional[QuantizationConfig]): Quantization configuration. Defaults to None.
        prefix (str): Prefix for the model. Defaults to "".

    Raises:
        ValueError: If the interleaved sliding window is not supported.
    """

    def __init__(
        self,
        config: LlamaConfig,
        hidden_size: int,
        num_heads: int,
        num_kv_heads: int,
        head_dim: Optional[int] = None,
        max_position_embeddings: int = 8192,
        rope_theta: float = 10000,
        rope_scaling: Optional[Dict[str, Any]] = None,
        bias: bool = False,
        cache_config: Optional[CacheConfig] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.hidden_size = hidden_size
        self.num_heads = num_heads
        self.num_kv_heads = max(1, num_kv_heads)

        self.head_dim = head_dim or self.hidden_size // self.num_heads
        assert self.head_dim % 2 == 0, "head_dim must be divisible by 2."

        partial_rotary_factor = getattr(config, "partial_rotary_factor", 1)
        self.rotary_dim = int(partial_rotary_factor * self.head_dim)

        self.q_size = self.num_heads * self.head_dim
        self.kv_size = self.num_kv_heads * self.head_dim
        self.scaling = self.head_dim**-0.5
        self.rope_theta = rope_theta
        self.max_position_embeddings = max_position_embeddings

        self.q_proj = Linear(
            input_size=hidden_size,
            output_size=self.q_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.q_proj",
        )
        self.k_proj = Linear(
            input_size=hidden_size,
            output_size=self.kv_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.k_proj",
        )
        self.v_proj = Linear(
            input_size=hidden_size,
            output_size=self.kv_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.v_proj",
        )
        self.o_proj = Linear(
            input_size=self.q_size,
            output_size=hidden_size,
            use_bias=bias,
            quant_config=quant_config,
            prefix=f"{prefix}.o_proj",
        )

        is_neox_style = True
        self.rotary_emb = RotaryEmbedding(
            self.head_dim,
            rotary_dim=self.rotary_dim,
            max_position=max_position_embeddings,
            base=rope_theta,
            rope_scaling=rope_scaling,
            is_neox_style=is_neox_style,
        )

        if hasattr(config, "interleaved_sliding_window"):
            interleaved_sliding_window = config.interleaved_sliding_window
            if isinstance(interleaved_sliding_window, int):
                sliding_window = interleaved_sliding_window
            else:
                raise ValueError(f"{type(interleaved_sliding_window)} is not supported.")
        else:
            sliding_window = None

        self.attn = Attention(
            self.num_heads,
            self.head_dim,
            self.scaling,
            num_kv_heads=self.num_kv_heads,
            cache_config=cache_config,
            per_layer_sliding_window=sliding_window,
            prefix=f"{prefix}.attn",
        )

    def forward(
        self,
        position_ids: torch.Tensor,
        hidden_states: torch.Tensor,
        kv_cache: Tuple[torch.Tensor, torch.Tensor],
        attention_metadata: AttentionMetadataBase,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward pass of the attention block.

        Args:
            position_ids (torch.Tensor): Positional IDs.
            hidden_states (torch.Tensor): Hidden states.
            kv_cache (Tuple[torch.Tensor, torch.Tensor]): Tuple of key-value caches.
            attention_metadata (AttentionMetadataBase): Attention metadata.
            attention_mask (Optional[torch.Tensor]): Attention mask. Defaults to None.

        Returns:
            torch.Tensor: Hidden states from the attention block.
        """
        q = self.q_proj(hidden_states)
        k = self.k_proj(hidden_states)
        v = self.v_proj(hidden_states)
        q, k = self.rotary_emb(position_ids, q, k)
        attn_output = self.attn(q, k, v, kv_cache, attention_metadata, attention_mask)
        output: torch.Tensor = self.o_proj(attn_output)
        return output


class LlamaDecoder(nn.Module):
    """Llama decoder block implementation.

    Args:
        config (LlamaConfig): Llama configuration.
        cache_config (Optional[CacheConfig], optional): Cache configuration. Defaults to None.
        quant_config (Optional[QuantizationConfig], optional): Quantization configuration. Defaults
            to None.
        prefix (str, optional): Prefix for the model. Defaults to "".
    """

    def __init__(
        self,
        config: LlamaConfig,
        cache_config: Optional[CacheConfig] = None,
        quant_config: Optional[QuantizationConfig] = None,
        prefix: str = "",
    ) -> None:
        super().__init__()
        self.hidden_size = config.hidden_size
        num_kv_heads = getattr(config, "num_key_value_heads", config.num_attention_heads)

        rope_theta = getattr(config, "rope_theta", 10000)
        rope_scaling = getattr(config, "rope_scaling", None)
        if rope_scaling is not None and getattr(config, "original_max_position_embeddings", None):
            rope_scaling["original_max_position_embeddings"] = (
                config.original_max_position_embeddings
            )
        max_position_embeddings = getattr(config, "max_position_embeddings", 8192)
        # Support abacusai/Smaug-72B-v0.1 with attention_bias
        # Support internlm/internlm-7b with bias
        attention_bias = getattr(config, "attention_bias", False) or getattr(config, "bias", False)
        mlp_bias = getattr(config, "mlp_bias", False)

        self.self_attn = LlamaAttention(
            config=config,
            hidden_size=self.hidden_size,
            num_heads=config.num_attention_heads,
            num_kv_heads=num_kv_heads,
            head_dim=getattr(
                config, "head_dim", None
            ),  # MistralConfig has an optional head_dim introduced by Mistral-Nemo
            max_position_embeddings=max_position_embeddings,
            rope_theta=rope_theta,
            rope_scaling=rope_scaling,
            bias=attention_bias,
            cache_config=cache_config,
            quant_config=quant_config,
            prefix=f"{prefix}.self_attn",
        )
        self.mlp = LlamaMLP(
            hidden_size=self.hidden_size,
            intermediate_size=config.intermediate_size,
            hidden_act=config.hidden_act,
            bias=mlp_bias,
            prefix=f"{prefix}.mlp",
        )
        self.input_layernorm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)
        self.post_attention_layernorm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def forward(
        self,
        position_ids: torch.Tensor,
        hidden_states: torch.Tensor,
        kv_cache: Tuple[torch.Tensor, torch.Tensor],
        attention_metadata: AttentionMetadataBase,
        attention_mask: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward pass of the decoder block.

        Args:
            position_ids (torch.Tensor): Positional IDs.
            hidden_states (torch.Tensor): Hidden states.
            kv_cache (Tuple[torch.Tensor, torch.Tensor]): Tuple of key-value caches.
            attention_metadata (AttentionMetadataBase): Attention metadata.
            attention_mask (Optional[torch.Tensor]): Attention mask. Defaults to None.

        Returns:
            torch.Tensor: Hidden states from the decoder block.
        """
        residual = hidden_states

        hidden_states = self.input_layernorm(hidden_states)

        hidden_states = self.self_attn(
            position_ids=position_ids,
            hidden_states=hidden_states,
            kv_cache=kv_cache,
            attention_metadata=attention_metadata,
            attention_mask=attention_mask,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        # NOTE: Ensuring consistency with the original LLaMA implementation
        #
        # Reference:
        #   - Meta LLaMA: https://github.com/meta-llama/llama/blob/1e8375848d3a3ebaccab83fd670b880864cf9409/llama/model.py#L409
        #   - Hugging Face Transformers: https://github.com/huggingface/transformers/blob/v4.49.0/src/transformers/models/llama/modeling_llama.py#L353
        #
        # - Issue: The vLLM implementation is missing the residual addition step.
        #   - vLLM source: https://github.com/vllm-project/vllm/blob/v0.7.3/vllm/model_executor/models/llama.py#L288-L291
        #
        # - Fix: Ensure that the residual connection is properly applied.
        hidden_states = hidden_states + residual

        return hidden_states


class LlamaModel(nn.Module):
    """Llama model implementation.

    Args:
        llm_config (LLMConfig): Llama configuration.
        prefix (str): Prefix for the model. Defaults to "".
    """

    def __init__(
        self,
        *,
        llm_config: LLMConfig,
        prefix: str = "",
    ) -> None:
        super().__init__()
        config = llm_config.model_config.hf_config
        cache_config = llm_config.cache_config
        quant_config = llm_config.quant_config
        lora_config = llm_config.lora_config

        self.config = config
        self.padding_idx = config.pad_token_id
        lora_vocab = (
            (lora_config.lora_extra_vocab_size * (lora_config.max_loras or 1)) if lora_config else 0
        )
        self.vocab_size = config.vocab_size + lora_vocab
        self.org_vocab_size = config.vocab_size

        self.embed_tokens = VocabEmbedding(
            self.vocab_size, config.hidden_size, orig_num_embeddings=config.vocab_size
        )

        self.layers = make_layers(
            num_layers=config.num_hidden_layers,
            layer_fn=lambda idx: LlamaDecoder(
                config=config,
                cache_config=cache_config,
                quant_config=quant_config,
                prefix=f"{prefix}.layers.{idx}",
            ),
        )
        self.norm = RMSNorm(config.hidden_size, eps=config.rms_norm_eps)

    def get_input_embeddings(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Get input embeddings from the model's embedding layer.

        Args:
            input_ids (torch.Tensor): Input token IDs.

        Returns:
            torch.Tensor: Input embeddings.
        """
        embeddings: torch.Tensor = self.embed_tokens(input_ids)
        return embeddings

    def forward(
        self,
        input_ids: Optional[torch.Tensor],
        position_ids: torch.Tensor,
        kv_caches: List[Tuple[torch.Tensor, torch.Tensor]],
        attention_metadata: AttentionMetadataBase,
        attention_masks: Optional[Union[torch.Tensor, List[torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward pass of the model.

        Args:
            input_ids (Optional[torch.Tensor]): Input token IDs.
            position_ids (torch.Tensor): Positional IDs.
            kv_caches (List[Tuple[torch.Tensor, torch.Tensor]]): List of key-value cache tuple.
            attention_metadata (AttentionMetadataBase): Attention metadata.
            attention_masks (Optional[Union[torch.Tensor, List[torch.Tensor]]]): Attention masks.
                Defaults to None.
            inputs_embeds (Optional[torch.Tensor], optional): Input embeddings. Defaults to None.

        Returns:
            torch.Tensor: Hidden states from the model.

        Raises:
            ValueError: If neither `input_ids` nor `inputs_embeds` is provided, or if the number of
                layers does not match the number of KV caches or attention masks.
        """
        if inputs_embeds is not None:
            hidden_states = inputs_embeds
        else:
            if input_ids is None:
                raise ValueError("Either input_ids or inputs_embeds must be provided.")
            hidden_states = self.get_input_embeddings(input_ids)

        if len(kv_caches) != len(self.layers):
            raise ValueError(
                "KV caches must match the number of layers. "
                f"Got {len(kv_caches)} but expected {len(self.layers)}."
            )

        if isinstance(attention_masks, list) and len(attention_masks) != len(self.layers):
            raise ValueError(
                "Attention masks must match the number of layers. "
                f"Got {len(attention_masks)} but expected {len(self.layers)}."
            )

        for i, layer in enumerate(self.layers):
            attention_mask = (
                attention_masks if not isinstance(attention_masks, list) else attention_masks[i]
            )
            hidden_states = layer(
                position_ids,
                hidden_states,
                kv_caches[i],
                attention_metadata,
                attention_mask,
            )

        # NOTE: Ensuring consistency with the original LLaMA implementation
        #
        # - Reference:
        # Reference:
        #   - Meta LLaMA: https://github.com/meta-llama/llama/blob/1e8375848d3a3ebaccab83fd670b880864cf9409/llama/model.py#L493
        #   - Hugging Face Transformers: https://github.com/huggingface/transformers/blob/v4.49.0/src/transformers/models/llama/modeling_llama.py#L611
        # - Issue: vLLM applies LayerNorm incorrectly before residual addition.
        #   - vLLM source: https://github.com/vllm-project/vllm/blob/v0.7.3/vllm/model_executor/models/llama.py#L368-L378
        #
        # - Fix: Remove the redundant residual addition to ensure correctness.
        hidden_states = self.norm(hidden_states)
        return hidden_states

    def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]) -> Set[str]:
        """Load weights from weights.

        Args:
            weights (Iterable[Tuple[str, torch.Tensor]]): Weights to load.

        Returns:
            Set[str]: Set of loaded parameters.
        """
        params_dict = dict(self.named_parameters())
        loaded_params: Set[str] = set()
        for name, loaded_weight in weights:
            if "rotary_emb.inv_freq" in name:
                continue
            if "rotary_emb.cos_cached" in name or "rotary_emb.sin_cached" in name:
                # Models trained using ColossalAI may include these tensors in
                # the checkpoint. Skip them.
                continue

            # Skip loading extra bias for GPTQ models.
            if name.endswith(".bias") and name not in params_dict:
                continue

            param = params_dict[name]
            weight_loader = getattr(param, "weight_loader", default_weight_loader)
            weight_loader(param, loaded_weight)
            loaded_params.add(name)
        return loaded_params


class LlamaForCausalLM(CausalModelServer):
    """Llama model for causal language modeling.

    Args:
        llm_config (LLMConfig): Llama configuration.
        prefix (str): Prefix for the model. Defaults to "".
    """

    def __init__(self, *, llm_config: LLMConfig, prefix: str = "") -> None:
        super().__init__(llm_config=llm_config)
        self.model = self._init_model(
            llm_config=self.llm_config, prefix=append_prefix(prefix, "model")
        )

        self.unpadded_vocab_size = self.config.vocab_size
        if self.lora_config:
            self.unpadded_vocab_size += self.lora_config.lora_extra_vocab_size
        self.lm_head = LMHead(
            self.unpadded_vocab_size,
            self.config.hidden_size,
            orig_num_embeddings=self.config.vocab_size,
            padding_size=(
                DEFAULT_VOCAB_PADDING_SIZE
                # We need bigger padding if using lora for kernel
                # compatibility
                if not self.lora_config
                else self.lora_config.lora_vocab_padding_size
            ),
        )
        if self.config.tie_word_embeddings:
            self.lm_head = self.lm_head.tie_weights(self.model.embed_tokens)
        logit_scale = getattr(self.config, "logit_scale", 1.0)
        self.logits_processor = LogitsProcessor(
            lm_head=self.lm_head,
            vocab_size=self.unpadded_vocab_size,
            org_vocab_size=self.config.vocab_size,
            scale=logit_scale,
        )

    def _init_model(self, llm_config: LLMConfig, prefix: str = "") -> LlamaModel:
        """Initialize the Llama model.

        Args:
            llm_config (LLMConfig): Llama configuration.
            prefix (str, optional): Prefix for the model. Defaults to "".

        Returns:
            LlamaModel: Initialized Llama model.
        """
        return LlamaModel(llm_config=llm_config, prefix=prefix)

    def get_input_embeddings(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Get input embeddings from the model's embedding layer.

        Args:
            input_ids (torch.Tensor): Input token IDs.

        Returns:
            torch.Tensor: Input embeddings.
        """
        return self.model.get_input_embeddings(input_ids)

    def forward(
        self,
        input_ids: Optional[torch.Tensor],
        position_ids: torch.Tensor,
        kv_caches: List[Tuple[torch.Tensor, torch.Tensor]],
        attention_metadata: AttentionMetadataBase,
        attention_masks: Optional[Union[torch.Tensor, List[torch.Tensor]]] = None,
        inputs_embeds: Optional[torch.Tensor] = None,
        compute_logits: bool = True,
    ) -> torch.Tensor:
        """Forward pass of the model.

        Args:
            input_ids (Optional[torch.Tensor]): Input token IDs.
            position_ids (torch.Tensor): Positional IDs.
            kv_caches (List[Tuple[torch.Tensor, torch.Tensor]]): List of key-value cache tuple.
            attention_metadata (AttentionMetadataBase): Attention metadata.
            attention_masks (Optional[Union[torch.Tensor, List[torch.Tensor]]]): Attention masks.
                Defaults to None.
            inputs_embeds (Optional[torch.Tensor], optional): Input embeddings. Defaults to None.
            compute_logits (bool, optional): Whether to compute logits. Defaults to True.

        Returns:
            torch.Tensor: Logits if `compute_logits` is True, otherwise the model output.
        """
        model_output: torch.Tensor = self.model(
            input_ids, position_ids, kv_caches, attention_metadata, attention_masks, inputs_embeds
        )
        if compute_logits:
            return self.compute_logits(model_output)
        return model_output

    def compute_logits(
        self,
        hidden_states: torch.Tensor,
    ) -> torch.Tensor:
        """Compute logits from hidden states.

        Args:
            hidden_states (torch.Tensor): Hidden states from the model.

        Returns:
            torch.Tensor: Logits computed from the hidden states.
        """
        return self.logits_processor.forward(hidden_states)

    def load_weights(self, weights: Iterable[Tuple[str, torch.Tensor]]) -> Set[str]:
        """Load weights from a checkpoint."""
        loader = AutoWeightsLoader(
            self,
            skip_prefixes=(["lm_head."] if self.config.tie_word_embeddings else None),
        )
        return loader.load_weights(weights)
