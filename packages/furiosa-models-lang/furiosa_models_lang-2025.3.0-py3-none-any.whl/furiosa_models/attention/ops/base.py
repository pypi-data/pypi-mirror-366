from typing import Any

import torch


class AttentionOpBase:
    """Base class for attention operations."""

    @staticmethod
    def forward(
        *args: Any,
        **kwargs: Any,
    ) -> torch.Tensor:
        """Base method for attention operations forward pass."""
        _ = args
        _ = kwargs
        raise NotImplementedError("Subclasses must implement `forward()`.")
