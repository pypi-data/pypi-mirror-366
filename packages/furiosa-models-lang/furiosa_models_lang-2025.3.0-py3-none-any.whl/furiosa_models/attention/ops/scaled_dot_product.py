import math
from typing import Optional

import torch

from furiosa_models.attention.ops.attention_mask import conditional_masking


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
    attn_mask: Optional[torch.Tensor] = None,
    is_causal: bool = False,
    scale: Optional[float] = None,
    enable_gqa: bool = False,
    mask_value: float = float("-inf"),
) -> torch.Tensor:
    r"""Computes the scaled dot-product attention.

    The scaled dot-product attention mechanism follows these steps:

    1. Compute raw attention scores:
       \[
       \text{scores} = \frac{Q K^T}{\sqrt{d_k}}
       \]
       where \(d_k\) is the key embedding dimension.

    2. Optionally apply a causal mask (prevents attending to future tokens).
    3. Optionally add an attention mask (e.g., padding or relative position bias).
    4. Normalize attention scores using the softmax function.
    5. Compute the weighted sum of value (`V`) vectors:
       \[
       \text{output} = \text{softmax(scores)} \cdot V
       \]

    Args:
        query (torch.Tensor): Query tensor of shape `(..., L, D)`,
            where `L` is the sequence length and `D` is the embedding dimension.
        key (torch.Tensor): Key tensor of shape `(..., S, D_v)`,
            where `S` is the key-value sequence length.
        value (torch.Tensor): Value tensor of shape `(..., S, D_v)`,
            where `D_v` is the value dimension.
        attn_mask (Optional[torch.Tensor], optional): Mask to control attention.
            It can be a boolean mask (masking out positions) or a float mask (biasing scores).
            Expected shape: `(L, S)`. Defaults to `None`.
        is_causal (bool, optional): If `True`, applies a causal mask to prevent attending
            to future tokens. Defaults to `False`.
        scale (Optional[float], optional): Custom scaling factor for the dot product.
            If `None`, defaults to `1/sqrt(D)`. Defaults to `None`.
        enable_gqa (bool, optional): If `True`, enables Grouped Query Attention (GQA)
            by repeating key and value tensors to match the query's head count. Defaults to `False`.
        mask_value (float, optional): Value to use for masking in the attention scores.
            Defaults to `float("-inf")`.

    Returns:
        torch.Tensor: The output tensor after applying attention, of shape `(..., L, D_v)`.

    Raises:
        RuntimeError: If causal masking is enabled and an explicit `attn_mask` is provided, or if
            the number of heads in `key` and `value` does not divide the number of heads in `query`.
    """
    B, H = query.size(0), query.size(1)
    L, S = query.size(-2), key.size(-2)
    scale_factor = scale or 1 / math.sqrt(query.size(-1))
    attn_bias: Optional[torch.Tensor] = torch.zeros(
        B, H, L, S, dtype=query.dtype, device=query.device
    )

    if is_causal:
        if attn_mask is not None:
            raise RuntimeError("Explicit attn_mask should not be set when `is_causal=True`.")
        temp_mask = torch.ones(L, S, dtype=torch.bool).tril(diagonal=0)
        assert attn_bias is not None, "attn_bias should not be None when is_causal is True."
        attn_bias.masked_fill_(temp_mask.logical_not(), float("-inf"))
        attn_bias.to(query.dtype)

    if attn_mask is not None:
        if attn_mask.dtype == torch.bool:
            attn_bias = None
        else:
            attn_bias = attn_mask

    if enable_gqa:
        if query.size(-3) % key.size(-3) != 0 or query.size(-3) % value.size(-3) != 0:
            raise RuntimeError(
                "Number of heads in key and value must divide the number of heads in query."
            )
        key = key.repeat_interleave(query.size(-3) // key.size(-3), -3)
        value = value.repeat_interleave(query.size(-3) // value.size(-3), -3)

    attn_score = query @ key.transpose(-2, -1) * scale_factor

    if attn_bias is not None:
        attn_score += attn_bias
    else:
        assert attn_mask is not None, "attn_mask should not be None when attn_bias is None."
        attn_score = conditional_masking(attn_mask, attn_score, mask_value=mask_value)

    attn_weight = torch.softmax(attn_score, dim=-1)

    return attn_weight @ value
