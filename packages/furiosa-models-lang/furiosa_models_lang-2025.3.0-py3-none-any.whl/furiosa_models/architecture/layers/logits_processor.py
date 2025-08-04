from abc import ABC, abstractmethod
from typing import Optional

import torch

from furiosa_models.architecture.layers.vocab_embedding import LMHeadLayer


class LogitsProcessorBase(ABC):
    """Base class for all logits processors.

    Subclasses must implement the `process` method for modifying logits.
    """

    @abstractmethod
    def process(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply processing to the logits.

        Args:
            logits (torch.Tensor): Input logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.

        Returns:
            torch.Tensor: Processed logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.
        """
        pass


class LogitsProcessor(LogitsProcessorBase):
    """Applies scaling, soft capping, and vocab truncation to logits.

    Args:
        lm_head (LMHeadLayer): The language model head for projecting hidden states.
        vocab_size (int): The output vocabulary size.
        org_vocab_size (Optional[int]): Original vocabulary size. Defaults to None.
        scale (float): Scaling factor for logits. Defaults to 1.0.
        logits_as_input (bool): Treat input as logits if `True`.
        soft_cap (Optional[float]): Apply tanh-based soft cap if provided. Defaults to None.
    """

    def __init__(
        self,
        lm_head: LMHeadLayer,
        vocab_size: int,
        org_vocab_size: Optional[int] = None,
        scale: float = 1.0,
        logits_as_input: bool = False,
        soft_cap: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.lm_head = lm_head
        self.scale = scale
        self.vocab_size = vocab_size
        self.org_vocab_size = org_vocab_size or vocab_size
        self.logits_as_input = logits_as_input
        self.soft_cap = soft_cap

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Processes logits from hidden states.

        Args:
            hidden_states (torch.Tensor): Input tensor of shape
                `(batch_size, sequence_length, hidden_size)`.

        Returns:
            torch.Tensor: Processed logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.
        """
        logits = hidden_states if self.logits_as_input else self._get_logits(hidden_states)
        return self.process(logits)

    def process(self, logits: torch.Tensor) -> torch.Tensor:
        """Applies soft capping and scaling to the logits.

        Args:
            logits (torch.Tensor): Input logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.

        Returns:
            torch.Tensor: Processed logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.
        """
        if self.soft_cap is not None:
            logits = self._apply_soft_cap(logits)

        if self.scale != 1.0:
            logits *= self.scale

        return logits

    def _get_logits(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Generates logits using the LMHead.

        Args:
            hidden_states (torch.Tensor): Hidden states tensor of shape
                `(batch_size, sequence_length, hidden_size)`.

        Returns:
            torch.Tensor: Logits tensor truncated to `org_vocab_size`, of shape
                `(batch_size, sequence_length, org_vocab_size)`.
        """
        logits: torch.Tensor = self.lm_head(hidden_states)
        return logits[..., : self.org_vocab_size]

    def _apply_soft_cap(self, logits: torch.Tensor) -> torch.Tensor:
        """Applies soft capping using `tanh`.

        Args:
            logits (torch.Tensor): Input logits tensor of shape
                `(batch_size, sequence_length, vocab_size)`.

        Returns:
            torch.Tensor: Logits tensor after applying soft capping, of shape
                `(batch_size, sequence_length, vocab_size)`.
        """
        logits = logits / self.soft_cap
        logits = torch.tanh(logits)
        return logits * self.soft_cap

    def extra_repr(self) -> str:
        """Returns a string representation for debugging.

        Returns:
            str: A description of the processor's configuration.
        """
        return (
            f"vocab_size={self.vocab_size}, "
            f"org_vocab_size={self.org_vocab_size}, "
            f"scale={self.scale}, "
            f"logits_as_input={self.logits_as_input}, "
            f"soft_cap={self.soft_cap}"
        )
