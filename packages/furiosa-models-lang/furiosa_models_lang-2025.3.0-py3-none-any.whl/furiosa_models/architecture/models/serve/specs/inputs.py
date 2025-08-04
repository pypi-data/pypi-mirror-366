from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import torch

from furiosa_models.attention.backends.llm import LLMAttentionMetadata


@dataclass
class CausalModelForwardInputs:
    """Forward inputs for torch export of a causal language model.

    Attributes:
        input_ids (torch.Tensor): Input IDs for the model.
        position_ids (torch.Tensor): Position IDs for the model.
        kv_caches (List[Tuple[torch.Tensor, torch.Tensor]]): Key-value caches for the model.
        attention_metadata (LLMAttentionMetadata): Attention metadata for the model.
        attention_masks (torch.Tensor): Attention masks for the model.
    """

    input_ids: torch.Tensor
    position_ids: torch.Tensor
    kv_caches: List[Tuple[torch.Tensor, torch.Tensor]]
    attention_metadata: LLMAttentionMetadata
    attention_masks: torch.Tensor

    def __post_init__(self) -> None:
        """Post-initialization for CausalModelExampleInputs."""
        if not isinstance(self.input_ids, torch.Tensor):
            raise TypeError("input_ids must be a torch.Tensor")
        if not isinstance(self.position_ids, torch.Tensor):
            raise TypeError("position_ids must be a torch.Tensor")
        if not isinstance(self.attention_masks, torch.Tensor):
            raise TypeError("attention_masks must be a torch.Tensor")

        if not isinstance(self.kv_caches, list):
            raise TypeError("kv_caches must be a list of (key, value) tensors")

        if not self.kv_caches:
            raise ValueError("kv_caches must be a non-empty list")

        for idx, pair in enumerate(self.kv_caches):
            if not (
                isinstance(pair, tuple)
                and len(pair) == 2
                and all(isinstance(t, torch.Tensor) for t in pair)
            ):
                raise TypeError("kv_caches must be a list of (Tensor, Tensor) pairs")

            k, v = pair
            if k.shape != v.shape:
                raise ValueError(
                    f"KV cache pair at index {idx} has mismatched shapes: "
                    f"key shape={k.shape}, value shape={v.shape}"
                )

        if not isinstance(self.attention_metadata, LLMAttentionMetadata):
            raise TypeError("attention_metadata must be an instance of LLMAttentionMetadata")

    def asdict(self) -> Dict[str, Any]:
        """Convert to dictionary for export."""
        return {
            "input_ids": self.input_ids,
            "position_ids": self.position_ids,
            "kv_caches": self.kv_caches,
            "attention_metadata": self.attention_metadata,
            "attention_masks": self.attention_masks,
        }
