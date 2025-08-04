import itertools
import logging
from dataclasses import dataclass, field
from typing import (
    Callable,
    Iterable,
    List,
    Mapping,
    Optional,
    Set,
    Tuple,
)

import torch
import torch.nn as nn

from furiosa_models.architecture.model_loader.weight_utils import default_weight_loader

logger = logging.getLogger(__name__)

WeightsMapping = Mapping[str, Optional[str]]
"""If a key maps to a value of `None`, the corresponding weight is ignored."""


@dataclass
class WeightsMapper:
    """Maps the name of each weight if they match the following patterns."""

    orig_to_new_substr: WeightsMapping = field(default_factory=dict)
    orig_to_new_prefix: WeightsMapping = field(default_factory=dict)
    orig_to_new_suffix: WeightsMapping = field(default_factory=dict)

    def _map_name(self, key: str) -> Optional[str]:
        for substr, new_key in self.orig_to_new_substr.items():
            if substr in key:
                if new_key is None:
                    return None

                key = key.replace(substr, new_key, 1)

        for prefix, new_key in self.orig_to_new_prefix.items():
            if key.startswith(prefix):
                if new_key is None:
                    return None

                key = key.replace(prefix, new_key, 1)

        for suffix, new_key in self.orig_to_new_suffix.items():
            if key.endswith(suffix):
                if new_key is None:
                    return None

                key = new_key.join(key.rsplit(suffix, 1))

        return key

    def apply(
        self, weights: Iterable[Tuple[str, torch.Tensor]]
    ) -> Iterable[Tuple[str, torch.Tensor]]:
        """Maps the names of the weights based on the defined patterns."""
        return (
            (out_name, data)
            for name, data in weights
            if (out_name := self._map_name(name)) is not None
        )


class AutoWeightsLoader:
    """Automatically loads weights into a module based on the weight names.

    The weight loading logic for individual modules can be overridden
    by defining a ``load_weights`` method.

    Similarly, the weight loading logic for individual parameters can be
    overridden by defining a ``weight_loader`` method.

    Detailed weight loading information can be viewed by setting the
    environment variable ``VLLM_LOGGING_LEVEL=DEBUG``.
    """

    def __init__(
        self,
        module: nn.Module,
        *,
        skip_prefixes: Optional[List[str]] = None,
        ignore_unexpected_prefixes: Optional[List[str]] = None,
    ) -> None:
        super().__init__()

        self.module = module
        self.skip_prefixes = skip_prefixes or []
        self.ignore_unexpected_prefixes = ignore_unexpected_prefixes or []

    def _groupby_prefix(
        self,
        weights: Iterable[Tuple[str, torch.Tensor]],
    ) -> Iterable[Tuple[str, Iterable[Tuple[str, torch.Tensor]]]]:
        weights_by_parts = (
            (weight_name.split(".", 1), weight_data) for weight_name, weight_data in weights
        )

        for prefix, group in itertools.groupby(weights_by_parts, key=lambda x: x[0][0]):
            yield (
                prefix,
                # Because maxsplit=1 in weight_name.split(...),
                # the length of `parts` must either be 1 or 2
                (
                    ("" if len(parts) == 1 else parts[1], weights_data)
                    for parts, weights_data in group
                ),
            )

    def _get_qualname(self, prefix: str, rest: str) -> str:
        if prefix == "":
            return rest
        if rest == "":
            return prefix

        return ".".join((prefix, rest))

    def _can_skip(self, qualname: str) -> bool:
        return any(qualname.startswith(p) for p in self.skip_prefixes)

    def _can_ignore_unexpected(self, qualname: str) -> bool:
        return any(qualname.startswith(p) for p in self.ignore_unexpected_prefixes)

    def _load_param(
        self,
        base_prefix: str,
        param: nn.Parameter,
        weights: Iterable[Tuple[str, torch.Tensor]],
    ) -> Iterable[str]:
        for weight_name, weight_data in weights:
            weight_qualname = self._get_qualname(base_prefix, weight_name)

            if self._can_skip(weight_qualname):
                logger.debug("Skipping weight %s", weight_qualname)

                continue

            if weight_name != "":
                if self._can_ignore_unexpected(weight_qualname):
                    logger.debug("Ignoring weight %s", weight_qualname)

                    continue

                raise ValueError(
                    f"Attempted to load nested weight '{weight_qualname}' "
                    f"into a single parameter '{base_prefix}'"
                )

            weight_loader = getattr(param, "weight_loader", default_weight_loader)
            weight_loader(param, weight_data)

            logger.debug("Loaded weight %s with shape %s", weight_qualname, param.shape)

            yield weight_qualname

    def _load_module(
        self,
        base_prefix: str,
        module: nn.Module,
        weights: Iterable[Tuple[str, torch.Tensor]],
    ) -> Iterable[str]:
        # Avoid infinite recursion since this function is typically
        # called inside load_weights of the module itself
        if module != self.module:
            module_load_weights = getattr(module, "load_weights", None)
            if callable(module_load_weights):
                loaded_params = module_load_weights(weights)
                if loaded_params is None:
                    logger.warning("Unable to collect loaded parameters for module %s", module)
                else:
                    yield from map(
                        lambda x: self._get_qualname(base_prefix, x),
                        loaded_params,
                    )

        child_modules = dict(module.named_children())
        child_params = dict(module.named_parameters(recurse=False))

        for child_prefix, child_weights in self._groupby_prefix(weights):
            prefix = self._get_qualname(base_prefix, child_prefix)

            if child_prefix in child_modules:
                if self._can_skip(prefix + "."):
                    logger.debug("Skipping module %s", prefix)

                    continue

                yield from self._load_module(prefix, child_modules[child_prefix], child_weights)
            elif child_prefix in child_params:
                if self._can_skip(prefix):
                    logger.debug("Skipping param %s", prefix)

                    continue

                yield from self._load_param(prefix, child_params[child_prefix], child_weights)
            else:
                can_skip_module = self._can_skip(prefix + ".")
                can_skip_param = self._can_skip(prefix)
                if can_skip_module or can_skip_param:
                    logger.debug("Skipping missing %s", prefix)

                    continue

                can_ignore_module = self._can_ignore_unexpected(prefix + ".")
                can_ignore_param = self._can_ignore_unexpected(prefix)
                if can_ignore_module or can_ignore_param:
                    logger.debug("Ignoring missing %s", prefix)

                    continue

                msg = (
                    f"There is no module or parameter named '{prefix}' "
                    f"in {type(self.module).__name__}"
                )
                raise ValueError(msg)

    def load_weights(
        self,
        weights: Iterable[Tuple[str, torch.Tensor]],
        *,
        mapper: Optional[WeightsMapper] = None,
    ) -> Set[str]:
        """Loads weights into the module."""
        if mapper is not None:
            weights = mapper.apply(weights)

        autoloaded_weights = set(self._load_module("", self.module, weights))
        return autoloaded_weights


def make_layers(
    num_layers: int,
    layer_fn: Callable[[int], nn.Module],
) -> nn.ModuleList:
    """Creates a list of layers using the given layer factory function.

    Args:
        num_layers (int): Number of layers to create.
        layer_fn (Callable[[int], nn.Module]): Function to create a layer, taking an index as input.

    Returns:
        nn.ModuleList: A list of layers wrapped in `nn.ModuleList`.
    """
    return nn.ModuleList(layer_fn(idx) for idx in range(num_layers))


def append_prefix(prefix: str, name: str) -> str:
    """Appends a prefix to a name if the prefix is provided.

    Args:
        prefix (str): The prefix to append. If empty, the name remains unchanged.
        name (str): The base name to append the prefix to.

    Returns:
        str: The name with the prefix appended, or the original name if no prefix is provided.

    Example:
        >>> append_prefix("layer", "weight")
        'layer.weight'
        >>> append_prefix("", "weight")
        'weight'
    """
    return name if not prefix else f"{prefix}.{name}"
