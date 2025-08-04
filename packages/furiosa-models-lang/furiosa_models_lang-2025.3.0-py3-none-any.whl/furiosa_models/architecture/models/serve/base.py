from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union

import torch
import torch.nn as nn
from torch._dynamo.eval_frame import ExportResult
from transformers import PretrainedConfig

from furiosa_models.config import LLMConfig, ModelConfig

T = TypeVar("T", bound="ModelServer")


class ModelServer(nn.Module, ABC):
    """Abstract class for model serving."""

    def __init__(self, llm_config: LLMConfig) -> None:
        super().__init__()
        self.llm_config = llm_config
        self.model_config: ModelConfig = llm_config.model_config
        self.config: PretrainedConfig = llm_config.model_config.hf_config
        self._validate_architecture_match()

    def _trace(
        self,
        example_inputs: Dict[str, Any],
        dynamic_shapes: Optional[Union[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> Callable[..., ExportResult]:
        """Internal trace method for model export."""
        return torch._dynamo.export(self, **example_inputs, dynamic_shapes=dynamic_shapes, **kwargs)

    @classmethod
    @abstractmethod
    def create(cls: Type[T], *args: Any, **kwargs: Any) -> T:
        """Abstract method to create a model server instance."""
        raise NotImplementedError("Subclasses must implement `create()` method.")

    @abstractmethod
    def trace(
        self,
        example_inputs: Dict[str, Any],
        dynamic_shapes: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Callable[..., ExportResult]:
        """Abstract method for tracing the model for export."""
        raise NotImplementedError("Subclasses must implement `trace()` method.")

    @staticmethod
    @abstractmethod
    def make_example_inputs(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Abstract method to make example inputs for the model."""
        raise NotImplementedError("Subclasses must implement `make_example_inputs()` method.")

    @staticmethod
    @abstractmethod
    def make_dynamic_shapes(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Abstract method to make dynamic shapes for the model."""
        raise NotImplementedError("Subclasses must implement `make_dynamic_shapes()` method.")

    def _validate_architecture_match(self) -> None:
        """Ensure that the model class matches one of the architectures defined in the config.

        The `transformers.PretrainedConfig.architectures` field serves as the binding between
        the model class and its configuration, ensuring correctness and compatibility.
        """
        if not isinstance(self.config, PretrainedConfig):
            raise TypeError(
                f"Model class {self.__class__.__name__!r} requires "
                "a transformers.PretrainedConfig instance, "
                f"but got {type(self.config).__name__}."
            )

        if not hasattr(self.config, "architectures"):
            raise ValueError(
                f"Model class {self.__class__.__name__!r} requires "
                "'architectures' field in the config."
            )

        if not self.config.architectures:
            raise ValueError(
                f"Model class {self.__class__.__name__!r} requires the config (an instance of "
                "transformers.PretrainedConfig) "
                "to have the 'architectures' field set, but received config of type "
                f"'{type(self.config).__name__}' without architectures.\n"
                "Please use a model ID (from_pretrained) or manually set the 'architectures' field "
                "in your config."
            )

        if self.__class__.__name__ not in self.config.architectures:
            raise ValueError(
                f"Model class {self.__class__.__name__!r} does not match "
                f"any of the config architectures {self.config.architectures}."
            )
