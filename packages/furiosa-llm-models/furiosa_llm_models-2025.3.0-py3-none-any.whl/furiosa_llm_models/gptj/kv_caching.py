from typing import Sequence, Tuple

import torch


def kv_concat_update(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    past_key, past_value = past_key_value
    present_key = torch.cat((past_key, present_key), dim=-2)
    present_value = torch.cat((past_value, present_value), dim=-2)
    next_key_value = (present_key, present_value)

    return present_key, present_value, next_key_value


def kv_concat_update_reducing_next_kv_size(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    past_key, past_value = past_key_value
    next_key_value = present_key, present_value
    present_key = torch.cat((past_key, present_key), dim=-2)
    present_value = torch.cat((past_value, present_value), dim=-2)

    return present_key, present_value, next_key_value


def kv_index_update(
    new_index: torch.IntTensor,
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    past_key, past_value = past_key_value
    past_key[:, :, new_index, :] = present_key
    past_value[:, :, new_index, :] = present_value
    next_key_value = past_key, past_value

    return past_key, past_value, next_key_value


def _reshape_and_cache(
    target: torch.Tensor,
    total: torch.Tensor,
    new_target_location: torch.Tensor,
) -> None:
    indices = torch.squeeze(new_target_location.reshape(1, -1), dim=0)
    batch, seq, num_head, head_dim = target.shape
    total[indices] = target.reshape(batch * seq, 1, num_head, head_dim)


def _gather_cache(
    paged_key: torch.Tensor,
    paged_value: torch.Tensor,
    valid_key_indices: torch.IntTensor,
    valid_value_indices: torch.IntTensor,
    target_shape: Sequence[int],
) -> Tuple[torch.Tensor, torch.Tensor]:
    key_gather = paged_key[valid_key_indices].reshape(*target_shape)
    value_gather = paged_value[valid_value_indices].reshape(*target_shape)

    return key_gather, value_gather


def _gather_cache_with_unified_kv_indices(
    paged_key: torch.Tensor,
    paged_value: torch.Tensor,
    valid_kv_indices: torch.IntTensor,
    target_shape: Sequence[int],
) -> Tuple[torch.Tensor, torch.Tensor]:
    key_gather = paged_key[valid_kv_indices].reshape(*target_shape)
    value_gather = paged_value[valid_kv_indices].reshape(*target_shape)

    return key_gather, value_gather


def _gather_and_expand_cache(
    paged_key: torch.Tensor,
    paged_value: torch.Tensor,
    valid_key_indices: torch.IntTensor,
    valid_value_indices: torch.IntTensor,
    before_expand_shape: Sequence[int],
    after_expand_shape: Sequence[int],
    num_beam: int,
) -> Tuple[torch.Tensor, torch.Tensor]:
    # reshape -> repeat -> reshape
    key_gather = (
        paged_key[valid_key_indices]
        .reshape(*before_expand_shape)
        .repeat(1, num_beam, 1, 1)
        .reshape(*after_expand_shape)
    )
    value_gather = (
        paged_value[valid_value_indices]
        .reshape(*before_expand_shape)
        .repeat(1, num_beam, 1, 1)
        .reshape(*after_expand_shape)
    )

    return key_gather, value_gather


def kv_page_update(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    valid_key_indices: torch.IntTensor,
    valid_value_indices: torch.IntTensor,
    bucket_size: int,
    is_prefill: bool,
    head_first: bool = False,
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    past_key, past_value = past_key_value

    assert not head_first, f"head_first={head_first} is not supported."
    # at this point
    # present key = [batch, seq_len, head, head_dim]
    # present_value = [batch, head, seq_len, head_dim]
    # if head is first, this means past_key_value must have head before seq_len
    # thus, there is no need to permute present_value, only permute present_key
    # else: permute present_value such that seq_len is in front
    if head_first:
        present_key = present_key.permute(0, 2, 1, 3)
    else:
        present_value = present_value.permute(0, 2, 1, 3)

    _reshape_and_cache(
        target=present_key,
        total=past_key,
        new_target_location=new_key_location,
    )

    _reshape_and_cache(
        target=present_value,
        total=past_value,
        new_target_location=new_value_location,
    )

    next_key_value = (past_key, past_value)

    batch_size, _, num_heads, head_size = present_key.shape

    if not is_prefill:
        present_key, present_value = _gather_cache(
            past_key,
            past_value,
            valid_key_indices,
            valid_value_indices,
            target_shape=(batch_size, bucket_size, num_heads, head_size),
        )

    # return value must have head as first
    if not head_first:
        # make it head first
        present_key = present_key.permute(0, 2, 1, 3)
        present_value = present_value.permute(0, 2, 1, 3)

    return present_key, present_value, next_key_value


def kv_page_update_do_input_select_with_past_kv_indices(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    past_valid_key_indices: torch.IntTensor,
    past_valid_value_indices: torch.IntTensor,
    bucket_size: int,
    is_prefill: bool,
    head_first: bool = False,
    sp_len: int = 1,
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    assert not head_first, f"head_first={head_first} is not supported."

    # at this point
    # present key = [batch, seq_len, head, head_dim]
    # present_value = [batch, head, seq_len, head_dim]
    # if head is first, this means past_key_value must have head before seq_len
    # thus, there is no need to permute present_value, only permute present_key
    # else: permute present_value such that seq_len is in front
    if head_first:
        present_key = present_key.permute(0, 2, 1, 3)
    else:
        present_value = present_value.permute(0, 2, 1, 3)

    total_key, total_value = past_key_value
    target_key, target_value = present_key[:], present_value[:]

    batch_size, _, num_heads, head_size = present_key.shape

    if not is_prefill:
        past_key, past_value = _gather_cache(
            total_key,
            total_value,
            past_valid_key_indices,
            past_valid_value_indices,
            # target_shape=(batch_size, bucket_size - sp_len, num_heads, head_size),
            # The code is equivalent to the original code that uses bucket_size.
            # The fix below is to ensure that torch.dynamo.export
            # maintains dynamic bucket_size in the graph.
            # With the original code, the number bucket_size - sp_len is fixed in the graph.
            target_shape=(
                batch_size,
                past_valid_key_indices.shape[-1] // batch_size,
                num_heads,
                head_size,
            ),
        )

        present_key = torch.concat((past_key, present_key), dim=1)
        present_value = torch.concat((past_value, present_value), dim=1)

    _reshape_and_cache(
        target=target_key,
        total=total_key,
        new_target_location=new_key_location,
    )

    _reshape_and_cache(
        target=target_value,
        total=total_value,
        new_target_location=new_value_location,
    )

    # return value must have head as first
    if not head_first:
        # make it head first
        present_key = present_key.permute(0, 2, 1, 3)
        present_value = present_value.permute(0, 2, 1, 3)

    return present_key, present_value


def kv_page_update_do_input_select_with_past_kv_indices_verify(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    past_valid_key_indices: torch.IntTensor,
    past_valid_value_indices: torch.IntTensor,
    bucket_size: int,
    is_prefill: bool,
    head_first: bool = False,
    sp_len: int = 1,
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    assert not head_first, f"head_first={head_first} is not supported."

    # at this point
    # present key = [batch, seq_len, head, head_dim]
    # present_value = [batch, head, seq_len, head_dim]
    # if head is first, this means past_key_value must have head before seq_len
    # thus, there is no need to permute present_value, only permute present_key
    # else: permute present_value such that seq_len is in front
    if head_first:
        present_key = present_key.permute(0, 2, 1, 3)
    else:
        present_value = present_value.permute(0, 2, 1, 3)

    total_key, total_value = past_key_value
    target_key, target_value = present_key[:], present_value[:]

    batch_size, _, num_heads, head_size = present_key.shape
    if not is_prefill:
        past_key, past_value = _gather_cache(
            total_key,
            total_value,
            past_valid_key_indices,
            past_valid_value_indices,
            target_shape=(batch_size, bucket_size - sp_len - 1, num_heads, head_size),
        )

        present_key = torch.concat((past_key, present_key), dim=1)
        present_value = torch.concat((past_value, present_value), dim=1)

    _reshape_and_cache(
        target=target_key,
        total=total_key,
        new_target_location=new_key_location,
    )

    _reshape_and_cache(
        target=target_value,
        total=total_value,
        new_target_location=new_value_location,
    )

    # return value must have head as first
    if not head_first:
        # make it head first
        present_key = present_key.permute(0, 2, 1, 3)
        present_value = present_value.permute(0, 2, 1, 3)

    return present_key, present_value


def kv_paged_update_beam(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    past_valid_key_prompt_indices: torch.Tensor,
    past_valid_value_prompt_indices: torch.Tensor,
    past_valid_key_decode_indices: torch.Tensor,
    past_valid_value_decode_indices: torch.Tensor,
    bucket_size: int,
    is_prefill: bool,
    num_beam: int,
    num_real_batch: int,
    max_new_tokens: int,
    head_first: bool = False,
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    assert not head_first, f"head_first={head_first} is not supported."

    # at this point
    # present key = [batch, seq_len, head, head_dim]
    # present_value = [batch, head, seq_len, head_dim]
    # if head is first, this means past_key_value must have head before seq_len
    # thus, there is no need to permute present_value, only permute present_key
    # else: permute present_value such that seq_len is in front
    if head_first:
        present_key = present_key.permute(0, 2, 1, 3)
    else:
        present_value = present_value.permute(0, 2, 1, 3)

    total_key, total_value = past_key_value
    target_key, target_value = present_key[:], present_value[:]

    batch_size, _, num_heads, head_size = present_key.shape

    if not is_prefill:
        # gather prompt cache
        past_key_prompt, past_value_prompt = _gather_and_expand_cache(
            total_key,
            total_value,
            past_valid_key_prompt_indices,
            past_valid_value_prompt_indices,
            before_expand_shape=(
                num_real_batch,
                bucket_size - max_new_tokens,
                num_heads,
                head_size,
            ),
            after_expand_shape=(
                batch_size,
                bucket_size - max_new_tokens,
                num_heads,
                head_size,
            ),
            num_beam=num_beam,
        )

        # gather decode cache
        past_key_decode, past_value_decode = _gather_cache(
            total_key,
            total_value,
            past_valid_key_decode_indices,
            past_valid_value_decode_indices,
            target_shape=(batch_size, max_new_tokens - 1, num_heads, head_size),
        )

        # then concat prompt cache with decode cache

        present_key = torch.cat((past_key_prompt, past_key_decode, present_key), dim=1)
        present_value = torch.cat((past_value_prompt, past_value_decode, present_value), dim=1)

    _reshape_and_cache(
        target=target_key,
        total=total_key,
        new_target_location=new_key_location,
    )

    _reshape_and_cache(
        target=target_value,
        total=total_value,
        new_target_location=new_value_location,
    )

    # return value must have head as first
    if not head_first:
        # make it head first
        present_key = present_key.permute(0, 2, 1, 3)
        present_value = present_value.permute(0, 2, 1, 3)

    return present_key, present_value


def kv_page_update_with_unified_kv_indices(
    present_key: torch.Tensor,
    present_value: torch.Tensor,
    past_key_value: Tuple[torch.Tensor, torch.Tensor],
    new_kv_location: torch.Tensor,
    past_valid_kv_indices: torch.IntTensor,
    bucket_size: int,
    is_prefill: bool,
    head_first: bool = False,
    sp_len: int = 1,
) -> Tuple[torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    assert not head_first, f"head_first={head_first} is not supported."

    # at this point
    # present key = [batch, seq_len, head, head_dim]
    # present_value = [batch, head, seq_len, head_dim]
    # if head is first, this means past_key_value must have head before seq_len
    # thus, there is no need to permute present_value, only permute present_key
    # else: permute present_value such that seq_len is in front
    if head_first:
        present_key = present_key.permute(0, 2, 1, 3)
    else:
        present_value = present_value.permute(0, 2, 1, 3)

    total_key, total_value = past_key_value
    target_key, target_value = present_key[:], present_value[:]

    batch_size, _, num_heads, head_size = present_key.shape

    if not is_prefill:
        past_key, past_value = _gather_cache_with_unified_kv_indices(
            total_key,
            total_value,
            past_valid_kv_indices,
            target_shape=(
                batch_size,
                past_valid_kv_indices.shape[-1] // batch_size,
                num_heads,
                head_size,
            ),
        )

        present_key = torch.concat((past_key, present_key), dim=1)
        present_value = torch.concat((past_value, present_value), dim=1)

    _reshape_and_cache(
        target=target_key,
        total=total_key,
        new_target_location=new_kv_location,
    )

    _reshape_and_cache(
        target=target_value,
        total=total_value,
        new_target_location=new_kv_location,
    )

    # return value must have head as first
    if not head_first:
        # make it head first
        present_key = present_key.permute(0, 2, 1, 3)
        present_value = present_value.permute(0, 2, 1, 3)

    return present_key, present_value
