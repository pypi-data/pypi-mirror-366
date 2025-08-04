import torch


def conditional_masking(
    attn_mask: torch.Tensor, attn_score: torch.Tensor, mask_value: float = float("-inf")
) -> torch.Tensor:
    """Apply conditional masking to attention scores using a boolean mask.

    This corresponds to `torch.where(mask, scores, mask_value)`.

    Args:
        attn_mask (torch.Tensor): Boolean attention mask of shape `(..., L, S)`.
        attn_score (torch.Tensor): Attention attn_score tensor (e.g., QK^T)
            of shape `(..., D, L, S)`.
        mask_value (float, optional): Value to apply at masked positions. Defaults to -inf.

    Returns:
        torch.Tensor: Masked attention weights of shape `(..., D, L, S)`.

    Raises:
        ValueError: If `attn_mask` is not boolean or has incompatible shape.
    """
    if attn_mask.dtype != torch.bool:
        raise ValueError(f"`attn_mask` must be a boolean tensor. Got {attn_mask.dtype}.")
    if attn_score.ndim == attn_mask.ndim + 1:
        attn_mask = attn_mask.unsqueeze(-3)  # shape: (..., 1, L, S)
    elif attn_score.ndim != attn_mask.ndim:
        raise ValueError(
            f"`attn_score` must have the same ndim or one more than `attn_mask`, "
            f"(got {attn_score.ndim=} vs {attn_mask.ndim=})"
        )
    if attn_mask.shape[-2:] != attn_score.shape[-2:]:
        raise ValueError(
            f"`attn_mask` shape {attn_mask.shape[-2:]} must match "
            f"`attn_score` shape {attn_score.shape[-2:]}"
        )

    mask_tensor = torch.tensor(mask_value, dtype=attn_score.dtype, device=attn_score.device)
    return torch.where(attn_mask, attn_score, mask_tensor)
