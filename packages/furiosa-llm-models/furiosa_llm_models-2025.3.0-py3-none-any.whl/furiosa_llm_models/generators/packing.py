from typing import List, Tuple

import torch

# u8.MAX - 1, to support compact mask with padding value
MAX_PACKING_PER_ROW: int = 254


# TODO(packing should be combined into two for both bert and gptj)
def greedy_attention_packing_bert(
    input_ids: torch.Tensor,
    token_type_ids: torch.Tensor,
    bucketized_attention_mask: torch.Tensor,
    pad_token_id: int,
    compact_mask: bool,
    position_offset: int = 0,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, List[List[Tuple[int, int]]]]:
    """
    return  input_ids, token_type_ids, attention_mask, position_ids, target_locations
    """
    assert input_ids.shape == bucketized_attention_mask.shape

    logit_target_locations = []
    (original_batch, bucket_size) = bucketized_attention_mask.shape

    # split attention mask by batch
    batch_real_len = []
    for single_batch in bucketized_attention_mask:
        num_real_token = single_batch.sum().item()
        batch_real_len.append(num_real_token)

    # find real tokens
    # first convert all padding tensors to zero
    # This ensures that non_zero_indices contains all input_ids that are not padding tokens,
    # regardless of the padding token value.
    non_zero_indices = (bucketized_attention_mask != 0).nonzero().tolist()

    real_locations = []
    for i, real_len in enumerate(batch_real_len):
        locations = [non_zero_indices.pop(0)[1] for _ in range(real_len)]
        start = locations[0]
        end = locations[-1] + 1
        real_locations.append((i, start, end))

    marker = bucket_size
    target_locations: List[List[Tuple[int, int]]] = []  # List of List
    temp_indices = []
    for i in range(original_batch):
        cur_len = batch_real_len[i]
        if marker - cur_len < 0 or len(temp_indices) >= MAX_PACKING_PER_ROW:
            # we cannot pack so start a new row
            target_locations.append(temp_indices)
            temp_indices = []
            marker = bucket_size

        temp_indices.append((marker - cur_len, marker))
        marker -= cur_len

    # push the last row into the target locations
    target_locations.append(temp_indices)

    packed_batch_size = len(target_locations)

    # initialize attention mask
    packed_shape = (packed_batch_size, bucket_size)

    packed_input_ids = torch.full(
        packed_shape, fill_value=pad_token_id, dtype=torch.int32, device=input_ids.device
    )
    packed_token_type_ids = torch.zeros(
        packed_shape, dtype=torch.int32, device=token_type_ids.device
    )
    position_ids = torch.ones(packed_shape, dtype=torch.long, device=input_ids.device)

    # initialize causal mask
    if compact_mask:
        packed_attention_mask = torch.zeros(
            (packed_batch_size, bucket_size),
            dtype=torch.uint8,
            device=bucketized_attention_mask.device,
        )
    else:
        packed_attention_mask = torch.zeros(
            (packed_batch_size, bucket_size, bucket_size),
            dtype=torch.bool,
            device=bucketized_attention_mask.device,
        )

    # fill the new attention mask and mark the logit locations
    for index, target_location in enumerate(target_locations):
        # record new target locations
        logit_target_location = []
        for packing_idx, (start, end) in enumerate(target_location):
            (original_index, original_start, original_end) = real_locations.pop(0)
            packed_input_ids[index][start:end] = input_ids[original_index][
                original_start:original_end
            ]
            packed_token_type_ids[index][start:end] = token_type_ids[original_index][
                original_start:original_end
            ]
            position_ids[index][start:end] = torch.arange(end - start) + position_offset
            logit_target_location.append((start, end))

            if compact_mask:
                mask_value = packing_idx + 1  # 0 is reserved for padding
                packed_attention_mask[index][start:end] = mask_value
            else:
                packed_attention_mask[index][start:end, start:end] = torch.ones(
                    (end - start, end - start),
                    dtype=torch.bool,
                    device=bucketized_attention_mask.device,
                )

        logit_target_locations.append(logit_target_location)

    return (
        packed_input_ids,
        packed_token_type_ids,
        packed_attention_mask,
        position_ids,
        logit_target_locations,
    )


def greedy_attention_packing(
    input_ids: torch.Tensor,
    bucketized_attention_mask: torch.Tensor,
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    pad_token_id: int,
    compact_mask: bool = False,
) -> Tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    List[List[int]],
    torch.Tensor,
    torch.Tensor,
]:
    """
    return (packed_attention_mask, packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_location, packed_new_value_location)
    """  # noqa: E501
    assert input_ids.shape == bucketized_attention_mask.shape
    assert bucketized_attention_mask.shape == new_key_location.shape
    assert bucketized_attention_mask.shape == new_value_location.shape

    logit_target_locations = []
    (original_batch, bucket_size) = bucketized_attention_mask.shape

    # split attention mask by batch
    batch_real_len = []
    for single_batch in bucketized_attention_mask:
        num_real_token = single_batch.sum().item()
        batch_real_len.append(num_real_token)

    # find real tokens
    # first convert all padding tensors to 0
    # This ensures that non_zero_indices contains all input_ids that are not padding tokens,
    # regardless of the padding token value.
    non_zero_indices = (bucketized_attention_mask != 0).nonzero().tolist()
    real_locations = []
    for i, real_len in enumerate(batch_real_len):
        locations = [non_zero_indices.pop(0)[1] for _ in range(real_len)]
        start = locations[0]
        end = locations[-1] + 1
        real_locations.append((i, start, end))

    marker = bucket_size
    target_locations: List[List[Tuple[int, int]]] = []  # List of List
    temp_indices = []
    for i in range(original_batch):
        cur_len = batch_real_len[i]
        if marker - cur_len < 0 or len(temp_indices) >= MAX_PACKING_PER_ROW:
            # we cannot pack so start a new row
            target_locations.append(temp_indices)
            temp_indices = []
            marker = bucket_size

        temp_indices.append((marker - cur_len, marker))
        marker -= cur_len

    # push the last row into the target locations
    target_locations.append(temp_indices)

    packed_batch_size = len(target_locations)

    # initialize attention mask
    packed_shape = (packed_batch_size, bucket_size)

    packed_attention_mask = torch.zeros(packed_shape, dtype=torch.bool)
    packed_input_ids = torch.full(packed_shape, fill_value=pad_token_id, dtype=torch.int32)
    packed_new_key_location = torch.zeros(packed_shape, dtype=torch.int32)
    packed_new_value_location = torch.zeros(packed_shape, dtype=torch.int32)
    position_ids = torch.ones(packed_shape, dtype=torch.long)

    # initialize causal mask
    if compact_mask:
        causal_mask = torch.zeros((packed_batch_size, bucket_size), dtype=torch.uint8)
    else:
        causal_mask = torch.zeros((packed_batch_size, bucket_size, bucket_size), dtype=torch.bool)

    # fill the new attention mask and mark the logit locations
    for index, target_location in enumerate(target_locations):
        # record new target locations
        logit_target_location = []
        for packing_idx, (start, end) in enumerate(target_location):
            (original_index, original_start, original_end) = real_locations.pop(0)
            packed_attention_mask[index][start:end] = True
            packed_input_ids[index][start:end] = input_ids[original_index][
                original_start:original_end
            ]
            packed_new_key_location[index][start:end] = new_key_location[original_index][
                original_start:original_end
            ]
            packed_new_value_location[index][start:end] = new_value_location[original_index][
                original_start:original_end
            ]
            position_ids[index][start:end] = torch.arange(end - start)
            logit_target_location.append(end - 1)

            if compact_mask:
                mask_value = packing_idx + 1  # 0 is reserved for padding
                causal_mask[index][start:end] = mask_value
            else:
                causal_mask[index][start:end, start:end] = torch.tril(
                    torch.ones((end - start, end - start), dtype=torch.bool)
                )
        logit_target_locations.append(logit_target_location)
    return (
        packed_attention_mask,
        packed_input_ids,
        causal_mask,
        logit_target_locations,
        position_ids,
        packed_new_key_location,
        packed_new_value_location,
    )
