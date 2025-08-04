from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import torch
from transformers import PretrainedConfig

from furiosa_models.config import (
    CacheConfig,
    LLMConfig,
    LoRAConfig,
    ModelConfig,
    QuantizationConfig,
)
from furiosa_models.dtype import ALLOWED_MODEL_DTYPE, normalize_dtype

allowed_model_dtype_str = list(ALLOWED_MODEL_DTYPE.keys())
allowed_model_dtype_torch = list(set(ALLOWED_MODEL_DTYPE.values()))


@dataclass
class CausalModelArgs:
    """Arguments to create a serving-ready causal language model.

    Attributes:
        model_or_config (Union[str, PretrainedConfig]): HuggingFace Hub model ID (str) or
            PretrainedConfig instance.
        model_dtype (Union[str, torch.dtype]): Data type for both model parameters and activations
            without using AMP. "auto" follows the `torch_dtype` from the model config.
            (Allowed: "auto", "bfloat16", "float16", "float32". Default: "bfloat16")
        kv_cache_dtype (Union[str, torch.dtype]): Data type for key-value caches, must match
            model_dtype.
            (Allowed: "bfloat16", "float16", or "float32". Default: "bfloat16")
        block_size (int): Block size for key-value cache memory layout. (Default: 1)
    """

    model_or_config: Union[str, PretrainedConfig]
    model_dtype: Union[str, torch.dtype] = "bfloat16"
    kv_cache_dtype: Union[str, torch.dtype] = "bfloat16"
    block_size: int = 1

    def __post_init__(self) -> None:
        """Post-initialization checks for causal model arguments."""
        if self.model_dtype != "auto":
            self.model_dtype = normalize_dtype(self.model_dtype)

        self.kv_cache_dtype = normalize_dtype(self.kv_cache_dtype)

        if self.model_dtype not in ["auto", *allowed_model_dtype_torch]:
            raise ValueError(
                f"Invalid model_dtype: {self.model_dtype!r}. "
                f"Allowed values are: {['auto', *allowed_model_dtype_torch]}."
            )
        if self.kv_cache_dtype not in allowed_model_dtype_torch:
            raise ValueError(
                f"Invalid kv_cache_dtype: {self.kv_cache_dtype!r}. "
                f"Allowed values are: {allowed_model_dtype_torch}."
            )
        if self.model_dtype != self.kv_cache_dtype:
            raise ValueError(
                f"dtype ({self.model_dtype!r}) and kv_cache_dtype ({self.kv_cache_dtype!r}) "
                "must match."
            )

    def create_model_config(self) -> ModelConfig:
        """Create model configuration."""
        if self.model_dtype == "auto":
            dtype: Union[str, torch.dtype] = "auto"  # Special case: keep as string
        else:
            dtype = normalize_dtype(self.model_dtype)

        fields: Dict[str, Any] = {
            "dtype": dtype,
        }
        if isinstance(self.model_or_config, str):
            fields["model"] = self.model_or_config
        elif isinstance(self.model_or_config, PretrainedConfig):
            fields["hf_config_override"] = self.model_or_config
        else:
            raise TypeError(f"Unsupported type for model: {type(self.model_or_config)}")

        return ModelConfig(**fields)

    def create_cache_config(self) -> CacheConfig:
        """Create cache configuration."""
        dtype = normalize_dtype(self.kv_cache_dtype)
        return CacheConfig(
            cache_dtype=dtype,
            block_size=self.block_size,
        )

    def create_lora_config(self) -> Optional[LoRAConfig]:
        """Create LoRA configuration."""
        raise NotImplementedError("LoRA support is not implemented yet.")

    def create_quant_config(self) -> Optional[QuantizationConfig]:
        """Create quantization configuration."""
        raise NotImplementedError("Quantization support is not implemented yet.")

    def to_llm_config(self) -> LLMConfig:
        """Convert causal model arguments to LLMConfig."""
        return LLMConfig(
            model_config=self.create_model_config(),
            cache_config=self.create_cache_config(),
            lora_config=None,  # Future: self.create_lora_config()
            quant_config=None,  # Future: self.create_quant_config()
        )
