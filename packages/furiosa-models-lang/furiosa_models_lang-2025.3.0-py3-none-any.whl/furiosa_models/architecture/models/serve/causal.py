import copy
import dataclasses
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

import torch
import torch.utils._pytree as pytree
from torch._dynamo.eval_frame import ExportResult
from torch.export import Dim, register_dataclass
from torch.fx._pytree import register_pytree_flatten_spec, tree_flatten_spec
from torch.utils._pytree import PyTree, TreeSpec
from transformers import PretrainedConfig

from furiosa_models.architecture.models.serve.args import CausalModelArgs
from furiosa_models.architecture.models.serve.base import ModelServer
from furiosa_models.architecture.models.serve.specs import (
    CausalModelContexts,
    CausalModelForwardInputs,
    CausalModelInputDtypes,
)
from furiosa_models.architecture.models.serve.utils import (
    CausalModelUtils,
    set_default_dtype,
)
from furiosa_models.attention.backends.llm import LLMAttentionBackend, LLMAttentionMetadata
from furiosa_models.config import CacheConfig, LLMConfig, LoRAConfig
from furiosa_models.dtype import normalize_dtype

T = TypeVar("T", bound="CausalModelServer")


class CausalModelServer(ModelServer):
    """Base class for causal language model export and runtime."""

    attention_backend: LLMAttentionBackend = LLMAttentionBackend()

    def __init__(self, llm_config: LLMConfig) -> None:
        super().__init__(llm_config)
        # LLMConfig, ModelConfig, and Transformers config are initialized
        # in the constructor of the base class
        # Belows are the CausalModelServer specific configurations
        self.cache_config: CacheConfig = llm_config.cache_config
        self.lora_config: Optional[LoRAConfig] = llm_config.lora_config

    @classmethod
    def create(
        cls: Type[T],
        model_or_config: Union[str, PretrainedConfig],
        *,
        model_dtype: Union[str, torch.dtype] = "bfloat16",
        kv_cache_dtype: Optional[Union[str, torch.dtype]] = None,
        block_size: int = 1,
    ) -> T:
        """Create serving-ready causal language model.

        Args:
            model_or_config (Union[str, PretrainedConfig]): HuggingFace Hub model ID or
                PretrainedConfig instance.
            model_dtype (Union[str, torch.dtype]): Data type for model parameters and activations.
                (Allowed: "bfloat16", "float16", "float32").
            kv_cache_dtype (Optional[Union[str, torch.dtype]]): Data type for key-value cache.
                (Allowed: "bfloat16", "float16", "float32").
            block_size (int): KV cache block size. Must be 1 for serving-ready models.

        Returns:
            T: The created causal language model instance.

        Raises:
            ValueError: if block size is not 1.
        """
        if block_size != 1:
            raise ValueError("block_size must be 1 for serving-ready causal language model.")

        model_dtype = normalize_dtype(model_dtype)
        kv_cache_dtype = normalize_dtype(kv_cache_dtype or model_dtype)

        llm_config = CausalModelArgs(
            model_or_config=model_or_config,
            model_dtype=model_dtype,
            kv_cache_dtype=kv_cache_dtype,
            block_size=block_size,
        ).to_llm_config()

        # Set torch's default dtype within this context during model initialization.
        # This ensures that only model parameters that follow the default torch dtype
        # (and are not fixed).
        with set_default_dtype(model_dtype):
            model = cls(llm_config=llm_config)

        return model

    def trace(
        self,
        example_inputs: Dict[str, Any],
        dynamic_shapes: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Callable[..., ExportResult]:
        """Trace causal language model with example inputs and dynamic shapes."""
        if "attention_metadata" not in example_inputs:
            raise ValueError("Missing attention_metadata in example_inputs")
        if dynamic_shapes is not None and "attention_metadata" not in dynamic_shapes:
            raise ValueError("Missing attention_metadata in dynamic_shapes")

        metadata_from_input = example_inputs["attention_metadata"]

        expected_type = self.attention_backend.metadata
        assert isinstance(expected_type, type), (
            "Expected attention_metadata to be a type, not an instance."
        )
        if not isinstance(metadata_from_input, expected_type):
            raise TypeError(
                f"Expected attention_metadata of type {expected_type}, "
                f"got {type(metadata_from_input)}"
            )

        self.register_attention_metadata()

        if dynamic_shapes is not None:
            metadata_from_shape = dynamic_shapes["attention_metadata"]

            # Normalize the dict to a list of values
            dynamic_shapes = copy.deepcopy(dynamic_shapes or {})
            if isinstance(metadata_from_shape, dict):
                dynamic_shapes["attention_metadata"] = list(metadata_from_shape.values())

        return self._trace(example_inputs, dynamic_shapes, **kwargs)

    @staticmethod
    def make_example_inputs(
        config: PretrainedConfig,
        *,
        batch_size: int,
        attention_size: int,
        kv_cache_size: int,
        paged_attention_block_size: int,
        paged_attention_num_blocks: int,
        kv_cache_dtype: Union[str, torch.dtype] = torch.float32,
    ) -> Dict[str, Any]:
        """Make example inputs for causal language model export.

        Args:
            config (PretrainedConfig): Model configuration.
            batch_size (int): Batch size for the model.
            attention_size (int): Size of the attention input.
            kv_cache_size (int): Size of the key-value cache.
            paged_attention_block_size (int): Block size for paged attention.
            paged_attention_num_blocks (int): Number of blocks for paged attention.
            kv_cache_dtype (Union[str, torch.dtype]): Data type for the key-value cache.

        Returns:
            Dict[str, Any]: Example inputs for the model.
        """
        contexts = CausalModelContexts(
            batch_size=batch_size,
            attention_size=attention_size,
            kv_cache_size=kv_cache_size,
            paged_attention_block_size=paged_attention_block_size,
            paged_attention_num_blocks=paged_attention_num_blocks,
        )
        kv_cache_dtype = normalize_dtype(kv_cache_dtype)
        input_dtypes = CausalModelInputDtypes(kv_cache=kv_cache_dtype)
        model_dims = CausalModelUtils.get_model_dims(config)

        return CausalModelServer._make_example_inputs(
            batch_size=batch_size,
            num_layers=model_dims.num_layers,
            num_kv_heads=model_dims.num_kv_heads,
            head_dim=model_dims.head_dim,
            block_size=paged_attention_block_size,
            num_blocks=paged_attention_num_blocks,
            prefill_seq_len=contexts.prefill_seq_len,
            decode_seq_len=contexts.decode_seq_len,
            past_seq_len=contexts.past_seq_len,
            max_seq_len=contexts.max_seq_len,
            is_prefill=contexts.is_prefill,
            input_ids_dtype=input_dtypes.input_ids,
            position_ids_dtype=input_dtypes.position_ids,
            attention_masks_dtype=input_dtypes.attention_masks,
            kv_cache_dtype=input_dtypes.kv_cache,
        )

    @staticmethod
    def _make_example_inputs(
        batch_size: int,
        num_layers: int,
        num_kv_heads: int,
        head_dim: int,
        max_seq_len: int,
        prefill_seq_len: Optional[int] = None,
        decode_seq_len: Optional[int] = None,
        past_seq_len: Optional[int] = None,
        block_size: int = 1,
        num_blocks: Optional[int] = None,
        is_prefill: bool = True,
        input_ids_dtype: torch.dtype = torch.int32,
        position_ids_dtype: torch.dtype = torch.int32,
        attention_masks_dtype: torch.dtype = torch.bool,
        kv_cache_dtype: torch.dtype = torch.bfloat16,
    ) -> Dict[str, Any]:
        """Make example inputs for causal language model export.

        Args:
            batch_size (int): Batch size for the model.
            num_layers (int): Number of layers in the model.
            num_kv_heads (int): Number of key-value heads in the model.
            head_dim (int): Dimension of each head in the model.
            max_seq_len (int): Maximum sequence length for the model.
            prefill_seq_len (Optional[int]): Sequence length for prefill mode.
            decode_seq_len (Optional[int]): Sequence length for decode mode.
            past_seq_len (Optional[int]): Past sequence length for decode mode.
            block_size (int): Block size for paged attention.
            num_blocks (Optional[int]): Number of blocks for paged attention.
            is_prefill (bool): Whether to use prefill mode.
            input_ids_dtype (torch.dtype): Data type for input IDs.
            position_ids_dtype (torch.dtype): Data type for position IDs.
            attention_masks_dtype (torch.dtype): Data type for attention masks.
            kv_cache_dtype (torch.dtype): Data type for key-value cache.

        Returns:
            Dict[str, Any]: Example inputs for the model.
        """
        if is_prefill:
            assert prefill_seq_len is not None, "prefill_seq_len must be provided for prefill mode"
            attention_size = prefill_seq_len
        else:
            assert decode_seq_len is not None, (
                "decode_seq_len must be provided for non-prefill mode"
            )
            assert past_seq_len is not None, "past_seq_len must be provided for non-prefill mode"
            attention_size = decode_seq_len + past_seq_len

        input_ids_size = prefill_seq_len if is_prefill else decode_seq_len
        assert input_ids_size is not None, "input_ids_size must be provided."
        input_ids = CausalModelUtils.create_input_ids(
            batch_size, input_ids_size, dtype=input_ids_dtype
        )
        position_ids = CausalModelUtils.create_position_ids(
            batch_size, input_ids_size, dtype=position_ids_dtype
        )
        attention_masks = CausalModelUtils.create_attention_masks(
            batch_size, input_ids_size, attention_size, dtype=attention_masks_dtype
        )
        attention_metadata = CausalModelUtils.create_attention_metadata(
            batch_size,
            block_size=block_size,
            prefill_seq_len=prefill_seq_len,
            past_seq_len=past_seq_len,
            decode_seq_len=decode_seq_len,
            max_seq_len=max_seq_len,
            is_prefill=is_prefill,
        )
        kv_caches = CausalModelUtils.create_kv_caches(
            batch_size=batch_size,
            max_seq_len=max_seq_len,
            num_layers=num_layers,
            num_kv_heads=num_kv_heads,
            head_dim=head_dim,
            block_size=block_size,
            num_blocks=num_blocks,
            dtype=kv_cache_dtype,
        )

        return CausalModelForwardInputs(
            input_ids=input_ids,
            position_ids=position_ids,
            kv_caches=kv_caches,
            attention_metadata=attention_metadata,
            attention_masks=attention_masks,
        ).asdict()

    @staticmethod
    def make_dynamic_shapes(
        batch_size: int,
        num_layers: int,
        is_prefill: bool = True,
        input_ids_size: int = 1,
    ) -> Dict[str, Any]:
        """Get dynamic shapes for causal language model export.

        Args:
            batch_size (int): Batch size for the model.
            num_layers (int): Number of layers in the model.
            is_prefill (bool): Whether to use prefill mode.
            input_ids_size (int): Size of the input IDs.

        Returns:
            Dict[str, Any]: Dynamic shapes for the model.

        Raises:
            ValueError: If input_ids_size is not greater than 0.
        """
        batch_dim = Dim("batch")
        num_blocks_dim = Dim("num_blocks")
        seq_len_dim = Dim("seq_len")

        if is_prefill:
            return {
                "input_ids": {0: batch_dim, 1: seq_len_dim},
                "position_ids": {0: batch_dim, 1: seq_len_dim},
                "kv_caches": [({0: num_blocks_dim}, {0: num_blocks_dim})] * num_layers,
                "attention_metadata": {
                    "prefill_seq_lens": [None] * batch_size,
                    "block_size": None,
                    "write_block_mapping": (
                        {0: batch_dim, 1: seq_len_dim},
                        {0: batch_dim, 1: seq_len_dim},
                    ),
                    "max_seq_len": None,
                },
                "attention_masks": {0: batch_dim, 1: seq_len_dim, 2: seq_len_dim},
            }
        else:
            past_seq_len_dim = Dim("past_seq_len")

            if input_ids_size > 1:
                # No add operation is allowed for the past_seq_len_dim and seq_len_dim
                past_plus_seq_len_dim = Dim("past_plus_seq_len")
                input_ids_shape = {0: batch_dim, 1: seq_len_dim}
                position_ids_shape = {0: batch_dim, 1: seq_len_dim}
                wrtite_block_mapping_shape = (
                    {0: batch_dim, 1: seq_len_dim},
                    {0: batch_dim, 1: seq_len_dim},
                )
                attention_masks_shape = {
                    0: batch_dim,
                    1: seq_len_dim,
                    2: past_plus_seq_len_dim,
                }
            elif input_ids_size == 1:
                input_ids_shape = {0: batch_dim}
                position_ids_shape = {0: batch_dim}
                wrtite_block_mapping_shape = (
                    {0: batch_dim},
                    {0: batch_dim},
                )
                attention_masks_shape = {0: batch_dim, 2: past_seq_len_dim + input_ids_size}
            else:
                raise ValueError("input_ids_size must be greater than 0")

            return {
                "input_ids": input_ids_shape,
                "position_ids": position_ids_shape,
                "kv_caches": [({0: num_blocks_dim}, {0: num_blocks_dim})] * num_layers,
                "attention_metadata": {
                    "prefill_seq_lens": [None] * batch_size,
                    "block_size": None,
                    "write_block_mapping": wrtite_block_mapping_shape,
                    "load_block_mapping": (
                        {0: batch_dim, 1: past_seq_len_dim},
                        {0: batch_dim, 1: past_seq_len_dim},
                    ),
                    "max_seq_len": None,
                },
                "attention_masks": attention_masks_shape,
            }

    @staticmethod
    def register_attention_metadata() -> None:
        """Register attention metadata as a dataclass for graph export (torch.export).

        This allows LLMAttentionMetadata to be treated as a valid dataclass
        during graph tracing and export.
        """
        CausalModelServer.reset_attention_metadata_registration()
        register_dataclass(CausalModelServer.attention_backend.metadata)

    @staticmethod
    def prepare_graph_forward() -> None:
        """Prepare attention metadata flatten/unflatten rules for graph forward execution.

        This ensures LLMAttentionMetadata instances are correctly flattened and unflattened
        during GraphModule.forward execution after export.
        """
        attention_metadata = CausalModelServer.attention_backend.metadata
        CausalModelServer.reset_attention_metadata_registration()
        field_names = [f.name for f in dataclasses.fields(attention_metadata)]

        def flatten_fn(x: PyTree, spec: TreeSpec) -> List[Any]:
            flat = []
            for name, child_spec in zip(field_names, spec.children_specs):
                value = getattr(x, name)
                flat.append(tree_flatten_spec(value, child_spec))
            return flat

        def exact_match_fn(x: PyTree, spec: TreeSpec) -> bool:
            _ = x
            return len(dataclasses.fields(attention_metadata)) == len(spec.children_specs)

        register_pytree_flatten_spec(
            attention_metadata,
            flatten_fn_spec=flatten_fn,
            flatten_fn_exact_match_spec=exact_match_fn,
        )

    @staticmethod
    def reset_attention_metadata_registration() -> None:
        """Reset PyTree registration of attention metadata."""
        attention_metadata: Type[LLMAttentionMetadata] = (
            CausalModelServer.attention_backend.metadata
        )
        if attention_metadata in pytree.SUPPORTED_NODES:
            del pytree.SUPPORTED_NODES[attention_metadata]
