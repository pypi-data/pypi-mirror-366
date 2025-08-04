# coding=utf-8
"""
Mask utility functions for optimized attention mechanisms.
"""

import torch


def build_3d_mask(mask, reference_shape, triu_for_causal=True):
    """
    Build 3d condition tensor with shape [B, ..., I, S] for non-chunked attention masking.
    """
    mask_shape = mask.shape
    assert len(mask_shape) == 2, f"Invalid mask shape {mask_shape}"
    assert len(reference_shape) > 2, f"Invalid reference shape {reference_shape}"

    B = reference_shape[0]  # batch size
    input_ids_size = reference_shape[-2]  # input ids size
    S = reference_shape[-1]  # attention size
    K = S - input_ids_size  # kv cache size

    assert B == mask_shape[0], f"Batch size mismatch {mask_shape} vs {reference_shape}"
    assert S == mask_shape[1], f"Attention size mismatch {mask_shape} vs {reference_shape}"
    assert K >= 0, f"Invalid reference shape {reference_shape}"

    target_shape = [B] + [1] * (len(reference_shape) - 3) + [input_ids_size, S]

    if input_ids_size == 1:
        return mask.view(target_shape)  # [B, ..., 1, S]

    # static tensors
    if triu_for_causal:
        col_static = torch.arange(S - 1, K - 1, -1, dtype=torch.int32, device=mask.device)  # [I]
    else:
        col_static = torch.arange(K, S, dtype=torch.int32, device=mask.device)  # [I]

    row_static = torch.cat(
        (torch.arange(K, dtype=torch.int32, device=mask.device), col_static)
    )  # [K+I]=[S]

    # mask row-wise
    row_masked = torch.ops.aten.where(mask, row_static, torch.iinfo(torch.int32).max)  # [B, S]

    # mask col-wise
    col_masked = torch.ops.aten.where(mask[:, K:], col_static, -1)  # [B, I]

    row_masked = row_masked.unsqueeze(-2)  # [B, 1, S]
    col_masked = col_masked.unsqueeze(-1)  # [B, I, 1]
    cond = col_masked >= row_masked  # [B, I, S]
    return cond.view(target_shape)  # [B, ..., I, S]
