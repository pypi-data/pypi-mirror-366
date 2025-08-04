from typing import List, Optional, Tuple

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
            position_ids[index][start:end] = torch.arange(end - start)
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
    device = input_ids.device
    packed_attention_mask = torch.zeros(packed_shape, dtype=torch.bool).to(device)
    packed_input_ids = torch.full(packed_shape, fill_value=pad_token_id, dtype=torch.int32).to(
        device
    )
    packed_new_key_location = torch.zeros(packed_shape, dtype=torch.int32).to(device)
    packed_new_value_location = torch.zeros(packed_shape, dtype=torch.int32).to(device)
    position_ids = torch.ones(packed_shape, dtype=torch.long).to(device)

    # initialize causal mask
    if compact_mask:
        causal_mask = torch.zeros((packed_batch_size, bucket_size), dtype=torch.uint8).to(device)
    else:
        causal_mask = torch.zeros(
            (packed_batch_size, bucket_size, bucket_size), dtype=torch.bool
        ).to(device)

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


class GreedyAttentionPacker:
    def __init__(self, pad_token_id: int):
        self.pad_token_id = pad_token_id

    def pack(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        **kwargs,
    ) -> Tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        List[List[int]],
    ]:
        """
        Packs input sequences and their associated attention masks into a compact representation suitable for efficient processing.

        Args:
            input_ids (torch.Tensor): The input token IDs.
            attention_mask (torch.Tensor): The attention mask indicating non-padding tokens.

        Returns:
            Tuple containing:
                - packed_input_ids (torch.Tensor)
                - packed_attention_mask (torch.Tensor)
                - packed_position_ids (torch.Tensor)
                - packed_causal_mask (torch.Tensor)
                - end_token_positions (List[List[int]])
        """  # noqa: E501
        assert input_ids.shape == attention_mask.shape

        # Assume input_ids and attention_mask have been bucketized.
        # That is, the shape of input_ids and attention_mask is (batch_size, bucket_size).
        # For example, batch_size = 3, bucket_size = 5.
        # attention_mask: [[1, 1, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 1, 0]
        _, bucket_size = attention_mask.shape

        # Calculate non-padding token counts and positions
        # non_padding_token_counts: [2, 3, 4]
        non_padding_token_counts = self._count_non_padding_tokens(attention_mask)

        # Find the positions of non-padding tokens
        # non_padding_token_positions: [(0, 0, 2), (1, 0, 3), (2, 0, 4)]
        # The tuple (i, start, end) represents the position of non-padding tokens in the i-th row.
        # end is exclusive.
        non_padding_token_positions = self._find_non_padding_token_positions(
            attention_mask, non_padding_token_counts
        )

        # Determine the packing positions
        # packing_positions: [[(3, 5), (0, 3)], [1, 5]]
        # The tuple (start, end) represents the start and end positions of the packed tokens in the row. # noqa
        # end is exclusive.
        # The list represents the packing positions for each row.
        # Implicitly, we are packing from the end of the row. Say, "Rightmost packing."
        packing_positions = self._determine_packing_positions(non_padding_token_counts, bucket_size)

        # Fill packed tensors
        (
            packed_input_ids,
            packed_attention_mask,
            packed_position_ids,
            packed_causal_mask,
            end_token_positions,
        ) = self._fill_packed_tensors(
            packing_positions,
            non_padding_token_positions,
            input_ids,
        )

        return (
            packed_input_ids,
            packed_attention_mask,
            packed_position_ids,
            packed_causal_mask,
            end_token_positions,  # Needs to locate the prom
        )

    def _count_non_padding_tokens(self, attention_mask: torch.Tensor) -> List[int]:
        # Example:
        # attention_mask: [[1, 1, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 1, 0]]
        # non_padding_token_counts: [2, 3, 4]
        return attention_mask.sum(dim=1).tolist()

    def _find_non_padding_token_positions(
        self, attention_mask: torch.Tensor, non_padding_token_counts: List[int]
    ) -> List[Tuple[int, int, int]]:
        # Example:
        # attention_mask: [[1, 1, 0, 0, 0], [1, 1, 1, 0, 0], [1, 1, 1, 1, 0]]
        # non_padding_token_counts: [2, 3, 4]
        # non_zero_indices: [[0, 0], [0, 1], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2], [2, 3]]
        # non_padding_token_positions: [(0, 0, 2), (1, 0, 3), (2, 0, 4)]
        non_zero_indices = (attention_mask != 0).nonzero(as_tuple=False).tolist()
        non_padding_token_positions = []
        for i, non_padding_token_count in enumerate(non_padding_token_counts):
            positions = [non_zero_indices.pop(0)[1] for _ in range(non_padding_token_count)]
            start_position = positions[0]
            end_position = positions[-1] + 1  # end is exclusive
            non_padding_token_positions.append((i, start_position, end_position))
        return non_padding_token_positions

    def _determine_packing_positions(
        self, non_padding_token_counts: List[int], bucket_size: int
    ) -> List[List[Tuple[int, int]]]:
        # "row" means packed row.
        packing_positions = []
        remaining_space_in_row = bucket_size
        current_row_positions = []

        # Example:
        # non_padding_token_counts: [2, 3, 4]
        # bucket_size: 5
        # packing_positions: [[(3, 5), (0, 3)], [(1, 5)]]
        for count in non_padding_token_counts:
            if remaining_space_in_row < count or len(current_row_positions) >= MAX_PACKING_PER_ROW:
                packing_positions.append(current_row_positions)
                current_row_positions = []
                remaining_space_in_row = bucket_size

            # Implicitly, we are packing from the end of the row. Say, "Rightmost packing."
            start_position = remaining_space_in_row - count
            end_position = remaining_space_in_row
            # For "Leftmost packing", set the start_position and end_position as follows.
            # start_position = bucket_size - remaining_space_in_row
            # end_position = start_position + count
            current_row_positions.append((start_position, end_position))
            remaining_space_in_row -= count

        if current_row_positions:
            packing_positions.append(current_row_positions)

        return packing_positions

    def _initialize_padded_tensor(
        self, packed_batch_size: int, bucket_size: int, pad: int, dtype: torch.dtype
    ) -> torch.Tensor:
        return torch.full((packed_batch_size, bucket_size), fill_value=pad, dtype=dtype)

    def _initialize_zero_tensor(
        self, packed_batch_size: int, bucket_size: int, dtype: torch.dtype
    ) -> torch.Tensor:
        return torch.zeros((packed_batch_size, bucket_size), dtype=dtype)

    def _initialize_zero_2d_tensor(
        self, packed_batch_size: int, bucket_size: int, dtype: torch.dtype
    ) -> torch.Tensor:
        return torch.zeros((packed_batch_size, bucket_size, bucket_size), dtype=dtype)

    def _fill_packed_tensors(
        self,
        packing_positions: List[List[Tuple[int, int]]],
        non_padding_token_positions: List[Tuple[int, int, int]],
        input_ids: torch.Tensor,
        packed_input_ids: Optional[torch.Tensor] = None,
        packed_attention_mask: Optional[torch.Tensor] = None,
        packed_position_ids: Optional[torch.Tensor] = None,
        packed_causal_mask: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        # Initialize packed tensors
        # All are zero-initialized with the shape of (packed_batch_size, bucket_size).
        packed_batch_size = len(packing_positions)
        bucket_size = input_ids.shape[1]
        packed_shape = (packed_batch_size, bucket_size)
        packed_input_ids = packed_input_ids or self._initialize_padded_tensor(
            *packed_shape, pad=self.pad_token_id, dtype=torch.int32
        )
        packed_attention_mask = packed_attention_mask or self._initialize_zero_tensor(
            *packed_shape, dtype=torch.bool
        )
        packed_position_ids = packed_position_ids or self._initialize_zero_tensor(
            *packed_shape, dtype=torch.long
        )
        packed_causal_mask = packed_causal_mask or self._initialize_zero_2d_tensor(
            *packed_shape, dtype=torch.bool
        )

        assert input_ids.shape[1] == packed_input_ids.shape[1]

        # Example:
        # Inputs:
        # set pad_token_id = -1
        # packing_positions: [[(3, 5), (0, 3)], [(1, 5)]]
        # non_padding_token_positions: [(0, 0, 2), (1, 0, 3), (2, 0, 4)]
        # input_ids: [[101, 102, -1, -1, -1], [201, 202, 203, -1, -1], [301, 302, 303, 304, -1]]

        # Returns:
        # packed_input_ids: [[201, 202, 203, 101, 102], [-1, 301, 302, 303, 304]]
        # packed_attention_mask: [[1, 1, 1, 1, 1], [0, 1, 1, 1, 1]]
        # packed_position_ids: [[0, 1, 2, 0, 1], [0, 0, 1, 2, 3]]
        # packed_causal_mask: [[[1, 0, 0, 0, 0],
        #                       [1, 1, 0, 0, 0],
        #                       [1, 1, 1, 0, 0],
        #                       [0, 0, 0, 1, 0],
        #                       [0, 0, 0, 1, 1]],
        #                       [[0, 0, 0, 0, 0],
        #                       [0, 1, 0, 0, 0],
        #                       [0, 1, 0, 0, 0],
        #                       [0, 1, 1, 0, 0],
        #                       [0, 1, 1, 1, 1]]]
        # end_token_positions: [[2, 4], [4]]
        end_token_positions: List[List[int]] = []
        for row_index, row_positions in enumerate(packing_positions):
            end_positions = []
            for start, end in row_positions:
                original_index = non_padding_token_positions.index((start, end))
                packed_input_ids[row_index][start:end] = input_ids[original_index][start:end]
                packed_attention_mask[row_index][start:end] = True
                packed_position_ids[row_index][start:end] = torch.arange(end - start)
                packed_causal_mask[row_index][start:end, start:end] = torch.tril(
                    torch.ones((end - start, end - start), dtype=torch.bool)
                )
                end_positions.append(end - 1)

            end_token_positions.append(end_positions)

        return (
            packed_input_ids,
            packed_attention_mask,
            packed_position_ids,
            packed_causal_mask,
            end_token_positions,
        )


class GreedyAttentionPackerForPagedAttention(GreedyAttentionPacker):
    def pack(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        new_key_location: torch.Tensor,
        new_value_location: torch.Tensor,
        **kwargs,
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
        Packs input sequences and their associated attention masks into a compact representation suitable for efficient processing.
        Additionally handles the new key and value locations for paged attention.

        Args:
            input_ids (torch.Tensor): The input token IDs.
            attention_mask (torch.Tensor): The attention mask indicating non-padding tokens.
            new_key_location (torch.Tensor): The new key location tensor for paged attention.
            new_value_location (torch.Tensor): The new value location tensor for paged attention.

        Returns:
            Tuple containing:
                - packed_input_ids (torch.Tensor)
                - packed_attention_mask (torch.Tensor)
                - packed_position_ids (torch.Tensor)
                - packed_causal_mask (torch.Tensor)
                - end_token_positions (List[List[int]])
                - packed_new_key_location (torch.Tensor)
                - packed_new_value_location (torch.Tensor)
        """  # noqa: E501

        assert input_ids.shape == attention_mask.shape

        # Assume input_ids and attention_mask have been bucketized.
        _, bucket_size = attention_mask.shape

        # Calculate non-padding token counts and positions
        non_padding_token_counts = self._count_non_padding_tokens(attention_mask)

        # Find the positions of non-padding tokens
        non_padding_token_positions = self._find_non_padding_token_positions(
            attention_mask, non_padding_token_counts
        )

        # Determine the packing positions
        packing_positions = self._determine_packing_positions(non_padding_token_counts, bucket_size)

        # Fill packed tensors
        (
            packed_input_ids,
            packed_attention_mask,
            packed_position_ids,
            packed_causal_mask,
            end_token_positions,
        ) = super()._fill_packed_tensors(
            packing_positions,
            non_padding_token_positions,
            input_ids,
        )

        packed_new_key_location, packed_new_value_location = (
            self._fill_packed_key_new_value_locations(
                packing_positions,
                non_padding_token_positions,
                new_key_location,
                new_value_location,
            )
        )

        return (
            packed_input_ids,
            packed_attention_mask,
            packed_position_ids,
            packed_causal_mask,
            # Needs to locate the end of each token, that is, the prompt's logit position.
            end_token_positions,
            packed_new_key_location,
            packed_new_value_location,
        )

    def _fill_packed_key_new_value_locations(
        self,
        packing_positions: List[List[Tuple[int, int]]],
        non_padding_token_positions: List[Tuple[int, int, int]],
        new_key_location: torch.Tensor,
        new_value_location: torch.Tensor,
        packed_new_key_location: Optional[torch.Tensor] = None,
        packed_new_value_location: Optional[torch.Tensor] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        packed_batch_size = len(packing_positions)
        bucket_size = new_key_location.shape[1]
        packed_shape = (packed_batch_size, bucket_size)
        packed_new_key_location = packed_new_key_location or self._initialize_zero_tensor(
            *packed_shape, dtype=torch.int32
        )
        packed_new_value_location = packed_new_value_location or self._initialize_zero_tensor(
            *packed_shape, dtype=torch.int32
        )

        for row_index, row_positions in enumerate(packing_positions):
            for start, end in row_positions:
                original_index = non_padding_token_positions.index((start, end))
                packed_new_key_location[row_index][start:end] = new_key_location[original_index][
                    start:end
                ]
                packed_new_value_location[row_index][start:end] = new_value_location[
                    original_index
                ][start:end]

        return packed_new_key_location, packed_new_value_location
