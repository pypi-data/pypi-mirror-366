import math
from abc import abstractmethod
from typing import Any, Dict, Optional, Tuple

import torch

from furiosa_models.architecture.layers.ops import OpBase


class RotaryEmbeddingOpBase(OpBase):
    """Abstract base class for rotary positional embedding operations.

    This class defines the structure for rotary embedding operations, including
    cosine and sine cache computations and the embedding application logic.

    Methods:
        compute(): Applies rotary embeddings to query and key tensors.
        compute_cos_sin(): Computes cosine and sine cache based on input parameters.
        _compute_cos_sin(): Internal helper for calculating cosine and sine caches.
        _compute_inv_freq(): Internal helper for calculating inverse frequencies.
    """

    @abstractmethod
    def compute(
        self,
        positions: torch.Tensor,
        query: torch.Tensor,
        key: torch.Tensor,
        head_size: int,
        rotary_dim: int,
        cos_sin_cache: torch.Tensor,
        is_neox_style: bool = False,
        offsets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies rotary embeddings to query and key tensors.

        Args:
            positions (torch.Tensor): Positional indices of shape `(batch_size, sequence_length)`.
            query (torch.Tensor): Query tensor of shape `(batch_size, num_heads, hidden_size)`.
            key (torch.Tensor): Key tensor of shape `(batch_size, num_heads, hidden_size)`.
            head_size (int): Size of each attention head.
            rotary_dim (int): Dimensionality of the rotary embedding.
            cos_sin_cache (torch.Tensor): Cached cosine and sine values of shape
                `(max_seq_length, rotary_dim * 2)`.
            is_neox_style (bool): Whether to use Neox-style rotary embeddings.
            offsets (Optional[torch.Tensor]): Optional position offsets of shape
                `(batch_size, sequence_length)`.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Transformed query and key tensors of shape
                                               `(batch_size, num_heads, hidden_size)`.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute()`.")

    @abstractmethod
    def compute_cos_sin(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes the cosine and sine cache used for rotary embeddings.

        Args:
            base (float): Base frequency for positional embeddings.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (int): Maximum number of positional embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Optional scaling configuration.

        Returns:
            torch.Tensor: Cosine and sine cache tensor of shape `(max_seq_length, rotary_dim * 2)`.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `compute_cos_sin()`.")

    @abstractmethod
    def _compute_cos_sin(
        self,
        inv_freq: torch.Tensor,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Internal function to compute cosine and sine values using inverse frequencies.

        Args:
            inv_freq (torch.Tensor): Inverse frequency tensor of shape `(rotary_dim // 2,)`.
            max_position_embeddings (int): Maximum position embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Optional scaling configuration.

        Returns:
            torch.Tensor: Concatenated cosine and sine tensor of shape
                `(max_seq_length, rotary_dim * 2)`.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `_compute_cos_sin()`.")

    @abstractmethod
    def _compute_inv_freq(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes the inverse frequency for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (int): Maximum position embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Optional scaling configuration.

        Returns:
            torch.Tensor: Inverse frequency tensor of shape `(rotary_dim // 2,)`.

        Raises:
            NotImplementedError: If the method is not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement `_compute_inv_freq()`.")


def _apply_rotary_emb(
    z: torch.Tensor,
    rotary_matrix: torch.Tensor,
    is_interleaved: bool,
) -> torch.Tensor:
    """Applies rotary embeddings using precomputed 2×2 rotation matrices.

    Supports both interleaved (GPT-J-style) and chunked (Neox-style) formats.

    For details, refer to:
    https://github.com/furiosa-ai/furiosa-models-lang/issues/14#issuecomment-2817205660

    Args:
        z (torch.Tensor): Input tensor of shape `(..., H, D * 2)` where D = rotary_dim // 2.
            Represents (xₖ, yₖ) pairs per position.
        rotary_matrix (torch.Tensor): Tensor of shape `(..., D, 2, 2)` representing
            per-position 2×2 rotation matrices.
        is_interleaved (bool): If True, assumes GPT-J-style interleaved layout.
            Affects how z is constructed and flattened after rotation.

    Returns:
        torch.Tensor: Tensor of shape `(..., H, D * 2)` after applying rotation.
            Caller is responsible for reshaping it back to original layout if needed.
    """
    assert z.shape[-1] % 2 == 0, "z must have an even number of dimensions."
    assert z.shape[-1] // 2 == rotary_matrix.shape[-3], (
        "z and rotary_matrix must have the same number of pair_dim(D) dimensions. "
        f"Got {z.shape[-1] // 2} and {rotary_matrix.shape[-3]} respectively."
    )

    pair_dim = int(z.shape[-1] // 2)  # D = rotary_dim // 2
    # Reshape z to (..., H, D, 2), where the last dimension is (xₖ, yₖ)
    if is_interleaved:
        # Interleaved format:
        # - last dim: [x₀, y₀, x₁, y₁, ..., x_{D−1}, y_{D−1}]
        # → view(..., D, 2): [..., D, 2] with pairs like [x₀, y₀], [x₁, y₁], ...
        z = z.view(*z.shape[:-1], pair_dim, 2)
    else:
        # Chunked format:
        # - last dim: [x₀, x₁, ..., x_{D−1}, y₀, y₁, ..., y_{D−1}]
        # → view(..., 2, D): [..., 2, D] where rows = [x*], [y*]
        # → transpose(-2, -1): [..., D, 2] with pairs like [x₀, y₀], [x₁, y₁], ...
        z = z.view(*z.shape[:-1], 2, pair_dim)
        z = z.transpose(-2, -1)

    # Cast rotary_matrix to the same dtype as z
    rotary_matrix = rotary_matrix.to(z.dtype)
    rotary_matrix = rotary_matrix.unsqueeze(2)  # Shape: [..., 1, D, 2, 2]

    if torch.compiler.is_compiling():
        # During graph tracing:
        # Use einsum to represent RoPE as a fused op for better traceability
        # and compiler optimization.
        # Verified to match the Hadamard-based fallback under float32 precision.

        # - z:              [..., H, D, 2]       ← (xₖ, yₖ) vector pairs
        # - rotary_matrix:  [..., 1, D, 2, 2]    ← 2×2 rotation matrix for each pair
        # - einsum equation: "...dij, ...dj → ...di"
        #     → For each pair index d, perform 2×2 matrix-vector multiplication:
        #        z_rot[..., d, i] = Σⱼ rotary_matrix[..., d, i, j] × z[..., d, j]
        #        i.e., z[..., d, :] @ R[..., d] ∈ ℝ²
        z_rot = torch.einsum("...dij,...dj->...di", rotary_matrix, z)
    else:
        # During eager execution:
        # Use elementwise (Hadamard) vector operations for better numerical precision
        # and model verification.
        # Avoids precision loss observed in einsum, especially under low-precision dtypes.

        # Extract cos and sin components: shape [..., D]
        cos = rotary_matrix[..., 0, 0]
        sin = rotary_matrix[..., 1, 0]

        # Extract x, y components from z: shape [..., H, D]
        x = z[..., 0]
        y = z[..., 1]

        # Perform elementwise rotation
        x_rot = x * cos - y * sin
        y_rot = y * cos + x * sin
        # Recombine rotated components: shape [..., H, D, 2]
        z_rot = torch.stack([x_rot, y_rot], dim=-1)

    # Reshape back to original layout
    if not is_interleaved:
        # If not interleaved (i.e., chunked), we need to undo the earlier transpose
        # Current shape: [..., D, 2] → transpose → [..., 2, D]
        z_rot = z_rot.transpose(-2, -1).contiguous()  # → shape: [..., 2, D]

    # Common reshaping to flatten the last two dimensions: [..., 2, D] or [..., D, 2]
    z_rot = z_rot.view(*z_rot.shape[:-2], -1)  # → shape: [..., H, 2 * D]

    return z_rot


def _make_rotary_matrix_cache(
    cos: torch.Tensor,
    sin: torch.Tensor,
) -> torch.Tensor:
    """Creates a rotary matrix cache from cosine and sine values.

    Args:
        cos (torch.Tensor): Cosine values tensor of shape
            `(max_position_embeddings, rotary_dim // 2)`.
        sin (torch.Tensor): Sine values tensor of shape
            `(max_position_embeddings, rotary_dim // 2)`.

    Returns:
        torch.Tensor: Rotary matrix cache tensor of shape `(max_position_embeddings, 2, 2)`.
    """
    assert cos.dtype == sin.dtype, "cos and sin must have the same dtype"
    assert cos.shape == sin.shape, "cos and sin must have the same shape"
    assert cos.ndim == 2, "cos and sin must be 2D tensors"

    cos = cos.unsqueeze(-1)  # Shape: (max_position_embeddings, rotary_dim // 2, 1)
    sin = sin.unsqueeze(-1)

    # rotary matrix
    rot = torch.cat((cos, -sin, sin, cos), dim=-1)
    return rot.view(*rot.shape[:2], 2, 2)


def _compute_cos_sin_cache(
    inv_freq: torch.Tensor,
    max_position_embeddings: int,
    scaling_factor: Optional[float] = None,
    mscale: Optional[float] = None,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    """Computes cosine and sine caches for rotary embeddings.

    Args:
        inv_freq (torch.Tensor): Inverse frequency tensor of shape `(rotary_dim // 2,)`.
        max_position_embeddings (int): Maximum number of position embeddings.
        scaling_factor (Optional[float]): Scaling factor for positions.
        mscale (Optional[float]): Magnitude scaling factor for cos/sin values.
        device (Optional[torch.device]): Device for computation.

    Returns:
        torch.Tensor: Cached cosine and sine embeddings with shape
            `(max_position_embeddings, rotary_dim * 2)`.
    """
    assert inv_freq.dtype == torch.float32, "inv_freq must be of type float32"

    if device is None:
        device = inv_freq.device

    if scaling_factor is not None:
        max_position_embeddings = int(float(max_position_embeddings) * scaling_factor)

    t = torch.arange(max_position_embeddings, dtype=torch.float, device=device)
    freqs = torch.einsum("i,j -> ij", t, inv_freq)

    cos = freqs.cos()
    sin = freqs.sin()

    if mscale is not None:
        cos *= mscale
        sin *= mscale

    return _make_rotary_matrix_cache(cos, sin)


# TODO: Apply rotary matrix caching to vision RoPE (einsum-based)
def _compute_vision_cos_sin_cache(
    inv_freq: torch.Tensor,
    max_position_embeddings: int,
    scaling_factor: Optional[float] = None,
    mscale: Optional[float] = None,
    dtype: torch.dtype = torch.float32,
    device: Optional[torch.device] = None,
) -> torch.Tensor:
    """Computes cosine and sine caches for vision-based rotary embeddings.

    Args:
        inv_freq (torch.Tensor): Inverse frequency tensor of shape `(rotary_dim // 2,)`.
        max_position_embeddings (int): Maximum number of position embeddings.
        scaling_factor (Optional[float]): Scaling factor for positions.
        mscale (Optional[float]): Magnitude scaling factor for cos/sin values.
        dtype (torch.dtype): Output data type.
        device (Optional[torch.device]): Device for computation.

    Returns:
        torch.Tensor: Cached cosine and sine embeddings with shape
            `(max_position_embeddings, rotary_dim * 2)`.
    """
    _ = mscale
    _ = dtype

    if device is None:
        device = inv_freq.device

    if scaling_factor is not None:
        max_position_embeddings = int(max_position_embeddings * scaling_factor)

    num_patches = max_position_embeddings
    img_idx = torch.arange(num_patches, dtype=torch.int32).reshape(num_patches, 1)
    img_idx = torch.cat([img_idx, img_idx[:1]], dim=0)
    img_idx[-1, -1] = -2  # set to ID_CLS_TOKEN
    num_patches_single_dim = int(math.sqrt(num_patches))
    frequencies_x = img_idx % num_patches_single_dim
    frequencies_y = img_idx // num_patches_single_dim
    freqs_x = ((frequencies_x + 1)[..., None] * inv_freq[None, None, :]).repeat_interleave(
        2, dim=-1
    )
    freqs_y = ((frequencies_y + 1)[..., None] * inv_freq[None, None, :]).repeat_interleave(
        2, dim=-1
    )
    freqs = torch.cat([freqs_x, freqs_y], dim=-1).float().contiguous()[..., ::2]
    freqs = freqs.masked_fill(img_idx.reshape(-1, 1, 1) < 0, 0)
    cache = torch.view_as_complex(torch.stack([torch.cos(freqs), torch.sin(freqs)], dim=-1))

    return cache


class RotaryEmbeddingOp(RotaryEmbeddingOpBase):
    """Standard implementation of Rotary Positional Embeddings (RoPE).

    This class provides the basic rotary embedding operations commonly used in models
    like GPT-J and Neox. It implements the default behavior without any custom scaling.
    """

    def _compute_inv_freq(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: Optional[int] = None,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes inverse frequencies for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (Optional[int]): Maximum position embeddings (unused).
            rope_scaling (Optional[Dict[str, Any]]): Scaling parameters (unused).

        Returns:
            torch.Tensor: Inverse frequency tensor of shape `(rotary_dim // 2,)`.
        """
        _ = max_position_embeddings
        _ = rope_scaling

        inv_freq = torch.tensor(
            1.0 / (base ** (torch.arange(0, rotary_dim, 2, dtype=torch.float) / rotary_dim))
        )
        return inv_freq

    def _compute_cos_sin(
        self,
        inv_freq: torch.Tensor,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes cosine and sine caches using the inverse frequencies.

        Args:
            inv_freq (torch.Tensor): Inverse frequency tensor.
            max_position_embeddings (int): Maximum position embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Scaling parameters (unused).

        Returns:
            torch.Tensor: Cosine and sine cache tensor of shape
                `(max_position_embeddings, rotary_dim * 2)`.
        """
        _ = rope_scaling
        return _compute_cos_sin_cache(inv_freq, max_position_embeddings)

    def compute_cos_sin(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes and returns the cosine and sine caches for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (int): Maximum number of positional embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Optional scaling configuration.

        Returns:
            torch.Tensor: Cosine and sine cache tensor of shape
                `(max_position_embeddings, rotary_dim * 2)`.
        """
        inv_freq = self._compute_inv_freq(base, rotary_dim, max_position_embeddings, rope_scaling)
        return self._compute_cos_sin(inv_freq, max_position_embeddings, rope_scaling)

    def compute(
        self,
        positions: torch.Tensor,
        query: torch.Tensor,
        key: torch.Tensor,
        head_size: int,
        rotary_dim: int,
        cos_sin_cache: torch.Tensor,
        is_neox_style: bool = False,
        offsets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies rotary embeddings to query and key tensors.

        Args:
            positions (torch.Tensor): Positional indices of shape `(batch_size, sequence_length)`.
            query (torch.Tensor): Query tensor of shape
                `(batch_size, seq_len, hidden_size)` or
                `(batch_size, seq_len, num_heads, head_size)`.
            key (torch.Tensor): Key tensor of shape
                `(batch_size, seq_len, hidden_size)` or
                `(batch_size, seq_len, num_heads, head_size)`.
            head_size (int): Size of each attention head.
            rotary_dim (int): Dimensionality of the rotary embedding.
            cos_sin_cache (torch.Tensor): Cached rotary matrix of cosine and sine values of shape
                `(max_position_embeddings, rotary_dim // 2, 2, 2)`.
            is_neox_style (bool): Whether to use Neox-style rotary embeddings.
            offsets (Optional[torch.Tensor]): Optional position offsets of shape
                `(batch_size, sequence_length)`.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Transformed query and key tensors.

        Raises:
            ValueError: If the rotary_dim does not match the shape of the rotary matrix, or if
                the query or key tensors do not have 4 dimensions.
        """
        if offsets is not None:
            positions = positions + offsets

        # Gather the rotary matrix cache with the position indices
        # Shape: (B, S, D, 2, 2) where D = rotary_dim // 2
        rotary_matrix = cos_sin_cache[positions]

        # pair_dim (D) = number of (xₖ, yₖ) pairs, where D = rotary_dim // 2
        if rotary_dim != rotary_matrix.shape[-3] * 2:
            raise ValueError(
                "rotary_dim must be twice the -3rd dimension of the rotary matrix cache. "
                f"Got {rotary_dim} and {rotary_matrix.shape[-3] * 2} respectively."
            )

        # Apply rotary embeddings to the query tensor
        query_shape = query.shape
        query = query.view(*query.shape[:2], -1, head_size)
        query_rot = query[..., :rotary_dim]
        query_rot = _apply_rotary_emb(query_rot, rotary_matrix, is_interleaved=not is_neox_style)
        query_pass = query[..., rotary_dim:]
        query = torch.cat((query_rot, query_pass), dim=-1)

        # Apply rotary embeddings to the key tensor
        key_shape = key.shape
        key = key.view(*key.shape[:2], -1, head_size)
        key_rot = key[..., :rotary_dim]
        key_rot = _apply_rotary_emb(key_rot, rotary_matrix, is_interleaved=not is_neox_style)
        key_pass = key[..., rotary_dim:]
        key = torch.cat((key_rot, key_pass), dim=-1)

        return query.view(query_shape), key.view(key_shape)


class Llama3RotaryEmbeddingOp(RotaryEmbeddingOp):
    """Llama3-specific rotary embedding operation.

    This implementation modifies the standard rotary embedding by adjusting the inverse frequencies
    based on dynamic scaling factors. It allows for a smooth transition between low and high
    frequency ranges, enabling better handling of longer sequences.
    """

    def _compute_inv_freq(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: Optional[int] = None,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes dynamically adjusted inverse frequencies for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (Optional[int]): Maximum position embeddings (unused).
            rope_scaling (Optional[Dict[str, Any]]): Scaling parameters.

        Returns:
            torch.Tensor: Adjusted inverse frequency tensor of shape `(rotary_dim // 2,)`.

        Raises:
            ValueError: If rope_scaling parameters are missing.
            KeyError: If 'original_max_position_embeddings' is not provided in rope_scaling.
        """
        _ = max_position_embeddings  # Unused

        if rope_scaling is None:
            raise ValueError(
                "Rope scaling parameters must be provided for Llama3RotaryEmbeddingOp."
            )

        if "original_max_position_embeddings" not in rope_scaling:
            raise KeyError(
                "'original_max_position_embeddings' must be provided in rope_scaling for "
                "Llama3RotaryEmbeddingOp."
            )

        orig_max_position = rope_scaling["original_max_position_embeddings"]
        scaling_factor = rope_scaling.get("scaling_factor", 1.0)
        low_freq_factor = rope_scaling.get("low_freq_factor", 1.0)
        high_freq_factor = rope_scaling.get("high_freq_factor", 1.0)

        inv_freq = super()._compute_inv_freq(base, rotary_dim)

        low_freq_wavelen = orig_max_position / low_freq_factor
        high_freq_wavelen = orig_max_position / high_freq_factor

        wave_len = 2 * math.pi / inv_freq

        if low_freq_factor != high_freq_factor:
            smooth = (orig_max_position / wave_len - low_freq_factor) / (
                high_freq_factor - low_freq_factor
            )
        else:
            smooth = 0

        new_freq = torch.where(
            wave_len < high_freq_wavelen,
            inv_freq,
            torch.where(
                wave_len > low_freq_wavelen,
                inv_freq / scaling_factor,
                (1 - smooth) * inv_freq / scaling_factor + smooth * inv_freq,
            ),
        )
        return new_freq


class LinearScalingRotaryEmbeddingOp(RotaryEmbeddingOp):
    """Linear scaling rotary embedding operation.

    Implements a linear scaling strategy for rotary embeddings.
    Scales positional embeddings linearly based on a predefined scaling factor,
    allowing embeddings to extend effectively for longer sequences.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("LinearScalingRotaryEmbeddingOp is not yet implemented.")


class DynamicNTKScalingRotaryEmbeddingOp(RotaryEmbeddingOp):
    """Dynamic NTK scaling rotary embedding operation.

    Implements a dynamic scaling strategy based on Neural Tangent Kernel (NTK) theory.
    Adjusts the scaling of embeddings dynamically depending on sequence length,
    allowing better representation for longer sequences.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("DynamicNTKScalingRotaryEmbeddingOp is not yet implemented.")


class YaRNScalingRotaryEmbeddingOp(RotaryEmbeddingOp):
    """YaRN scaling rotary embedding operation.

    Implements the YaRN scaling method, dynamically adjusting frequency components
    during training. Enhances long-context learning by refining attention patterns
    through frequency adaptation.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("YaRNScalingRotaryEmbeddingOp is not yet implemented.")


class Phi3LongRoPEScaledRotaryEmbeddingOp(RotaryEmbeddingOpBase):
    """Phi-3 long RoPE scaled rotary embedding operation.

    Implements a specialized scaling approach for the Phi-3 model family.
    Optimizes long-sequence modeling by adjusting the position encoding to accommodate
    larger context windows.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("Phi3LongRoPEScaledRotaryEmbeddingOp is not yet implemented.")

    def compute(self, *args: Any, **kwargs: Any) -> torch.Tensor:  # type: ignore[override]
        """Applies rotary embeddings to query and key tensors."""
        _ = args
        _ = kwargs
        raise NotImplementedError("Phi3LongRoPEScaledRotaryEmbeddingOp is not yet implemented.")

    def compute_cos_sin(self, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Computes and returns the cosine and sine caches for rotary embeddings."""
        _ = args
        _ = kwargs
        raise NotImplementedError("Phi3LongRoPEScaledRotaryEmbeddingOp is not yet implemented.")

    def _compute_cos_sin(self, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Computes cosine and sine values using inverse frequencies."""
        _ = args
        _ = kwargs
        raise NotImplementedError("Phi3LongRoPEScaledRotaryEmbeddingOp is not yet implemented.")

    def _compute_inv_freq(self, *args: Any, **kwargs: Any) -> torch.Tensor:
        """Computes the inverse frequency for rotary embeddings."""
        _ = args
        _ = kwargs
        raise NotImplementedError("Phi3LongRoPEScaledRotaryEmbeddingOp is not yet implemented.")


class DeepseekScalingRotaryEmbeddingOp(RotaryEmbeddingOp):
    """DeepSeek scaling rotary embedding operation.

    Implements a scaling strategy based on DeepSeek's optimization principles.
    Enhances the model's ability to retain long-context dependencies through
    specialized frequency adjustments.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("DeepseekScalingRotaryEmbeddingOp is not yet implemented.")


class MRotaryEmbeddingOp(RotaryEmbeddingOp):
    """Multimodal rotary embedding operation.

    Implements rotary embeddings designed for multimodal inputs.
    Supports joint positional encoding for text, images, and other modalities,
    enabling better integration of different input types.

    Raises:
        NotImplementedError: This operation has not been implemented yet.
    """

    def __init__(self) -> None:
        raise NotImplementedError("MRotaryEmbeddingOp is not yet implemented.")


class Llama4VisionRotaryEmbeddingOp(RotaryEmbeddingOp):
    """Llama4 vision rotary embedding operation.

    Implements rotary embeddings specifically designed for Vision Transformers.
    """

    def _compute_inv_freq(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: Optional[int] = None,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes inverse frequencies for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (Optional[int]): Maximum position embeddings (unused).
            rope_scaling (Optional[Dict[str, Any]]): Scaling parameters (unused).

        Returns:
            torch.Tensor: Inverse frequency tensor of shape `(rotary_dim // 2,)`.
        """
        inv_freq = super()._compute_inv_freq(
            base, rotary_dim, max_position_embeddings, rope_scaling
        )
        inv_freq = inv_freq[: (rotary_dim // 2)]
        return inv_freq

    def _compute_cos_sin(
        self,
        inv_freq: torch.Tensor,
        max_position_embeddings: Optional[int] = None,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes cosine and sine caches using the inverse frequencies.

        Args:
            inv_freq (torch.Tensor): Inverse frequency tensor.
            max_position_embeddings (Optional[int]): Maximum position embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Scaling parameters (unused).

        Returns:
            torch.Tensor: Cosine and sine cache tensor of shape
                `(max_position_embeddings + 1, rotary_dim)`.
        """
        assert max_position_embeddings is not None, "max_position_embeddings must be provided."
        _ = rope_scaling
        return _compute_vision_cos_sin_cache(inv_freq, max_position_embeddings)

    def compute_cos_sin(
        self,
        base: float,
        rotary_dim: int,
        max_position_embeddings: int,
        rope_scaling: Optional[Dict[str, Any]] = None,
    ) -> torch.Tensor:
        """Computes and returns the cosine and sine caches for rotary embeddings.

        Args:
            base (float): Base frequency value.
            rotary_dim (int): Dimensionality of the rotary embedding.
            max_position_embeddings (int): Maximum number of positional embeddings.
            rope_scaling (Optional[Dict[str, Any]]): Optional scaling configuration.

        Returns:
            torch.Tensor: Cosine and sine cache tensor of shape
                `(max_position_embeddings + 1, rotary_dim)`.
        """
        inv_freq = self._compute_inv_freq(base, rotary_dim, max_position_embeddings, rope_scaling)
        return self._compute_cos_sin(inv_freq, max_position_embeddings, rope_scaling)

    def compute(
        self,
        positions: torch.Tensor,
        query: torch.Tensor,
        key: torch.Tensor,
        head_size: int,
        rotary_dim: int,
        cos_sin_cache: torch.Tensor,
        is_neox_style: bool = False,
        offsets: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Applies rotary embeddings to query and key tensors.

        Note:
        This implementation uses precomputed complex rotary embeddings.
        The positional inputs (positions, offsets) and rotary style (is_neox_style)
        are ignored in this implementation.

        Args:
            positions (torch.Tensor): Positional indices of shape `(batch_size, sequence_length)`.
                (unused)
            query (torch.Tensor): Query tensor of shape `(batch_size, num_heads, hidden_size)`.
            key (torch.Tensor): Key tensor of shape `(batch_size, num_heads, hidden_size)`.
            head_size (int): Size of each attention head. (unused)
            rotary_dim (int): Dimensionality of the rotary embedding. (unused)
            cos_sin_cache (torch.Tensor): Cached cosine and sine values of shape
                `(max_seq_length, rotary_dim * 2)`.
            is_neox_style (bool): Whether to use Neox-style rotary embeddings. (unused)
            offsets (Optional[torch.Tensor]): Optional position offsets of shape
                `(batch_size, sequence_length)`. (unused)

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Transformed query and key tensors.
        """
        _ = positions
        _ = head_size
        _ = rotary_dim
        _ = is_neox_style
        _ = offsets

        query_ = torch.view_as_complex(query.float().reshape(*query.shape[:-1], -1, 2))
        key_ = torch.view_as_complex(key.float().reshape(*key.shape[:-1], -1, 2))
        broadcast_shape = [
            d if i == 1 or i == (query_.ndim - 1) else 1 for i, d in enumerate(query_.shape)
        ]
        freqs_ci = cos_sin_cache.view(*broadcast_shape)
        query_out = torch.view_as_real(query_ * freqs_ci).flatten(3)
        key_out = torch.view_as_real(key_ * freqs_ci).flatten(3)
        return query_out.type_as(query), key_out.type_as(key)
