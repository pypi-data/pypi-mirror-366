# copied and edited from vllm/config.py
# https://github.com/vllm-project/vllm/blob/v0.6.6/vllm/config.py

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List, Optional, Tuple, Union

import torch
from transformers import PretrainedConfig

from furiosa_models.dtype import STR_DTYPE_TO_TORCH_DTYPE as _STR_DTYPE_TO_TORCH_DTYPE
from furiosa_models.transformers_utils.config import (
    ConfigFormat,
    get_config,
    get_hf_text_config,
    get_sentence_transformer_tokenizer_config,
)

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Configuration for the model.

    Attributes:
        model (str): Name or path of the huggingface model to use.
        tokenizer (str): Name or path of the huggingface tokenizer to use.
        tokenizer_mode (str): Tokenizer mode to use. "auto" will use the fast toke
            "slow" will use the slow tokenizer, and "mistral" always use the tokenizer from
            `mistral_common`.
        trust_remote_code (bool): Whether to trust the remote code. If False, will only use
            local code.
        dtype (Union[str, torch.dtype]): Data type to use for the model weights and activations.
            "auto" option will use FP16 precision for FP32 and FP16 models, and BF16 precision
            for BF16 models.
        seed (int): Random seed to use for reproducibility.
        revision(Optional[str]): The specific model version to use. It can be a branch name,
            a tag name, or a commit id. If unspecified, will use the default
            version.
        code_revision(Optional[str]): The specific code version to use. It can be a branch name, or
            a tag name. If unspecified, will use the default version.
        tokenizer_revision(Optional[str]): The specific tokenizer version to use. It can be a
            branch name, or a tag name. If unspecified, will use the default version.
        max_model_len (Optional[int]): Maximum length of a sequence (including prompt and output)
            that the model can handle. If None, will be derived from the model.
        disable_sliding_window (bool): Whether to disable sliding window for models that support it.
        spec_target_max_model_len (Optional[int]): Maximum length of a sequence (including prompt
            and output) that spec decoding draft models.
        config_format (ConfigFormat): The format of the model configuration.
        logits_processor_config (Optional[str]): The configuration for the logits processor.
        hf_config_override (Optional[str]): The configuration for the huggingface model.
        generation_config (Optional[str]): The configuration for the generation.
    """

    model: str = None
    tokenizer: str = None
    tokenizer_mode: str = "auto"
    trust_remote_code: bool = True
    dtype: Union[str, torch.dtype] = "float32"
    seed: int = 42
    revision: Optional[str] = None
    code_revision: Optional[str] = None
    tokenizer_revision: Optional[str] = None
    max_model_len: Optional[int] = None
    disable_sliding_window: bool = False
    spec_target_max_model_len: Optional[int] = None
    config_format: ConfigFormat = ConfigFormat.AUTO
    logits_processor_config: Optional[str] = None
    hf_config_override: Optional[str] = None
    generation_config: Optional[str] = None

    def __post_init__(self) -> None:
        """Post-initialization function."""
        self.tokenizer_revision = self.tokenizer_revision or self.revision

        if self.model is not None:
            self.hf_config = get_config(
                self.model,
                self.trust_remote_code,
                self.revision,
                self.code_revision,
                self.config_format,
            )
        else:
            self.hf_config = self.hf_config_override

        self.hf_text_config = get_hf_text_config(self.hf_config)
        self.encoder_config = self._get_encoder_config() if self.model is not None else None
        self.dtype = self._get_and_verify_dtype(self.hf_text_config, self.dtype)

        sliding_window = getattr(self.hf_text_config, "sliding_window", None)
        has_interleaved_attention = (sliding_window is not None) and (
            isinstance(sliding_window, list)
            or (self.hf_text_config.model_type in ["gemma2", "cohere2"])
        )

        if not self.disable_sliding_window and has_interleaved_attention:
            # if envs.VLLM_ATTENTION_BACKEND == "XFORMERS":
            #     sliding_window_len_min = get_min_sliding_window(
            #         self.hf_text_config.sliding_window)

            #     logger.warning_once(
            #         f"{self.hf_text_config.model_type} has interleaved "
            #         "attention, which is currently not supported by the "
            #         "XFORMERS backend. Disabling sliding window and capping "
            #         "the max length to the sliding window size "
            #         f"({sliding_window_len_min}).")
            #     self.disable_sliding_window = True
            # else:
            # for a model with interleaved attention,
            # the scheduler and the model treat it as full attention
            # (i.e., not dropping any tokens outside the window).
            # only the attention layer itself is aware of the sliding
            # window, and use the window size to compute the attention.
            self.hf_text_config.interleaved_sliding_window = sliding_window
            delattr(self.hf_text_config, "sliding_window")
            sliding_window = None

        self.max_model_len = self._get_and_verify_max_len(
            hf_config=self.hf_text_config,
            max_model_len=self.max_model_len,
            disable_sliding_window=self.disable_sliding_window,
            sliding_window_len=self._get_hf_config_sliding_window(),
            spec_target_max_model_len=self.spec_target_max_model_len,
            encoder_config=self.encoder_config,
        )

    def _get_hf_config_sliding_window(self) -> Union[Optional[int], List[Optional[int]]]:
        """Get the sliding window size, or None if disabled."""
        # Some models, like Qwen2 and Qwen1.5, use `use_sliding_window` in
        # addition to sliding window size. We check if that field is present
        # and if it's False, return None.
        if (
            hasattr(self.hf_text_config, "use_sliding_window")
            and not self.hf_text_config.use_sliding_window
        ):
            return None
        return getattr(self.hf_text_config, "sliding_window", None)

    def _get_sliding_window(self) -> Optional[Union[int, List[Optional[int]]]]:
        """Get the sliding window size, or None if disabled."""
        # If user disables sliding window, return None.
        if self.disable_sliding_window:
            return None
        # Otherwise get the value from the hf config.
        return self._get_hf_config_sliding_window()

    def _get_encoder_config(self) -> Optional[Dict]:
        return get_sentence_transformer_tokenizer_config(self.model, self.revision)

    def _get_and_verify_dtype(
        self,
        config: PretrainedConfig,
        dtype: Union[str, torch.dtype],
    ) -> torch.dtype:
        # NOTE: getattr(config, "torch_dtype", torch.float32) is not correct
        # because config.torch_dtype can be None.
        config_dtype = getattr(config, "torch_dtype", None)
        if config_dtype is None:
            config_dtype = torch.float32

        if isinstance(dtype, str):
            dtype = dtype.lower()
            if dtype == "auto":
                if config_dtype == torch.float32:
                    if config.model_type == "gemma2":
                        logger.info(
                            "For Gemma 2, we downcast float32 to bfloat16 instead "
                            "of float16 by default. Please specify `dtype` if you "
                            "want to use float16."
                        )
                        torch_dtype = torch.bfloat16
                    else:
                        # Following the common practice, we use float16 for float32
                        # models.
                        torch_dtype = torch.float16
                else:
                    torch_dtype = config_dtype
            else:
                if dtype not in _STR_DTYPE_TO_TORCH_DTYPE:
                    raise ValueError(f"Unknown dtype: {dtype}")
                torch_dtype = _STR_DTYPE_TO_TORCH_DTYPE[dtype]
        elif isinstance(dtype, torch.dtype):
            torch_dtype = dtype
        else:
            raise ValueError(f"Unknown dtype: {dtype}")

        # Verify the dtype.
        if torch_dtype != config_dtype:
            if torch_dtype == torch.float32:
                # Upcasting to float32 is allowed.
                logger.warning("Upcasting %s to %s.", config_dtype, torch_dtype)
                pass
            elif config_dtype == torch.float32:
                # Downcasting from float32 to float16 or bfloat16 is allowed.
                logger.warning("Downcasting %s to %s.", config_dtype, torch_dtype)
                pass
            else:
                # Casting between float16 and bfloat16 is allowed with a warning.
                logger.warning("Casting %s to %s.", config_dtype, torch_dtype)

        return torch_dtype

    def _get_and_verify_max_len(
        self,
        hf_config: PretrainedConfig,
        max_model_len: Optional[int],
        disable_sliding_window: bool,
        sliding_window_len: Optional[Union[int, List[Optional[int]]]],
        spec_target_max_model_len: Optional[int] = None,
        encoder_config: Optional[Any] = None,
    ) -> int:
        """Get and verify the model's maximum length."""
        derived_max_model_len = float("inf")
        possible_keys = [
            # OPT
            "max_position_embeddings",
            # GPT-2
            "n_positions",
            # MPT
            "max_seq_len",
            # ChatGLM2
            "seq_length",
            # Command-R
            "model_max_length",
            # Whisper
            "max_target_positions",
            # Others
            "max_sequence_length",
            "max_seq_length",
            "seq_len",
        ]
        # Choose the smallest "max_length" from the possible keys.
        max_len_key = None
        for key in possible_keys:
            max_len = getattr(hf_config, key, None)
            if max_len is not None:
                max_len_key = key if max_len < derived_max_model_len else max_len_key
                derived_max_model_len = min(derived_max_model_len, max_len)

        # If sliding window is manually disabled, max_length should be less
        # than the sliding window length in the model config.
        if disable_sliding_window and sliding_window_len is not None:
            sliding_window_len_min = self._get_min_sliding_window(sliding_window_len)
            max_len_key = (
                "sliding_window" if sliding_window_len_min < derived_max_model_len else max_len_key
            )
            derived_max_model_len = min(derived_max_model_len, sliding_window_len_min)

        # If none of the keys were found in the config, use a default and
        # log a warning.
        if derived_max_model_len == float("inf"):
            if max_model_len is not None:
                # If max_model_len is specified, we use it.
                return max_model_len

            if spec_target_max_model_len is not None:
                # If this is a speculative draft model, we use the max model len
                # from the target model.
                return spec_target_max_model_len

            default_max_len = 2048
            logger.warning(
                "The model's config.json does not contain any of the following "
                "keys to determine the original maximum length of the model: "
                "%s. Assuming the model's maximum length is %d.",
                possible_keys,
                default_max_len,
            )
            derived_max_model_len = default_max_len

        rope_scaling = getattr(hf_config, "rope_scaling", None)
        if rope_scaling is not None:
            # No need to consider "type" key because of patch_rope_scaling when
            # loading HF config
            rope_type = rope_scaling["rope_type"]

            if rope_type not in ("su", "longrope", "llama3"):
                if disable_sliding_window:
                    # TODO(robertgshaw): Find a model that supports rope_scaling
                    # with sliding window to see if this case should be allowed.
                    raise NotImplementedError(
                        "Disabling sliding window is not supported for models "
                        "with rope_scaling. Please raise an issue so we can "
                        "investigate."
                    )

                # NOTE: rope_type == "default" does not define factor
                # https://github.com/huggingface/transformers/blob/v4.45.2/src/transformers/modeling_rope_utils.py
                scaling_factor = rope_scaling.get("factor", 1.0)

                if rope_type == "yarn":
                    derived_max_model_len = rope_scaling["original_max_position_embeddings"]
                derived_max_model_len *= scaling_factor

        if encoder_config and "max_seq_length" in encoder_config:
            derived_max_model_len = encoder_config["max_seq_length"]

        # If the user specified a max length, make sure it is smaller than the
        # derived length from the HF model config.
        if max_model_len is None:
            max_model_len = int(derived_max_model_len)
        elif max_model_len > derived_max_model_len:
            # Some models might have a separate key for specifying model_max_length
            # that will be bigger than derived_max_model_len. We compare user input
            # with model_max_length and allow this override when it's smaller.
            model_max_length = getattr(hf_config, "model_max_length", None)
            if model_max_length is not None and max_model_len <= model_max_length:
                if disable_sliding_window:
                    # TODO(robertgshaw): Find a model that has model_max_length
                    # with sliding window to see if this case should be allowed.
                    raise NotImplementedError(
                        "Disabling sliding window is not supported for models "
                        "model_max_length in the config. Please raise an issue "
                        "so we can investigate."
                    )
            else:
                msg = (
                    f"User-specified max_model_len ({max_model_len}) is greater "
                    f"than the derived max_model_len ({max_len_key}="
                    f"{derived_max_model_len} or model_max_length="
                    f"{model_max_length} in model's config.json). This may lead "
                    "to incorrect model outputs or CUDA errors."
                )
                # if envs.VLLM_ALLOW_LONG_MAX_MODEL_LEN:
                #     logger.warning(
                #         "%s Make sure the value is correct and within the "
                #         "model context size.", msg)
                # else:
                raise ValueError(
                    f"{msg} To allow overriding this maximum, set "
                    "the env var VLLM_ALLOW_LONG_MAX_MODEL_LEN=1"
                )
        return int(max_model_len)

    def _get_min_sliding_window(self, sliding_window: Union[int, List[Optional[int]]]) -> int:
        if isinstance(sliding_window, list):
            return min(s for s in sliding_window if s is not None)

        return sliding_window


@dataclass
class CacheConfig:
    """Configuration for the cache.

    Attributes:
        cache_dtype (torch.dtype): Data type to use for the cache.
        block_size (int): Number of slots per block.
    """

    cache_dtype: torch.dtype
    block_size: int


class LoadFormat(str, Enum):
    """Format of the model weights to load."""

    AUTO = "auto"
    PT = "pt"
    SAFETENSORS = "safetensors"
    NPCACHE = "npcache"
    DUMMY = "dummy"
    TENSORIZER = "tensorizer"
    SHARDED_STATE = "sharded_state"
    GGUF = "gguf"
    BITSANDBYTES = "bitsandbytes"
    MISTRAL = "mistral"
    RUNAI_STREAMER = "runai_streamer"


@dataclass
class LoadConfig:
    """Configuration for loading the model weights."""

    load_format: Union[str, LoadFormat] = LoadFormat.AUTO
    download_dir: Optional[str] = None
    model_loader_extra_config: Optional[Union[str, dict]] = field(default_factory=dict)
    ignore_patterns: Optional[Union[List[str], str]] = None

    def __post_init__(self) -> None:
        """Post-initialization function."""
        model_loader_extra_config = self.model_loader_extra_config or {}
        if isinstance(model_loader_extra_config, str):
            self.model_loader_extra_config = json.loads(model_loader_extra_config)
        if isinstance(self.load_format, str):
            load_format = self.load_format.lower()
            self.load_format = LoadFormat(load_format)

        if self.ignore_patterns is not None and len(self.ignore_patterns) > 0:
            logger.info(
                "Ignoring the following patterns when downloading weights: %s", self.ignore_patterns
            )
        else:
            self.ignore_patterns = ["original/**/*"]


@dataclass
class SpecDecConfig:
    """Configuration for the SpecDec model."""

    pass


# TODO: This is a placeholder. Implement the LoRAConfig dataclass.
@dataclass
class LoRAConfig:
    """Configuration for the LoRA model."""

    max_lora_rank: int
    max_loras: int
    fully_sharded_loras: bool = False
    max_cpu_loras: Optional[int] = None
    lora_dtype: Optional[Union[torch.dtype, str]] = None
    lora_extra_vocab_size: int = 256
    # This is a constant.
    lora_vocab_padding_size: ClassVar[int] = 256
    long_lora_scaling_factors: Optional[Tuple[float]] = None
    bias_enabled: bool = False


@dataclass
class MultiModalConfig:
    """Configuration for the multimodal model."""

    pass


@dataclass
class QuantizationConfig:
    """Configuration for quantization."""

    pass


@dataclass
class LLMConfig:
    """Configuration which contains all the sub-configurations for the LLM model."""

    model_config: ModelConfig = field(default=None, init=True)
    cache_config: CacheConfig = field(default=None, init=True)
    load_config: LoadConfig = field(default=None, init=True)
    lora_config: Optional[LoRAConfig] = None
    specdec_config: Optional[SpecDecConfig] = None
    quant_config: Optional[QuantizationConfig] = None
