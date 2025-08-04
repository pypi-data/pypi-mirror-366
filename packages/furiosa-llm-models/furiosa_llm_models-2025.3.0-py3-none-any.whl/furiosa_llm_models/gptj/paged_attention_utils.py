from itertools import chain
from typing import Dict, List, Optional

import torch


class InputMetadata:
    def __init__(
        self,
        past_key_cache_idx: Optional[
            List[List[int]]
        ],  # represents past key cache block indices that will be used for this phase
        past_value_cache_idx: Optional[List[List[int]]],
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
        self.past_valid_key_indices: torch.Tensor = torch.IntTensor(
            list(chain.from_iterable(past_key_cache_idx))
        )
        self.past_valid_value_indices: torch.Tensor = torch.IntTensor(
            list(chain.from_iterable(past_value_cache_idx))
        )
        self.num_generated_tokens = len(past_key_cache_idx[0])


# FIXME: move this function to .generators.paged_attention_generator
def prepare_inputs_for_paged_attention_generation(
    self,
    input_ids: torch.Tensor,
    input_metadata: InputMetadata,
    attention_mask: torch.Tensor,
    **kwargs,
) -> Dict:
    # we allow inputs with different sequence_length
    updated_input_ids = input_ids
    if not input_metadata.is_prefill:
        updated_input_ids = input_ids[:, -1:]

    if attention_mask is None:
        raise ValueError("attention_mask is None. It should be provided at this point.")

    model_inputs = {"input_ids": updated_input_ids}

    model_inputs.update(
        {
            "use_cache": kwargs.get("use_cache"),
            "attention_mask": attention_mask,
            "token_type_ids": None,
        }
    )

    return model_inputs
