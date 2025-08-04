from dataclasses import dataclass, fields


@dataclass
class CausalModelDims:
    """Architectural dimensions used for causal language model export.

    Attributes:
        num_layers (int): Number of layers in the model.
        num_kv_heads (int): Number of key-value heads in the model.
        head_dim (int): Dimension of each head in the model.
    """

    num_layers: int
    num_kv_heads: int
    head_dim: int

    def __post_init__(self) -> None:
        """Post-initialization for CausalModelDims."""
        for f in fields(self):
            value = getattr(self, f.name)
            expected_type = f.type

            if isinstance(expected_type, type):
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"{f.name} must be {expected_type.__name__}, got {type(value).__name__}"
                    )

            # If int, enforce positive constraint
            if expected_type is int and value <= 0:
                raise ValueError(f"{f.name} must be a positive integer, got {value}")
