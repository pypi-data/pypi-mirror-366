from itertools import chain
from typing import List, Optional

import torch


class InputMetadata:
    def __init__(
        self,
        key_cache_idx: Optional[
            List[List[int]]
        ],  # represents key cache block indices that will be used for this phase
        value_cache_idx: Optional[List[List[int]]],
        block_max_seq_len: int,  # max(after new keys are added)!,
        block_size: int,
        is_prefill: bool,
        new_key_location: torch.Tensor = None,
        new_value_location: torch.Tensor = None,
    ) -> None:
        # new key location can have different tensor values such as
        # for prefill,
        # tensor should have shape [batch, max_block_per_seq]

        # for decode, to ignore tuples, we have two tensors
        # block_idx tensor should have shape [batch, 1]
        # toekn_idx tensor should have shape [batch, 1]

        self.new_key_location: torch.Tensor = new_key_location
        self.new_value_location: torch.Tensor = new_value_location

        self.block_size: int = block_size  # used
        self.is_prefill: bool = is_prefill  # used
        self.bucket_size = int(block_max_seq_len * block_size)
        self.valid_key_indices: torch.Tensor = torch.IntTensor(
            list(chain.from_iterable(key_cache_idx))
        )
        self.valid_value_indices: torch.Tensor = torch.IntTensor(
            list(chain.from_iterable(value_cache_idx))
        )
