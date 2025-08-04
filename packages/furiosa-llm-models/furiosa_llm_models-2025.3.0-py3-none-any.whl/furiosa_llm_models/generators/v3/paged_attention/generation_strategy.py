import abc
import copy
import logging
import re
from typing import Dict, List, Optional, Tuple, Union

import torch
from torch.fx import GraphModule
from transformers import PreTrainedModel
from transformers.generation import (
    BeamScorer,
)
from transformers.generation.logits_process import (
    LogitsProcessorList,
    TemperatureLogitsWarper,
    TopKLogitsWarper,
    TopPLogitsWarper,
)
from transformers.generation.stopping_criteria import (
    StoppingCriteriaList,
    validate_stopping_criteria,
)
from transformers.generation.utils import BeamSearchDecoderOnlyOutput, GreedySearchDecoderOnlyOutput
from transformers.modeling_outputs import CausalLMOutputWithCrossAttentions, CausalLMOutputWithPast

from ..packing import greedy_attention_packing
from .generation_utils import create_key_value_blocks

SUPPORTED_GENERATION_RETURN_DICT_TYPES = (CausalLMOutputWithPast, CausalLMOutputWithCrossAttentions)
logger = logging.getLogger(__name__)


class GenerationStrategy(abc.ABC):
    block_size = 1
    max_batch_size = 4

    def __init__(self, model: PreTrainedModel) -> None:
        self.model = model
        self.model_config = model.config

    def __call__(self, *args, **kwargs):
        return self.decode(*args, **kwargs)

    @abc.abstractmethod
    def decode(self, *args, **kwargs): ...

    def get_layer_device_map(self, model):
        if hasattr(model, "device_map") and model.device_map is not None:
            items = list(model.device_map.items())
            layer_device_map = {}
            for i in range(1, len(items)):
                if "layer" in items[i][0] and "norm" not in items[i][0]:
                    layer_idx = int(re.findall(r"[0-9]+", items[i][0])[-1])
                    layer_device_map[str(layer_idx)] = items[i][1]
            return layer_device_map
        else:
            return None

    def create_key_value_blocks(
        self,
        batch_size: int,
        bucket_size: int,
        kv_dtype: torch.dtype,
        device: torch.device,
        is_draft: bool = False,
        device_map: Dict = None,
    ) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        batch_size = min(batch_size, self.max_batch_size)

        # block size: 1
        # num_blocks = 1 (dummy pad token) + bucket_size (max_length) * batch_size * 2 (for each key and value) # noqa
        # key_value_blocks:
        # layer 마다 (num_blocks, block_size, num_heads, head_size) x 2 가짐.
        if is_draft:
            # syo: check
            key_value_blocks = create_key_value_blocks(
                model_config=self.draft_config,
                batch_size=batch_size,
                block_size=self.block_size,
                device=device,
                bucket_size=bucket_size,
                kv_dtype=kv_dtype,
                device_map=device_map,
            )

        else:
            key_value_blocks = create_key_value_blocks(
                model_config=self.model_config,
                batch_size=batch_size,
                block_size=self.block_size,
                device=device,
                bucket_size=bucket_size,
                kv_dtype=kv_dtype,
                device_map=device_map,
            )

        _, block_size, _, _ = key_value_blocks[0][0].shape

        if bucket_size % block_size != 0:
            raise ValueError(
                f"Bucket size ({bucket_size}) should be divisible by block size ({block_size})"
            )

        if self.block_size != 1:
            raise ValueError(
                "Block size is fixed for RNGD architecture. Got block_size: {block_size} != 1"
            )

        return key_value_blocks

    def initialize_key_value_block_indices(
        self, key_value_blocks: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> torch.Tensor:
        block_indices, block_size, _, _ = key_value_blocks[0][0].shape
        self.block_size = block_size

        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []

        # Below fields keep track of prompt block indices which are shared across beam candidates
        self.prompt_key_block_indices: List[List[int]] = []
        self.prompt_value_block_indices: List[List[int]] = []

        self.available_block_indices = list(range(1, block_indices))
        self.zero_block_index = 0  # this is a special zero block
        self.total_block_count = block_indices

    def initialize_key_value_block_indices_draft(
        self, key_value_blocks: List[Tuple[torch.Tensor, torch.Tensor]]
    ) -> torch.Tensor:
        block_indices, block_size, _, _ = key_value_blocks[0][0].shape
        self.block_size_draft = block_size

        self.active_key_block_indices_draft: List[List[int]] = []
        self.active_value_block_indices_draft: List[List[int]] = []

        # Below fields keep track of prompt block indices which are shared across beam candidates
        self.prompt_key_block_indices_draft: List[List[int]] = []
        self.prompt_value_block_indices_draft: List[List[int]] = []

        self.available_block_indices_draft = list(range(1, block_indices))
        self.zero_block_index_draft = 0  # this is a special zero block
        self.total_block_count_draft = block_indices

    def move_kv_cache_block_in_place(
        self, seq_idx: int, new_location: torch.Tensor, existing_block_indices: List[List[int]]
    ) -> None:
        # new key location should always be shape [batch, 1]
        for single_batch_block_indices, new_index in zip(existing_block_indices, new_location):
            single_batch_block_indices[seq_idx] = new_index.item()

    def move_kv_cache_block_in_place_v2(
        self, seq_idx, new_location: torch.Tensor, existing_block_indices: List[List[int]]
    ) -> None:
        # here, seq_idx is tensor

        # new key location should always be shape [batch, 1]
        batch_idx = 0
        for single_batch_block_indices, new_index in zip(existing_block_indices, new_location):
            single_batch_block_indices[seq_idx[batch_idx]] = new_index.item()
            batch_idx += 1

    def move_kv_cache_block_in_place_verify_v2(
        self, seq_idx, sp_len, new_location: torch.Tensor, existing_block_indices: List[List[int]]
    ) -> None:
        # here, seq_idx is tensor

        # new key location should always be shape [batch, 1]
        batch_idx = 0
        for single_batch_block_indices in existing_block_indices:
            for sp_idx in range(sp_len):
                single_batch_block_indices[seq_idx[batch_idx] + sp_idx] = new_location[batch_idx][
                    sp_idx
                ].item()
            batch_idx += 1

    def reset(self):
        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []
        self.available_block_indices = list(range(1, self.total_block_count))


class GreedySearch(GenerationStrategy):
    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        use_sequence_axis: bool = False,
        use_unified_kv_indices: bool = False,
        **model_kwargs,
    ):
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device_map = self.get_layer_device_map(self.model)

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device, device_map=device_map
        )
        self.initialize_key_value_block_indices(key_value_blocks)
        # ----------- initial_settings -----------------
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size <= self.max_batch_size

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        device = input_ids.device
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask[:, :prompt_len] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids[:, :prompt_len] = starting_position_ids

        sequence_idx = prompt_len - 1
        is_prefill = True

        scores = None

        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)
        next_tokens = None

        # start generating new tokens
        for i in range(max_length - prompt_len):
            if is_prefill:
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask
                )

                (
                    packed_input_ids,
                    _,
                    causal_mask,
                    packed_position_ids,
                    logit_target_locations,
                    new_key_location,
                    new_value_location,
                ) = self.prepare_prefill_inputs(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    new_key_location=new_key_location,
                    new_value_location=new_value_location,
                    pad_token_id=pad_token_id,
                )  # original attention mask, original position ids

                forward_kwargs = {
                    "input_ids": packed_input_ids,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": packed_position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

            else:
                (input_ids, attention_mask, position_ids) = self.prepare_decode_inputs(
                    next_input_ids=next_tokens,
                    prev_attention_mask=attention_mask,
                    is_first_decode=(True if i == 1 else False),  # FIXME: hacky
                    seq_idx=sequence_idx,
                )

                logit_target_locations = None  # for decode, not needed

                (
                    new_key_location,
                    new_value_location,
                    valid_key_indices,
                    valid_value_indices,
                ) = self.prepare_decode_input_metadata()

                forward_kwargs = {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "causal_mask": None,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": valid_key_indices,
                    "past_valid_value_indices": valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }
                # support for model types that preserve sequence axis when decoding.
                if use_sequence_axis:
                    forward_kwargs["attention_mask"] = forward_kwargs["attention_mask"].unsqueeze(1)

            # For llama3 merged_idx models, unify kv indices.
            if use_unified_kv_indices:
                past_valid_kv_indices = forward_kwargs["past_valid_key_indices"]
                new_kv_location = forward_kwargs["new_key_location"]
                del forward_kwargs["past_valid_key_indices"]
                del forward_kwargs["past_valid_value_indices"]
                del forward_kwargs["new_key_location"]
                del forward_kwargs["new_value_location"]
                forward_kwargs["past_valid_kv_indices"] = past_valid_kv_indices
                forward_kwargs["new_kv_location"] = new_kv_location

            outputs = self.model(**forward_kwargs)

            if not is_prefill:
                # now copy the new_key location back to original place for decode_phase
                self.move_kv_cache_block_in_place(
                    seq_idx=sequence_idx,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place(
                    seq_idx=sequence_idx,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )

            # done
            outputs = handle_outputs(outputs)

            # done
            next_tokens = self.find_next_tokens(
                outputs,
                logit_target_locations,
                starting_input_ids,
                logits_processor,
                unfinished_sequences,
                pad_token_id,
                is_prefill,
            )

            starting_input_ids = torch.cat([starting_input_ids, next_tokens[:, None]], dim=-1)

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            if stopping_criteria(starting_input_ids, scores).all():
                break

            sequence_idx += 1

            # prepare for next phase
            is_prefill = False

        # reset must be called
        self.reset()
        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=starting_input_ids, scores=scores)
        return starting_input_ids

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-1])
            valid_value_indices.extend(value_batch[:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    def prepare_prefill_inputs(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        new_key_location: torch.Tensor,
        new_value_location: torch.Tensor,
        pad_token_id: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        (
            packed_attention_mask,
            packed_input_ids,
            causal_mask,
            logit_target_locations,
            packed_position_ids,
            packed_new_key_location,
            packed_new_value_location,
        ) = greedy_attention_packing(
            input_ids,
            attention_mask,
            new_key_location,
            new_value_location,
            pad_token_id=pad_token_id,
        )
        return (
            packed_input_ids,
            packed_attention_mask,
            causal_mask,
            packed_position_ids,
            logit_target_locations,
            packed_new_key_location,
            packed_new_value_location,
        )

    def prepare_decode_inputs(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        next_attention_mask = prev_attention_mask.clone()

        if is_first_decode:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
            # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            next_attention_mask[:, -1] = 1
        else:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
            next_attention_mask[:, seq_idx - 1] = 1

        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]

        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        logit_target_locations: Optional[List[List[int]]],
        input_ids: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList],
        unfinished_sequences: torch.Tensor,
        pad_token_id: int,
        is_prefill: bool,
    ) -> torch.Tensor:
        next_tokens_scores: torch.Tensor
        if is_prefill:
            # outputs should be logits which would have shape of [batch, seq_len, embedding_dimension] # noqa
            # loop through each batch and find the logit location due to attention_packing
            next_token_logits = []
            for single_batch_logit, single_batch_logit_target_location in zip(
                logits, logit_target_locations
            ):
                assert single_batch_logit.dim() == 2
                for logit_target in single_batch_logit_target_location:
                    # logit target will just be index
                    next_token_logits.append(
                        single_batch_logit[logit_target]
                    )  # will be [embedding_dimension]

            # stack this back to [batch, vocab_size]
            next_token_logits = torch.stack(next_token_logits)

        else:
            next_token_logits = logits[:, 0, :]  # for decode seq_len would just be 1

        next_tokens_scores = logits_processor(input_ids, next_token_logits)
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens


class BeamSearch(GreedySearch):
    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        beam_scorer: BeamScorer,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ):
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device
        )
        self.initialize_key_value_block_indices(key_value_blocks)
        # ----------- initial_settings -----------------
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask[:, :prompt_len] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids[:, :prompt_len] = starting_position_ids

        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]

        if max_length is not None:
            logger.warning(
                "`max_length` is deprecated in this function, use "
                "`stopping_criteria=StoppingCriteriaList(MaxLengthCriteria(max_length=max_length))`\
                      instead."
            )
            stopping_criteria = validate_stopping_criteria(stopping_criteria, max_length)

        # beam search config
        batch_size = len(beam_scorer._beam_hyps)
        num_beams = beam_scorer.num_beams
        batch_beam_size, _ = input_ids.shape
        # TODO(this is because we use bucketization)
        cur_len = prompt_len

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size // num_beams <= self.max_batch_size

        if num_beams * batch_size != batch_beam_size:
            raise ValueError(
                f"Batch dimension of `input_ids` should be {num_beams * batch_size}, "
                f"but is {batch_beam_size}."
            )

        beam_scores = torch.zeros(
            (batch_size, num_beams), dtype=torch.float, device=input_ids.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        scores = None
        beam_indices = None

        is_prefill = True
        is_first_decode = False
        next_input_ids = None
        generated_ids = starting_input_ids

        while True:
            if is_prefill:
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask, batch_size, num_beams
                )
                (
                    packed_input_ids,
                    _,
                    causal_mask,
                    packed_position_ids,
                    logit_target_locations,
                    new_key_location,
                    new_value_location,
                ) = self.prepare_prefill_inputs(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    new_key_location=new_key_location,
                    new_value_location=new_value_location,
                    pad_token_id=pad_token_id,
                )  # original attention mask, original position ids

                forward_kwargs = {
                    "input_ids": packed_input_ids,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": packed_position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

                is_first_decode = True
            else:
                (next_input_ids, attention_mask, position_ids) = self.prepare_decode_inputs(
                    next_input_ids=next_input_ids,
                    prev_attention_mask=attention_mask,
                    is_first_decode=is_first_decode,
                    seq_idx=cur_len - 1,
                )

                logit_target_locations = None  # for decode, not needed

                (
                    new_key_location,
                    new_value_location,
                    valid_key_indices,
                    valid_value_indices,
                ) = self.prepare_decode_input_metadata()

                forward_kwargs = {
                    "input_ids": next_input_ids,
                    "attention_mask": attention_mask,
                    "causal_mask": None,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": valid_key_indices,
                    "past_valid_value_indices": valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

                is_first_decode = False

            outputs = self.model(**forward_kwargs)
            logits = handle_outputs(outputs)

            next_token_logits = self.find_next_tokens(logits, logit_target_locations, is_prefill)
            # hack: adjust tokens for Marian. For Marian we have to make sure that the `pad_token_id` # noqa
            # cannot be generated both before and after the `nn.functional.log_softmax` operation.
            next_token_logits = self.adjust_logits_during_generation(
                next_token_logits, cur_len=cur_len
            )
            next_token_scores = torch.nn.functional.log_softmax(
                next_token_logits, dim=-1
            )  # [batch_size * num_beams, vocab_size]

            next_token_scores_processed = logits_processor(generated_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                next_token_scores
            )

            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

            next_token_scores, next_tokens = torch.topk(
                next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
            )
            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size

            beam_outputs = beam_scorer.process(
                generated_ids,
                next_token_scores,
                next_tokens,
                next_indices,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                beam_indices=beam_indices,
            )
            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]

            generated_ids = torch.cat(
                [generated_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1
            )
            if not is_prefill:
                # now copy the new_key location back to original place for decode_phase
                self.move_kv_cache_block_in_place(
                    seq_idx=cur_len - 1,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place(
                    seq_idx=cur_len - 1,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )
            # TODO(DONGHUN) based on this idx adjust the block index
            # we know new beams are chosen at this point
            new_key_block_indices = self.adjust_kv_cache_block(
                beam_idx, self.active_key_block_indices
            )
            self.active_key_block_indices = new_key_block_indices
            new_value_block_indices = self.adjust_kv_cache_block(
                beam_idx, self.active_value_block_indices
            )
            self.active_value_block_indices = new_value_block_indices

            cur_len = cur_len + 1
            if beam_scorer.is_done or stopping_criteria(generated_ids, scores):
                break

            # v2.Generator specific variables
            is_prefill = False
            next_input_ids = beam_next_tokens

        sequence_outputs = beam_scorer.finalize(
            generated_ids,
            beam_scores,
            next_tokens,
            next_indices,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            max_length=max_length,
            beam_indices=beam_indices,
        )

        # reset must be called for paged attention to call generate again
        self.reset()

        if return_dict_in_generate:
            return BeamSearchDecoderOnlyOutput(
                sequences=sequence_outputs["sequences"],
                sequences_scores=sequence_outputs["sequence_scores"],
                scores=scores,
                beam_indices=sequence_outputs["beam_indices"],
            )
        else:
            return sequence_outputs["sequences"]

    def prepare_prefill_input_metadata(
        self,
        attention_mask: torch.Tensor,
        batch_size: int,
        num_beams: int,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        # beams belonging to same prompts should share blocks

        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for count in range(batch_size):
            idx = count * num_beams
            single_attention_mask = attention_mask[idx]
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            # at this point block has been created
            for _ in range(num_beams):
                self.active_key_block_indices.append(copy.deepcopy(block_indices))
                self.active_value_block_indices.append(copy.deepcopy(block_indices))

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def adjust_kv_cache_block(
        self, beam_idx: torch.Tensor, existing_block_indices: List[List[int]]
    ):
        new_block_indices = []
        for idx in beam_idx:
            existing_block_index = existing_block_indices[idx]
            new_block_indices.append(copy.deepcopy(existing_block_index))

        return new_block_indices

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        logit_target_locations: Optional[List[List[int]]],
        is_prefill: bool,
    ):
        next_tokens_scores: torch.Tensor
        if is_prefill:
            # outputs should be logits which would have shape of [batch, seq_len, embedding_dimension] # noqa
            # loop through each batch and find the logit location due to attention_packing
            next_tokens_scores = []
            for single_batch_logit, single_batch_logit_target_location in zip(
                logits, logit_target_locations
            ):
                assert single_batch_logit.dim() == 2
                for logit_target in single_batch_logit_target_location:
                    # logit target will just be index
                    next_tokens_scores.append(
                        single_batch_logit[logit_target]
                    )  # will be [embedding_dimension]

            # stack this back to [batch, vocab_size]
            next_tokens_scores = torch.stack(next_tokens_scores)

        else:
            next_tokens_scores = logits[:, 0, :]  # for decode seq_len would just be 1
        return next_tokens_scores

    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L564-L568
    def adjust_logits_during_generation(
        self, logits: torch.FloatTensor, **kwargs
    ) -> torch.FloatTensor:
        """
        Implement in subclasses of [`PreTrainedModel`] for custom behavior to adjust the logits in \
            the generate method.
        """
        return logits


class MLPerfSubmissionGreedySearch(GreedySearch):
    pass


class MLPerfSubmissionBeamSearch(BeamSearch):
    @torch.no_grad()
    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        beam_scorer: BeamScorer,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ) -> Union[List[str], torch.Tensor]:
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """

        # max_new_tokens is required for MLPerfSubmissionBeamSearch
        max_new_tokens = model_kwargs["max_new_tokens"]

        # logit processor eos_token_id should be in the same device with input_id
        for logit_processor in logits_processor:
            logit_processor.eos_token_id = logit_processor.eos_token_id.to(input_ids.device)

        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device
        )
        self.initialize_key_value_block_indices(key_value_blocks)
        # ----------- initial_settings -----------------
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask[:, :prompt_len] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids[:, :prompt_len] = starting_position_ids

        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]

        # beam search config
        batch_size = len(beam_scorer._beam_hyps)
        num_beams = beam_scorer.num_beams
        batch_beam_size, _ = input_ids.shape
        # TODO(this is because we use bucketization)
        cur_len = prompt_len

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size // num_beams <= self.max_batch_size

        if num_beams * batch_size != batch_beam_size:
            raise ValueError(
                f"Batch dimension of `input_ids` should be {num_beams * batch_size}, "
                f"but is {batch_beam_size}."
            )

        beam_scores = torch.zeros(
            (batch_size, num_beams), dtype=torch.float, device=input_ids.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        scores = None
        beam_indices = None

        is_prefill = True
        is_first_decode = False
        generated_ids = starting_input_ids
        next_input_ids = None
        count = 0
        max_prompt_len = bucket_size - max_new_tokens

        while True:
            if is_prefill:
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask, batch_size, num_beams, max_prompt_len
                )
                (
                    packed_input_ids,
                    _,
                    causal_mask,
                    packed_position_ids,
                    logit_target_locations,
                    new_key_location,
                    new_value_location,
                ) = self.prepare_prefill_inputs(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    new_key_location=new_key_location,
                    new_value_location=new_value_location,
                    pad_token_id=pad_token_id,
                )  # original attention mask, original position ids
                forward_kwargs = {
                    "input_ids": packed_input_ids.to(device),
                    "attention_mask": None,
                    "causal_mask": causal_mask.to(device),
                    "position_ids": packed_position_ids.to(device),
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location.to(device),
                    "new_value_location": new_value_location.to(device),
                    "past_valid_key_prompt_indices": None,
                    "past_valid_key_decode_indices": None,
                    "past_valid_value_prompt_indices": None,
                    "past_valid_value_decode_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                    "num_beam": num_beams,
                    "max_new_tokens": max_new_tokens,
                    "num_real_batch": batch_size,
                }

                is_first_decode = True
            else:
                (next_input_ids, attention_mask, position_ids) = self.prepare_decode_inputs(
                    next_input_ids=next_input_ids,
                    prev_attention_mask=attention_mask,
                    is_first_decode=is_first_decode,
                    seq_idx=max_prompt_len + count - 1,
                )

                logit_target_locations = None  # for decode, not needed

                (
                    new_key_location,
                    new_value_location,
                    past_valid_key_prompt_indices,
                    past_valid_key_decode_indices,
                    past_valid_value_prompt_indices,
                    past_valid_value_decode_indices,
                ) = self.prepare_decode_input_metadata(max_prompt_len=max_prompt_len)

                forward_kwargs = {
                    "input_ids": next_input_ids,
                    "attention_mask": attention_mask,
                    "causal_mask": None,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_prompt_indices": past_valid_key_prompt_indices,
                    "past_valid_key_decode_indices": past_valid_key_decode_indices,
                    "past_valid_value_prompt_indices": past_valid_value_prompt_indices,
                    "past_valid_value_decode_indices": past_valid_value_decode_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                    "num_beam": num_beams,
                    "max_new_tokens": max_new_tokens,
                    "num_real_batch": batch_size,
                }

                is_first_decode = False

            outputs = self.model(**forward_kwargs)
            logits = handle_outputs(outputs)

            if is_prefill:
                next_token_scores = self.find_next_tokens(
                    logits, logit_target_locations, is_prefill
                )
            else:
                # For decode, we will use the logits as scores as model outputs
                next_token_scores = logits[:, -1]

            next_token_scores_processed = logits_processor(generated_ids, next_token_scores)

            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                next_token_scores
            )

            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

            next_token_scores, next_tokens = torch.topk(
                next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
            )

            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size

            beam_outputs = beam_scorer.process(
                generated_ids,
                next_token_scores,
                next_tokens,
                next_indices,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                beam_indices=beam_indices,
            )

            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]

            generated_ids = torch.cat(
                [generated_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1
            )

            if not is_prefill:
                # now copy the new_key location back to original place for decode_phase
                self.move_kv_cache_block_in_place(
                    seq_idx=max_prompt_len + count - 1,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place(
                    seq_idx=max_prompt_len + count - 1,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )
            # TODO(DONGHUN) based on this idx adjust the block index
            # we know new beams are chosen at this point
            new_key_block_indices = self.adjust_kv_cache_block(
                beam_idx, self.active_key_block_indices
            )
            self.active_key_block_indices = new_key_block_indices
            new_value_block_indices = self.adjust_kv_cache_block(
                beam_idx, self.active_value_block_indices
            )
            self.active_value_block_indices = new_value_block_indices

            cur_len = cur_len + 1
            count += 1

            if beam_scorer.is_done or count >= max_new_tokens:
                break

            # v2.Generator specific variables
            is_prefill = False
            next_input_ids = beam_next_tokens

        sequence_outputs = beam_scorer.finalize(
            generated_ids,
            beam_scores,
            next_tokens,
            next_indices,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            max_length=max_length,
            beam_indices=beam_indices,
        )

        # reset must be called for paged attention to call generate again
        self.reset()

        if return_dict_in_generate:
            return BeamSearchDecoderOnlyOutput(
                sequences=sequence_outputs["sequences"],
                sequences_scores=sequence_outputs["sequence_scores"],
                scores=scores,
                beam_indices=sequence_outputs["beam_indices"],
            )
        else:
            return sequence_outputs["sequences"]

    def prepare_prefill_input_metadata(
        self,
        attention_mask: torch.Tensor,
        batch_size: int,
        num_beams: int,
        max_prompt_len: int,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        # beams belonging to same prompts should share blocks

        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for count in range(batch_size):
            idx = count * num_beams
            single_attention_mask = attention_mask[idx]
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            # at this point block has been created
            # MAX_PROMPT_LEN is required to remove dynamic characteristc to decode phase
            self.prompt_key_block_indices.append(copy.deepcopy(block_indices[:max_prompt_len]))
            self.prompt_value_block_indices.append(copy.deepcopy(block_indices[:max_prompt_len]))

            for _ in range(num_beams):
                self.active_key_block_indices.append(copy.deepcopy(block_indices))
                self.active_value_block_indices.append(copy.deepcopy(block_indices))

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self, max_prompt_len: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        past_valid_key_decode_indices = []
        past_valid_value_decode_indices = []

        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            past_valid_key_decode_indices.extend(key_batch[max_prompt_len:-1])
            past_valid_value_decode_indices.extend(value_batch[max_prompt_len:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)

        past_valid_key_prompt_indices = torch.IntTensor(self.prompt_key_block_indices)
        past_valid_value_prompt_indices = torch.IntTensor(self.prompt_value_block_indices)
        past_valid_key_decode_indices = torch.IntTensor(past_valid_key_decode_indices)
        past_valid_value_decode_indices = torch.IntTensor(past_valid_value_decode_indices)

        return (
            new_key_location,
            new_value_location,
            past_valid_key_prompt_indices,
            past_valid_key_decode_indices,
            past_valid_value_prompt_indices,
            past_valid_value_decode_indices,
        )


def handle_outputs(
    outputs: Tuple[torch.Tensor, List[Tuple[torch.Tensor, torch.Tensor]]],
) -> torch.Tensor:
    # handle outputs differently based on prefill vs decode

    # SUPPORTED_GENERATION_RETURN_DICT_TYPES[1],
    # i.e., CausalLMOutputWithCrossAttentions is not yet checked.
    if isinstance(outputs, SUPPORTED_GENERATION_RETURN_DICT_TYPES[0]):
        logits = outputs.to_tuple()[0]
    elif isinstance(outputs, Tuple):
        logits = outputs[0]
    elif isinstance(outputs, Dict):
        logits = outputs["logits"]
    else:
        raise ValueError(f"Unsupported generation output type: {type(outputs)}")
    return logits


class GreedySearchNoPacking(GenerationStrategy):
    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ):
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device
        )
        self.initialize_key_value_block_indices(key_value_blocks)
        # ----------- initial_settings -----------------
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size <= self.max_batch_size

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        device = input_ids.device
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask[:, :prompt_len] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids[:, :prompt_len] = starting_position_ids

        sequence_idx = prompt_len - 1
        is_prefill = True

        scores = None

        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)
        next_tokens = None

        # start generating new tokens
        for i in range(max_length - prompt_len):
            if is_prefill:
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask
                )

                causal_mask, logit_target_locations = self.prepare_prefill_inputs(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                )  # original attention mask, original position ids

                forward_kwargs = {
                    "input_ids": input_ids,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

            else:
                (input_ids, attention_mask, position_ids) = self.prepare_decode_inputs(
                    next_input_ids=next_tokens,
                    prev_attention_mask=attention_mask,
                    is_first_decode=(True if i == 1 else False),  # FIXME: hacky
                    seq_idx=sequence_idx,
                )

                logit_target_locations = None  # for decode, not needed

                (
                    new_key_location,
                    new_value_location,
                    valid_key_indices,
                    valid_value_indices,
                ) = self.prepare_decode_input_metadata()

                forward_kwargs = {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "causal_mask": None,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": valid_key_indices,
                    "past_valid_value_indices": valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

            outputs = self.model(**forward_kwargs)

            if not is_prefill:
                # now copy the new_key location back to original place for decode_phase
                self.move_kv_cache_block_in_place(
                    seq_idx=sequence_idx,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place(
                    seq_idx=sequence_idx,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )

            # done
            outputs = handle_outputs(outputs)

            # done
            next_tokens = self.find_next_tokens(
                outputs,
                logit_target_locations,
                starting_input_ids,
                logits_processor,
                unfinished_sequences,
                pad_token_id,
                is_prefill,
            )

            starting_input_ids = torch.cat([starting_input_ids, next_tokens[:, None]], dim=-1)

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            if stopping_criteria(starting_input_ids, scores).all():
                break

            sequence_idx += 1

            # prepare for next phase
            is_prefill = False

        # reset must be called
        self.reset()
        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=starting_input_ids, scores=scores)
        return starting_input_ids

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-1])
            valid_value_indices.extend(value_batch[:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    def prepare_prefill_inputs(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )
        sequence_length = torch.sum(attention_mask, dim=-1)
        max_length = torch.max(sequence_length).item()
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][max_length - N : max_length, max_length - N : max_length] = torch.tril(
                torch.ones((N, N), dtype=torch.bool)
            )

        logit_target_locations = max_length
        return causal_mask, logit_target_locations

    def prepare_decode_inputs(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        next_attention_mask = prev_attention_mask.clone()

        if is_first_decode:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
            # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            next_attention_mask[:, -1] = 1
        else:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
            next_attention_mask[:, seq_idx - 1] = 1

        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]

        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        logit_target_locations: Optional[List[List[int]]],
        input_ids: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList],
        unfinished_sequences: torch.Tensor,
        pad_token_id: int,
        is_prefill: bool,
    ) -> torch.Tensor:
        next_tokens_scores: torch.Tensor
        if is_prefill:
            # logit target location is max_length
            next_token_logits = logits[:, logit_target_locations - 1, :]
        else:
            next_token_logits = logits[:, 0, :]  # for decode seq_len would just be 1

        next_tokens_scores = logits_processor(input_ids, next_token_logits)
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens


class SpecDec(GenerationStrategy):
    def __init__(self, model, draft_model, sp_len: int) -> None:
        if (
            isinstance(model, Dict)
            and isinstance(model["prefill"], GraphModule)
            and isinstance(model["decode"], GraphModule)
        ):
            self.model = self.prefill = model["prefill"]
            self.model_decode = model["decode"]
        else:
            self.model = model

        if (
            isinstance(draft_model, Dict)
            and isinstance(draft_model["prefill"], GraphModule)
            and isinstance(draft_model["decode"], GraphModule)
        ):
            self.draft_model = self.draft_prefill = draft_model["prefill"]
            self.draft_model_decode = draft_model["decode"]
        else:
            self.draft_model = draft_model

        self.model_config = self.model.config
        self.draft_config = self.draft_model.config
        self.sp_len = sp_len

        self.logits_warpers = []
        self.logits_warpers.append(TemperatureLogitsWarper(0.6))
        self.logits_warpers.append(TopKLogitsWarper(top_k=10, min_tokens_to_keep=1))
        self.logits_warpers.append(TopPLogitsWarper(top_p=0.4, min_tokens_to_keep=1))

    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ):
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        # target model key value blocks
        # num_blocks, block_size, num_head, head_size
        # block_size: bucket size

        device_map = self.get_layer_device_map(self.model)
        draft_device_map = self.get_layer_device_map(self.draft_model)

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size,
            bucket_size,
            kv_dtype,
            device,
            is_draft=False,
            device_map=device_map,
        )
        self.initialize_key_value_block_indices(key_value_blocks)

        # draft model key value blocks
        key_value_blocks_draft = model_kwargs.get(
            "key_value_blocks_draft"
        ) or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device, is_draft=True, device_map=draft_device_map
        )
        self.initialize_key_value_block_indices_draft(key_value_blocks_draft)

        # ----------- initial_settings -----------------
        original_length = torch.sum((input_ids != pad_token_id), dim=-1)
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size <= self.max_batch_size

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        device = input_ids.device
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask_for_prefill = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(
            device
        )
        attention_mask[:, :prompt_len] = starting_attention_mask
        attention_mask_for_prefill[:, -prompt_len:] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        input_ids_for_prefill = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids_for_prefill[:, -prompt_len:] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids_for_prefill = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(
            device
        )
        position_ids[:, :prompt_len] = starting_position_ids
        position_ids_for_prefill[:, -prompt_len:] = starting_position_ids

        sequence_idx = prompt_len - 1
        is_prefill = True

        scores = None

        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)
        next_tokens = None

        # get draft materials
        input_ids_draft = input_ids.clone()
        position_ids_draft = position_ids.clone()
        sequence_idx_draft = sequence_idx
        attention_mask_draft = attention_mask.clone()

        sequence_idx = torch.tensor(sequence_idx).repeat(batch_size).to(input_ids.device)
        sequence_idx_draft = (
            torch.tensor(sequence_idx_draft).repeat(batch_size).to(input_ids.device)
        )

        num_accepted = None
        # Run while loop when there are requests that are not finished.
        while unfinished_sequences.max() != 0:
            if is_prefill:
                # 여기선 올바른 자리에 넣어주기 위해 slice 모델이더라도 우측정렬 하지 않음.
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask_for_prefill
                )

                (new_key_location_draft, new_value_location_draft) = (
                    self.prepare_prefill_input_metadata_draft(attention_mask_for_prefill)
                )

                causal_mask, logit_target_locations = self.prepare_prefill_inputs_slice(
                    input_ids=input_ids_for_prefill,
                    attention_mask=attention_mask,
                )  # original attention mask, original position ids

                forward_kwargs = {
                    "input_ids": input_ids_for_prefill,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": position_ids_for_prefill,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

                forward_kwargs_draft = {
                    "input_ids": input_ids_for_prefill,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": position_ids_for_prefill,
                    "past_key_values": key_value_blocks_draft,
                    "new_key_location": new_key_location_draft,
                    "new_value_location": new_value_location_draft,
                    "past_valid_key_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }
                # If the model is a GraphModule, we need to switch the model to prefill.
                if isinstance(self.model, GraphModule) and self.model != self.prefill:
                    self.model = self.prefill

                if (
                    isinstance(self.draft_model, GraphModule)
                    and self.draft_model != self.draft_prefill
                ):
                    self.draft_model = self.draft_prefill

                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs:
                            del forward_kwargs[arg]

                if isinstance(self.draft_model, GraphModule):
                    for arg in self.draft_model.concrete_args:
                        if arg in forward_kwargs_draft:
                            del forward_kwargs_draft[arg]
                outputs = self.model(**forward_kwargs)
                outputs_draft = self.draft_model(**forward_kwargs_draft)

                outputs = handle_outputs(outputs)

                next_tokens = self.find_next_tokens(
                    outputs,
                    logit_target_locations,
                    starting_input_ids,
                    logits_processor,
                    unfinished_sequences,
                    pad_token_id,
                    is_prefill,
                )
                cur_len = logit_target_locations.squeeze(-1)
                first_decode = True  # syo FIXME: hacky
                sequence_idx += 1
                sequence_idx_draft += 1  # this new token will go into draft

                # slice model puts kv cache in last blocks. move them forward
                for i in range(batch_size):
                    self.active_key_block_indices_draft[i][:prompt_len] = (
                        self.active_key_block_indices_draft[i][-prompt_len:]
                    )
                    self.active_value_block_indices_draft[i][:prompt_len] = (
                        self.active_key_block_indices_draft[i][-prompt_len:]
                    )
                    self.active_key_block_indices[i][:prompt_len] = self.active_key_block_indices[
                        i
                    ][-prompt_len:]
                    self.active_value_block_indices[i][:prompt_len] = self.active_key_block_indices[
                        i
                    ][-prompt_len:]

                    self.active_key_block_indices_draft[i][-prompt_len:] = [
                        0 for _ in range(prompt_len)
                    ]
                    self.active_value_block_indices_draft[i][-prompt_len:] = [
                        0 for _ in range(prompt_len)
                    ]
                    self.active_key_block_indices[i][-prompt_len:] = [0 for _ in range(prompt_len)]
                    self.active_value_block_indices[i][-prompt_len:] = [
                        0 for _ in range(prompt_len)
                    ]

            else:
                # start of speculative decoding
                # when first decode, next_tokens are the output from prefill-phase.
                # draft for gamma number of times
                draft_tokens = [next_tokens]
                draft_logits = []
                # after first iteration, the seq_idxs will change.
                batch_size = input_ids_draft.size(0)

                for draft_iter in range(self.sp_len):
                    (input_ids_draft, attention_mask_draft, position_ids_draft) = (
                        self.prepare_decode_inputs_v2(
                            next_input_ids=next_tokens,
                            prev_attention_mask=attention_mask_draft,
                            is_first_decode=first_decode,  # FIXME: hacky
                            seq_idx=sequence_idx_draft,
                            num_accepted=num_accepted,
                        )
                    )
                    # rollback kv cache and update attention mask
                    if num_accepted is not None and draft_iter == 0:
                        # at least single speculative decoding have been performed

                        # update attention mask
                        for i in range(batch_size):
                            acc_num = num_accepted[i]

                            for idx in range(min(acc_num + 1, self.sp_len)):
                                attention_mask[i][sequence_idx[i] + idx] = 1

                            # update sequence length
                            if acc_num < self.sp_len:
                                sequence_idx[i] = sequence_idx[i] + acc_num + 1
                            else:
                                sequence_idx[i] = sequence_idx[i] + acc_num

                        # rollback kv cache
                        for i in range(batch_size):
                            empty_len = [0 for _ in range(bucket_size - sequence_idx[i])]
                            self.active_key_block_indices_draft[i][sequence_idx[i] :] = empty_len
                            self.active_value_block_indices_draft[i][sequence_idx[i] :] = empty_len

                            self.active_key_block_indices[i][sequence_idx[i] :] = empty_len
                            self.active_value_block_indices[i][sequence_idx[i] :] = empty_len

                        sequence_idx_draft = sequence_idx.clone()  # to actual draft index
                        num_accepted = None
                    first_decode = False  # FIXME: hacky

                    logit_target_locations = None  # for decode, not needed

                    (
                        new_key_location,
                        new_value_location,
                        valid_key_indices,
                        valid_value_indices,
                    ) = self.prepare_decode_input_metadata_draft()

                    # for draft model, use 2d mask
                    forward_kwargs_draft = {
                        "input_ids": input_ids_draft,
                        "attention_mask": attention_mask_draft,
                        "causal_mask": None,
                        "position_ids": position_ids_draft,
                        "past_key_values": key_value_blocks_draft,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": valid_key_indices,
                        "past_valid_value_indices": valid_value_indices,
                        "is_prefill": is_prefill,
                        "bucket_size": bucket_size,
                        "use_cache": False,
                    }

                    # If the model is a GraphModule, we need to switch the model to decode.
                    if (
                        isinstance(self.draft_model, GraphModule)
                        and self.draft_model != self.draft_model_decode
                    ):
                        self.draft_model = self.draft_model_decode

                    if isinstance(self.draft_model, GraphModule):
                        for arg in self.draft_model.concrete_args:
                            if arg in forward_kwargs_draft:
                                del forward_kwargs_draft[arg]

                    outputs_draft = self.draft_model(**forward_kwargs_draft)

                    # get argmax out of draft logits
                    outputs_draft = handle_outputs(outputs_draft)
                    draft_logits.append(outputs_draft.squeeze(1))

                    # done
                    next_tokens = self.find_next_tokens(
                        outputs_draft,
                        logit_target_locations,
                        starting_input_ids,
                        logits_processor,
                        unfinished_sequences,
                        pad_token_id,
                        is_prefill,
                    )
                    # if draft_iter != self.sp_len - 1:
                    draft_tokens.append(next_tokens)

                    self.move_kv_cache_block_in_place_v2(
                        seq_idx=sequence_idx_draft,
                        new_location=new_key_location,
                        existing_block_indices=self.active_key_block_indices_draft,
                    )
                    self.move_kv_cache_block_in_place_v2(
                        seq_idx=sequence_idx_draft,
                        new_location=new_value_location,
                        existing_block_indices=self.active_value_block_indices_draft,
                    )
                    sequence_idx_draft += 1  # this new token will go into draft

                draft_tokens = torch.stack(draft_tokens, dim=-1)  # concat draft tokens # B, sp_len
                draft_tokens_for_verify = draft_tokens[:, :-1]
                draft_logits = torch.stack(draft_logits, dim=1)  # B, sp_len

                # target run for verification
                (
                    new_key_location,
                    new_value_location,
                    valid_key_indices,
                    valid_value_indices,
                ) = self.prepare_decode_input_metadata(sp_len=self.sp_len)

                # verification step
                # verify_attention_mask =  # B, sp_len, N
                batch_size = input_ids.size(0)
                sp_attention_mask = []
                for batch_idx in range(batch_size):
                    batch_attention_mask = attention_mask[batch_idx].clone()  # N
                    batch_sp_attention_mask = []
                    for sp_idx in range(self.sp_len):
                        batch_attention_mask[-self.sp_len + sp_idx] = 1
                        batch_sp_attention_mask.append(batch_attention_mask.clone())
                    batch_sp_attention_mask = torch.stack(
                        batch_sp_attention_mask, dim=0
                    )  # sp_len, N
                    sp_attention_mask.append(batch_sp_attention_mask)
                sp_attention_mask = torch.stack(sp_attention_mask, dim=0)  # B, sp_len, N

                sp_position_ids = sp_attention_mask.long().cumsum(-1)[:, :, -1] - 1

                forward_kwargs_verify = {
                    "input_ids": draft_tokens_for_verify,
                    "attention_mask": sp_attention_mask,
                    "causal_mask": None,
                    "position_ids": sp_position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": valid_key_indices,
                    "past_valid_value_indices": valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                    "sp_len": self.sp_len,
                }

                # If the model is a GraphModule, we need to switch the model to decode.
                if isinstance(self.model, GraphModule) and self.model != self.model_decode:
                    self.model = self.model_decode

                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs_verify:
                            del forward_kwargs_verify[arg]

                target_output = handle_outputs(self.model(**forward_kwargs_verify))

                # following logit transformation in huggingface
                pad_num = torch.max(original_length) - original_length
                for logits_warper in self.logits_warpers:
                    for batch_idx in range(batch_size):
                        for sp_idx in range(self.sp_len):
                            candidate_input_ids = torch.cat(
                                (
                                    input_ids[batch_idx][
                                        pad_num[batch_idx] : cur_len[batch_idx] - 1
                                    ],
                                    draft_tokens[batch_idx][: sp_idx + 1],
                                ),
                                dim=-1,
                            )
                            target_output[batch_idx, sp_idx, :] = logits_warper(
                                candidate_input_ids[None, :],
                                target_output[batch_idx, sp_idx, :][None, :],
                            )

                self.move_kv_cache_block_in_place_verify_v2(
                    seq_idx=sequence_idx,
                    sp_len=self.sp_len,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place_verify_v2(
                    seq_idx=sequence_idx,
                    sp_len=self.sp_len,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )

                q = draft_logits.softmax(dim=-1)  # B, sp_len, V
                batch_indices = torch.arange(batch_size).unsqueeze(-1).expand(-1, self.sp_len)
                seq_indices = torch.arange(self.sp_len).unsqueeze(0).expand(batch_size, -1)
                q_i = q[batch_indices, seq_indices, draft_tokens[:, 1:]].squeeze(-1)  # B, sp len

                p = target_output.softmax(dim=-1)  # B, sp_len, V
                p_i = p[batch_indices, seq_indices, draft_tokens[:, 1:]].squeeze(-1)  # B, sp len

                probability_ratio = p_i / q_i
                r_i = torch.rand_like(probability_ratio)
                is_accepted = r_i <= probability_ratio
                num_accepted = torch.sum(((~is_accepted).cumsum(dim=-1) < 1), dim=-1)
                cur_len = cur_len.to(num_accepted.device)

                # put accepted tokens to
                batch_size = input_ids.size(0)
                bonus_tokens = []

                for i in range(batch_size):
                    num_acc = num_accepted[i]
                    if num_acc < self.sp_len:
                        input_ids[i][cur_len[i] : cur_len[i] + num_acc + 1] = draft_tokens[i][
                            : num_acc + 1
                        ]
                        cur_len[i] += num_acc + 1
                    else:
                        input_ids[i][cur_len[i] : cur_len[i] + num_acc] = draft_tokens[i][:num_acc]
                        cur_len[i] += num_acc

                    if num_acc < self.sp_len:
                        # rejection sampling
                        _p = p[i, num_acc]  # B, V
                        _q = q[i, num_acc]  # B, V
                        p_prime = torch.clamp((_p - _q), min=0)
                        p_prime.div_(p_prime.sum())
                        bonus_token = torch.multinomial(p_prime, num_samples=1)
                        bonus_tokens.append(bonus_token)

                    else:
                        bonus_token = draft_tokens[i][-1]
                        bonus_tokens.append(bonus_token)

                next_tokens = torch.tensor(bonus_tokens).to(input_ids.device)
                sequence_idx_draft = sequence_idx

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            max_cur_len = torch.max(cur_len)
            starting_input_ids = []
            for batch_idx in range(batch_size):
                pad = torch.tensor(
                    [pad_token_id for _ in range(max_cur_len - cur_len[batch_idx])]
                ).to(input_ids.device)
                padded_id = torch.cat((pad, input_ids[batch_idx][: cur_len[batch_idx]]))
                starting_input_ids.append(padded_id)
            starting_input_ids = torch.stack(starting_input_ids, dim=0).to(input_ids.dtype)
            # the final location will be pad - add bonus tokens
            starting_input_ids[:, -1] = next_tokens

            if stopping_criteria(starting_input_ids, scores).all():
                break

            is_prefill = False

        # reset must be called
        self.reset()
        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=input_ids, scores=scores)

        output_length = min(max_cur_len, max_length)
        return starting_input_ids[:, : output_length - 1]

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        # note: new_key_location and new_value_location are same for draft model

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_prefill_input_metadata_draft(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices_draft.pop())

            self.active_key_block_indices_draft.append(block_indices[:])
            self.active_value_block_indices_draft.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices_draft)
        new_value_location = torch.IntTensor(self.active_value_block_indices_draft)

        # note: new_key_location and new_value_location are same for draft model

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self, sp_len=1
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-sp_len])
            valid_value_indices.extend(value_batch[:-sp_len])

            # we use same block idx for key and value here

            key_blocks = []
            value_blocks = []
            for i in range(sp_len):
                new_block_idx = self.available_block_indices.pop()
                key_batch[-sp_len + i] = new_block_idx
                value_batch[-sp_len + i] = new_block_idx

                key_blocks.append(new_block_idx)
                value_blocks.append(new_block_idx)

            new_key_location.append(key_blocks)
            new_value_location.append(value_blocks)

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    # draft model does not require sp_len: it will generate tokens in autoregressive manner.
    def prepare_decode_input_metadata_draft(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices_draft, self.active_value_block_indices_draft
        ):
            valid_key_indices.extend(key_batch[:-1])  # 여기서 가져와야 함 - 에 해당하는 index 들
            valid_value_indices.extend(
                value_batch[:-1]
            )  # 여기서 가져와야 함 - 에 해당하는 index 들

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices_draft.pop()
            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    def prepare_prefill_inputs(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )
        sequence_length = torch.sum(attention_mask, dim=-1)
        max_length = torch.max(sequence_length).item()
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][max_length - N : max_length, max_length - N : max_length] = torch.tril(
                torch.ones((N, N), dtype=torch.bool)
            )

        logit_target_locations = torch.tensor(max_length).reshape(1, -1).repeat(batch_size, 1)
        return causal_mask, logit_target_locations

    # todo: slice 모델에서는 prefill inputs가 달라져야 한다.
    def prepare_prefill_inputs_slice(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )
        sequence_length = torch.sum(attention_mask, dim=-1)
        max_length = torch.max(sequence_length).item()
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][bucket_size - N :, bucket_size - N :] = torch.tril(
                torch.ones((N, N), dtype=torch.bool)
            )

        logit_target_locations = torch.tensor(max_length).reshape(1, -1).repeat(batch_size, 1)
        return causal_mask, logit_target_locations

    def prepare_decode_inputs(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        next_attention_mask = prev_attention_mask.clone()

        if is_first_decode:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
            # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            next_attention_mask[:, -1] = 1
        else:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
            next_attention_mask[:, seq_idx - 1] = 1

        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]

        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def prepare_decode_inputs_v2(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx,  # this is now a tensor
        num_accepted,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """

        batch_size = next_input_ids.size(0)
        next_attention_mask = prev_attention_mask.clone()
        if num_accepted is None:
            if is_first_decode:
                # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
                # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
                next_attention_mask[:, -1] = 1

            else:
                # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
                # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]

                for i in range(batch_size):
                    next_attention_mask[i][seq_idx[i] - 1] = 1

        else:
            # otherwise, we need to consider num_accepted
            # rollback attention_mask
            for i in range(batch_size):
                # rollback
                for sp_idx in range(self.sp_len):
                    next_attention_mask[i][seq_idx[i] + sp_idx] = 0

                for acc_idx in range(min(num_accepted[i] + 1, self.sp_len)):
                    next_attention_mask[i][seq_idx[i] + acc_idx] = 1
        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]
        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        logit_target_locations: Optional[List[List[int]]],
        input_ids: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList],
        unfinished_sequences: torch.Tensor,
        pad_token_id: int,
        is_prefill: bool,
    ) -> torch.Tensor:
        next_tokens_scores: torch.Tensor

        # when using slice model, every output has length 1 in sequence axis
        next_token_logits = logits[:, 0, :]  # for decode seq_len would just be 1

        next_tokens_scores = logits_processor(input_ids, next_token_logits)
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens


class SpecDecV2(GenerationStrategy):
    def __init__(self, model, draft_model, sp_len: int, temperature: float) -> None:
        if (
            isinstance(model, Dict)
            and isinstance(model["prefill"], GraphModule)
            and isinstance(model["decode"], GraphModule)
        ):
            self.model = self.prefill = model["prefill"]
            self.model_decode = model["decode"]
        else:
            self.model = model

        if (
            isinstance(draft_model, Dict)
            and isinstance(draft_model["prefill"], GraphModule)
            and isinstance(draft_model["decode"], GraphModule)
        ):
            self.draft_model = self.draft_prefill = draft_model["prefill"]
            self.draft_model_decode = draft_model["decode"]
        else:
            self.draft_model = draft_model

        self.model_config = self.model.config
        self.draft_config = self.draft_model.config
        self.sp_len = sp_len

        self.logits_warpers = []
        self.logits_warpers.append(TemperatureLogitsWarper(temperature))

    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ):
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        # target model key value blocks
        # num_blocks, block_size, num_head, head_size
        # block_size: bucket size

        device_map = self.get_layer_device_map(self.model)
        draft_device_map = self.get_layer_device_map(self.draft_model)

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size,
            bucket_size,
            kv_dtype,
            device,
            is_draft=False,
            device_map=device_map,
        )
        self.initialize_key_value_block_indices(key_value_blocks)

        # draft model key value blocks
        key_value_blocks_draft = model_kwargs.get(
            "key_value_blocks_draft"
        ) or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device, is_draft=True, device_map=draft_device_map
        )
        self.initialize_key_value_block_indices_draft(key_value_blocks_draft)

        # ----------- initial_settings -----------------
        original_length = torch.sum((input_ids != pad_token_id), dim=-1)
        pad_num = torch.max(original_length) - original_length
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape

        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size <= self.max_batch_size

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        device = input_ids.device
        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        attention_mask_for_prefill = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(
            device
        )
        attention_mask[:, :prompt_len] = starting_attention_mask
        attention_mask_for_prefill[:, -prompt_len:] = starting_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids[:, :prompt_len] = starting_input_ids

        input_ids_for_prefill = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        input_ids_for_prefill[:, -prompt_len:] = starting_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        position_ids_for_prefill = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(
            device
        )
        position_ids[:, :prompt_len] = starting_position_ids
        position_ids_for_prefill[:, -prompt_len:] = starting_position_ids

        sequence_idx = prompt_len - 1
        is_prefill = True

        scores = None

        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)
        next_tokens = None

        # get draft materials
        input_ids_draft = input_ids.clone()
        position_ids_draft = position_ids.clone()
        sequence_idx_draft = sequence_idx
        attention_mask_draft = attention_mask.clone()

        sequence_idx = torch.tensor(sequence_idx).repeat(batch_size).to(input_ids.device)
        sequence_idx_draft = (
            torch.tensor(sequence_idx_draft).repeat(batch_size).to(input_ids.device)
        )

        num_accepted = None
        # Run while loop when there are requests that are not finished.
        while unfinished_sequences.max() != 0:
            if is_prefill:
                # 여기선 올바른 자리에 넣어주기 위해 slice 모델이더라도 우측정렬 하지 않음.
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    attention_mask_for_prefill
                )

                sequence_length = torch.sum(attention_mask, dim=-1)
                sequence_length_draft = sequence_length.clone()
                causal_mask, logit_target_locations = self.prepare_prefill_inputs_slice(
                    input_ids=input_ids_for_prefill,
                    sequence_length=sequence_length,
                )  # original attention mask, original position ids

                forward_kwargs = {
                    "input_ids": input_ids_for_prefill,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": position_ids_for_prefill,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

                # If the model is a GraphModule, we need to switch the model to prefill.
                if isinstance(self.model, GraphModule) and self.model != self.prefill:
                    self.model = self.prefill

                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs:
                            del forward_kwargs[arg]

                outputs = self.model(**forward_kwargs)
                outputs = handle_outputs(outputs)

                next_tokens = self.find_next_tokens(
                    outputs,
                    starting_input_ids,
                    logits_processor,
                    unfinished_sequences,
                    pad_token_id,
                )

                bonus_token = next_tokens
                # update attention_mask_draft
                attention_mask_draft[:, prompt_len] = 1

                # for draft model, update materials, run draft model using newly generated token
                input_ids_for_prefill = torch.cat(
                    (input_ids_for_prefill[:, 1:], next_tokens[:, None]), dim=-1
                )  # B, bucket_size / but add new tokens in the end
                causal_mask, _ = self.prepare_prefill_inputs_slice(
                    input_ids=input_ids_for_prefill,
                    sequence_length=sequence_length + 1,
                )  # original attention mask, original position ids
                position_ids_for_prefill = torch.cat(
                    (position_ids_for_prefill[:, 1:], sequence_length[:, None]), dim=-1
                )
                attention_mask_for_prefill = torch.cat(
                    (
                        attention_mask_for_prefill[:, 1:],
                        torch.ones(batch_size).to(input_ids.device)[:, None],
                    ),
                    dim=-1,
                )

                (new_key_location_draft, new_value_location_draft) = (
                    self.prepare_prefill_input_metadata_draft(attention_mask_for_prefill)
                )
                forward_kwargs_draft = {
                    "input_ids": input_ids_for_prefill,
                    "attention_mask": None,
                    "causal_mask": causal_mask,
                    "position_ids": position_ids_for_prefill,
                    "past_key_values": key_value_blocks_draft,
                    "new_key_location": new_key_location_draft,
                    "new_value_location": new_value_location_draft,
                    "past_valid_key_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

                if (
                    isinstance(self.draft_model, GraphModule)
                    and self.draft_model != self.draft_prefill
                ):
                    self.draft_model = self.draft_prefill

                if isinstance(self.draft_model, GraphModule):
                    for arg in self.draft_model.concrete_args:
                        if arg in forward_kwargs_draft:
                            del forward_kwargs_draft[arg]

                # generate
                outputs_draft = self.draft_model(**forward_kwargs_draft)
                outputs_draft = handle_outputs(outputs_draft)
                next_tokens = self.find_next_tokens(
                    outputs_draft,
                    starting_input_ids,
                    logits_processor,
                    unfinished_sequences,
                    pad_token_id,
                )
                draft_tokens = []
                draft_logits = []
                # there is one bonus, and one draft that comes out of prefill
                draft_logits.append(outputs_draft.squeeze(1))
                draft_tokens.append(next_tokens)  # this is first draft token of draft model
                next_tokens_lst = []
                for i in range(batch_size):
                    # for draft model, this is prompt legnth + 1
                    self.active_key_block_indices_draft[i][: prompt_len + 1] = (
                        self.active_key_block_indices_draft[i][-(prompt_len + 1) :]
                    )
                    self.active_value_block_indices_draft[i][: prompt_len + 1] = (
                        self.active_key_block_indices_draft[i][-(prompt_len + 1) :]
                    )

                    self.active_key_block_indices[i][:prompt_len] = self.active_key_block_indices[
                        i
                    ][-prompt_len:]
                    self.active_value_block_indices[i][:prompt_len] = self.active_key_block_indices[
                        i
                    ][-prompt_len:]

                    self.active_key_block_indices_draft[i][-(prompt_len + 1) :] = [
                        0 for _ in range(prompt_len + 1)
                    ]
                    self.active_value_block_indices_draft[i][-(prompt_len + 1) :] = [
                        0 for _ in range(prompt_len + 1)
                    ]
                    self.active_key_block_indices[i][-prompt_len:] = [0 for _ in range(prompt_len)]
                    self.active_value_block_indices[i][-prompt_len:] = [
                        0 for _ in range(prompt_len)
                    ]
                    first_decode = True
                    next_double = False
                sequence_length_draft = sequence_length_draft + 1  # a single bonus token is added

            else:
                spec_iteration = (
                    self.sp_len - len(draft_tokens) + 1
                    if next_double
                    else self.sp_len - len(draft_tokens)
                )
                # start of speculative decoding
                for draft_iter in range(
                    spec_iteration
                ):  # exception: for the first iteration, sp_len - 1 amount should be iterated
                    # rollback kv cache and update attention mask
                    if num_accepted is not None and draft_iter == 0:
                        # at least single speculative decoding have been performed

                        # update attention mask
                        for i in range(batch_size):
                            attention_mask[i][: sequence_length[i]] = 1

                        for i in range(batch_size):
                            empty_len = [0 for _ in range(bucket_size - sequence_length[i])]
                            self.active_key_block_indices_draft[i][sequence_length[i] :] = empty_len
                            self.active_value_block_indices_draft[i][sequence_length[i] :] = (
                                empty_len
                            )

                            self.active_key_block_indices[i][sequence_length[i] :] = empty_len
                            self.active_value_block_indices[i][sequence_length[i] :] = empty_len

                        sequence_length_draft = sequence_length.clone()  # to actual draft index

                    if next_double and draft_iter < 2:
                        next_tokens = next_tokens_lst[draft_iter]
                        if draft_iter == 0:
                            sequence_length_draft = sequence_length_draft - 1

                    (input_ids_draft, attention_mask_draft, position_ids_draft) = (
                        self.prepare_decode_inputs_v2(
                            next_input_ids=next_tokens,
                            prev_attention_mask=attention_mask_draft,
                            is_first_decode=first_decode,  # FIXME: hacky
                            seq_idx_draft=pad_num + sequence_length_draft,
                            num_accepted=num_accepted,
                        )
                    )

                    num_accepted = None

                    # attention mask size 이상한데.
                    first_decode = False  # FIXME: hacky

                    (
                        new_key_location,
                        new_value_location,
                        valid_key_indices,
                        valid_value_indices,
                    ) = self.prepare_decode_input_metadata_draft()

                    forward_kwargs_draft = {
                        "input_ids": input_ids_draft.view(1, 1),
                        "attention_mask": attention_mask_draft,
                        "causal_mask": None,
                        "position_ids": position_ids_draft,
                        "past_key_values": key_value_blocks_draft,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": valid_key_indices,
                        "past_valid_value_indices": valid_value_indices,
                        "is_prefill": is_prefill,
                        "bucket_size": bucket_size,
                        "use_cache": False,
                    }

                    # If the model is a GraphModule, we need to switch the model to decode.
                    if (
                        isinstance(self.draft_model, GraphModule)
                        and self.draft_model != self.draft_model_decode
                    ):
                        self.draft_model = self.draft_model_decode

                    if isinstance(self.draft_model, GraphModule):
                        for arg in self.draft_model.concrete_args:
                            if arg in forward_kwargs_draft:
                                del forward_kwargs_draft[arg]

                    outputs_draft = self.draft_model(**forward_kwargs_draft)

                    # sequence lengths for debugging

                    # return input_ids
                    # get argmax out of draft logits
                    outputs_draft = handle_outputs(outputs_draft)

                    if next_double and draft_iter == 0:
                        # only kv cache is required
                        pass
                    else:
                        draft_logits.append(outputs_draft.squeeze(1))

                        # done
                        next_tokens = self.find_next_tokens(
                            outputs_draft,
                            starting_input_ids,
                            logits_processor,
                            unfinished_sequences,
                            pad_token_id,
                        )

                        draft_tokens.append(next_tokens)

                    self.move_kv_cache_block_in_place_v2(
                        seq_idx=sequence_length_draft,
                        new_location=new_key_location,
                        existing_block_indices=self.active_key_block_indices_draft,
                    )
                    self.move_kv_cache_block_in_place_v2(
                        seq_idx=sequence_length_draft,
                        new_location=new_value_location,
                        existing_block_indices=self.active_value_block_indices_draft,
                    )

                    sequence_length_draft = sequence_length_draft + 1

                draft_tokens = torch.stack(draft_tokens, dim=-1)  # concat draft tokens # B, sp_len
                draft_tokens_for_verify = torch.cat(
                    (bonus_token[:, None], draft_tokens), dim=-1
                )  # B, sp_len + 1
                draft_logits = torch.stack(draft_logits, dim=1)  # B, sp_len
                next_double = False

                # target run for verification
                (
                    new_key_location,
                    new_value_location,
                    valid_key_indices,
                    valid_value_indices,
                ) = self.prepare_decode_input_metadata(sp_len=self.sp_len + 1)

                # verification step
                # IMPORTANT: bonus_token + draft tokens are used for verification
                batch_size = input_ids.size(0)
                sp_attention_mask = []
                for batch_idx in range(batch_size):
                    batch_attention_mask = attention_mask[batch_idx].clone()  # N
                    batch_sp_attention_mask = []
                    for sp_idx in range(self.sp_len + 1):
                        batch_attention_mask[-(self.sp_len + 1) + sp_idx] = 1
                        batch_sp_attention_mask.append(batch_attention_mask.clone())
                    batch_sp_attention_mask = torch.stack(
                        batch_sp_attention_mask, dim=0
                    )  # sp_len, N
                    sp_attention_mask.append(batch_sp_attention_mask)
                sp_attention_mask = torch.stack(sp_attention_mask, dim=0)  # B, sp_len, N

                sp_position_ids = sp_attention_mask.long().cumsum(-1)[:, :, -1] - 1

                forward_kwargs_verify = {
                    "input_ids": draft_tokens_for_verify,
                    "attention_mask": sp_attention_mask,
                    "causal_mask": None,
                    "position_ids": sp_position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": valid_key_indices,
                    "past_valid_value_indices": valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                    "sp_len": self.sp_len,
                }

                # If the model is a GraphModule, we need to switch the model to decode.
                if isinstance(self.model, GraphModule) and self.model != self.model_decode:
                    self.model = self.model_decode

                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs_verify:
                            del forward_kwargs_verify[arg]
                target_output = handle_outputs(self.model(**forward_kwargs_verify))
                # following logit transformation in huggingface

                for logits_warper in self.logits_warpers:
                    for batch_idx in range(batch_size):
                        for sp_idx in range(self.sp_len + 1):
                            candidate_input_ids = torch.cat(
                                (
                                    input_ids[batch_idx][: sequence_length[batch_idx] - 1],
                                    bonus_token[batch_idx].reshape(1),
                                    draft_tokens[batch_idx][: sp_idx + 1],
                                ),
                                dim=-1,
                            )

                            target_output[batch_idx, sp_idx, :] = logits_warper(
                                candidate_input_ids[None, :],
                                target_output[batch_idx, sp_idx, :][None, :],
                            )

                self.move_kv_cache_block_in_place_verify_v2(
                    seq_idx=sequence_length,
                    sp_len=self.sp_len + 1,
                    new_location=new_key_location,
                    existing_block_indices=self.active_key_block_indices,
                )
                self.move_kv_cache_block_in_place_verify_v2(
                    seq_idx=sequence_length,
                    sp_len=self.sp_len + 1,
                    new_location=new_value_location,
                    existing_block_indices=self.active_value_block_indices,
                )

                q = draft_logits.softmax(dim=-1)  # B, sp_len, V
                batch_indices = torch.arange(batch_size).unsqueeze(-1).expand(-1, self.sp_len)
                seq_indices = torch.arange(self.sp_len).unsqueeze(0).expand(batch_size, -1)
                q_i = q[batch_indices, seq_indices, draft_tokens].squeeze(-1)  # B, sp len

                p = target_output.softmax(dim=-1)  # B, sp_len, V
                bonus_distribution = p[:, -1, :]
                p = p[:, :-1, :]

                p_i = p[batch_indices, seq_indices, draft_tokens].squeeze(-1)  # B, sp len

                probability_ratio = p_i / q_i
                r_i = torch.rand_like(probability_ratio)
                is_accepted = r_i <= probability_ratio
                num_accepted = torch.sum(((~is_accepted).cumsum(dim=-1) < 1), dim=-1)

                # put accepted tokens to
                batch_size = input_ids.size(0)
                bonus_tokens = []

                cur_len = pad_num + sequence_length

                for i in range(batch_size):
                    num_acc = num_accepted[i]
                    input_ids[i][cur_len[i]] = bonus_token[i]
                    input_ids[i][cur_len[i] + 1 : cur_len[i] + 1 + num_acc] = draft_tokens[i][
                        :num_acc
                    ]
                    sequence_length += num_acc + 1

                    if num_acc < self.sp_len:
                        # rejection sampling
                        _p = p[i, num_acc]  # B, V
                        _q = q[i, num_acc]  # B, V
                        p_prime = torch.clamp((_p - _q), min=0)
                        p_prime.div_(p_prime.sum())
                        bonus_token = torch.argmax(p_prime, dim=-1)
                        bonus_tokens.append(bonus_token)

                    else:
                        p_prime = bonus_distribution
                        bonus_token = torch.argmax(p_prime, dim=-1)
                        bonus_tokens.append(bonus_token)

                # here we assert batch size is 1
                if num_acc < self.sp_len:
                    # next double
                    next_tokens = torch.tensor(bonus_tokens).to(input_ids.device)
                    bonus_token = next_tokens
                    next_double = False
                    next_token_for_eos = next_tokens
                else:
                    next_tokens = torch.tensor(bonus_tokens).to(input_ids.device)
                    bonus_token = next_tokens
                    next_tokens_lst = [
                        draft_tokens[:, -1],
                        next_tokens,
                    ]  # second is bonus token, first should go into decode to make kv cache.
                    next_double = True
                    next_token_for_eos = next_tokens[0]

                sequence_length_draft = sequence_length

                # reset draft_tokens and draft_logits
                draft_tokens = []
                draft_logits = []

            if is_prefill:
                next_token_for_eos = next_tokens

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_token_for_eos.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            # max_cur_len = torch.max(cur_len)
            # starting_input_ids = []
            # for batch_idx in range(batch_size):
            #     pad = torch.tensor(
            #         [pad_token_id for _ in range(max_cur_len - cur_len[batch_idx])]
            #     ).to(input_ids.device)
            #     padded_id = torch.cat((pad, input_ids[batch_idx][: cur_len[batch_idx]]))
            #     starting_input_ids.append(padded_id)
            # starting_input_ids = torch.stack(starting_input_ids, dim=0).to(input_ids.dtype)
            # # the final location will be pad - add bonus tokens
            # starting_input_ids[:, -1] = next_tokens

            if stopping_criteria(input_ids[:, :sequence_length], scores).all():
                break

            is_prefill = False

        # reset must be called
        self.reset()
        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=input_ids, scores=scores)
        target_length = min(sequence_length, max_length)
        return input_ids[:, :target_length]

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        # note: new_key_location and new_value_location are same for draft model

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_prefill_input_metadata_draft(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices_draft.pop())

            self.active_key_block_indices_draft.append(block_indices[:])
            self.active_value_block_indices_draft.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices_draft)
        new_value_location = torch.IntTensor(self.active_value_block_indices_draft)

        # note: new_key_location and new_value_location are same for draft model

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self, sp_len=1
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-sp_len])
            valid_value_indices.extend(value_batch[:-sp_len])

            # we use same block idx for key and value here

            key_blocks = []
            value_blocks = []
            for i in range(sp_len):
                new_block_idx = self.available_block_indices.pop()
                key_batch[-sp_len + i] = new_block_idx
                value_batch[-sp_len + i] = new_block_idx

                key_blocks.append(new_block_idx)
                value_blocks.append(new_block_idx)

            new_key_location.append(key_blocks)
            new_value_location.append(value_blocks)

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    # draft model does not require sp_len: it will generate tokens in autoregressive manner.
    def prepare_decode_input_metadata_draft(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices_draft, self.active_value_block_indices_draft
        ):
            valid_key_indices.extend(key_batch[:-1])  # 여기서 가져와야 함 - 에 해당하는 index 들
            valid_value_indices.extend(
                value_batch[:-1]
            )  # 여기서 가져와야 함 - 에 해당하는 index 들

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices_draft.pop()
            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    def prepare_prefill_inputs(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )
        sequence_length = torch.sum(attention_mask, dim=-1)
        max_length = torch.max(sequence_length).item()
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][max_length - N : max_length, max_length - N : max_length] = torch.tril(
                torch.ones((N, N), dtype=torch.bool)
            )

        logit_target_locations = torch.tensor(max_length).reshape(1, -1).repeat(batch_size, 1)
        return causal_mask, logit_target_locations

    # todo: slice 모델에서는 prefill inputs가 달라져야 한다.
    def prepare_prefill_inputs_slice(
        self,
        input_ids: torch.Tensor,
        sequence_length: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        """
        return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
        """  # noqa: E501
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )

        max_length = torch.max(sequence_length).item()
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][bucket_size - N :, bucket_size - N :] = torch.tril(
                torch.ones((N, N), dtype=torch.bool)
            )

        logit_target_locations = torch.tensor(max_length).reshape(1, -1).repeat(batch_size, 1)
        return causal_mask, logit_target_locations

    def prepare_decode_inputs(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        next_attention_mask = prev_attention_mask.clone()

        if is_first_decode:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
            # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            next_attention_mask[:, -1] = 1
        else:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
            next_attention_mask[:, seq_idx - 1] = 1

        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]

        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def prepare_decode_inputs_v2(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx_draft,  # this is now a tensor
        num_accepted,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        batch_size = next_input_ids.size(0)
        next_attention_mask = prev_attention_mask.clone()
        if num_accepted is None:
            if is_first_decode:
                # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
                # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
                next_attention_mask[:, -1] = 1

            else:
                # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
                # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]

                for i in range(batch_size):
                    next_attention_mask[i][seq_idx_draft[i] - 1] = 1

        else:
            # otherwise, we need to consider num_accepted
            # rollback attention_mask
            for i in range(batch_size):
                # rollback
                next_attention_mask[i][: seq_idx_draft[i]] = 1
                next_attention_mask[i][seq_idx_draft[i] :] = 0
                next_attention_mask[i][-1] = 1

        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]
        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        input_ids: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList],
        unfinished_sequences: torch.Tensor,
        pad_token_id: int,
    ) -> torch.Tensor:
        next_tokens_scores: torch.Tensor

        # when using slice model, every output has length 1 in sequence axis
        next_token_logits = logits[:, 0, :]  # for decode seq_len would just be 1

        next_tokens_scores = logits_processor(input_ids, next_token_logits)
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens


class GreedySearchLeftSlice(GenerationStrategy):
    def decode(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        use_unified_kv_indices: bool = False,
        **model_kwargs,
    ):
        kv_dtype = model_kwargs.get("kv_dtype")
        if kv_dtype is None:
            raise ValueError("`kv_dtype` is required for Paged Attention.")

        device_map = self.get_layer_device_map(self.model)

        device = input_ids.device
        batch_size = input_ids.shape[0]
        bucket_size = model_kwargs.get("bucket_size") or max_length

        if bucket_size is None:
            raise ValueError("`bucket_size` is required for Paged Attention.")

        key_value_blocks = model_kwargs.get("key_value_blocks") or self.create_key_value_blocks(
            batch_size, bucket_size, kv_dtype, device, device_map=device_map
        )
        self.initialize_key_value_block_indices(key_value_blocks)
        # ----------- initial_settings -----------------
        starting_input_ids = input_ids
        starting_attention_mask = attention_mask
        batch_size, prompt_len = starting_input_ids.shape
        # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
        # In vllm, generate is async and inner scheduler decides which batch to use based on
        # memory allocation
        assert batch_size <= self.max_batch_size

        starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
        starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

        # ----------- adjust to bucket settings --------
        device = input_ids.device

        flipped_attention_mask = torch.flip(starting_attention_mask, dims=[1])
        flipped_input_ids = torch.flip(starting_input_ids, dims=[1])
        flipped_position_ids = torch.flip(starting_position_ids, dims=[1])

        attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int).to(device)
        left_slice_attention_mask = attention_mask.clone()
        attention_mask[:, :prompt_len] = starting_attention_mask
        left_slice_attention_mask[:, :prompt_len] = flipped_attention_mask

        input_ids = torch.full(
            (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
        ).to(device)
        left_slice_input_ids = input_ids.clone()
        input_ids[:, :prompt_len] = starting_input_ids
        left_slice_input_ids[:, :prompt_len] = flipped_input_ids

        position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long).to(device)
        left_slice_position_ids = position_ids.clone()
        position_ids[:, :prompt_len] = starting_position_ids
        left_slice_position_ids[:, :prompt_len] = flipped_position_ids

        sequence_idx = prompt_len - 1
        is_prefill = True

        scores = None

        batch_size = input_ids.shape[0]
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = torch.tensor(eos_token_id).to(input_ids.device)
        next_tokens = None

        # start generating new tokens
        for i in range(max_length - prompt_len):
            if is_prefill:
                (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                    left_slice_attention_mask
                )

                forward_kwargs = {
                    "input_ids": left_slice_input_ids,
                    "attention_mask": None,
                    "causal_mask": left_slice_attention_mask.bool(),  # 2d mask
                    "position_ids": left_slice_position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": None,
                    "past_valid_value_indices": None,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

            else:
                (input_ids, left_slice_attention_mask, position_ids) = self.prepare_decode_inputs(
                    next_input_ids=next_tokens,
                    prev_attention_mask=left_slice_attention_mask,
                    is_first_decode=(True if i == 1 else False),  # FIXME: hacky
                    seq_idx=sequence_idx,
                )

                (
                    new_key_location,
                    new_value_location,
                    past_valid_key_indices,
                    past_valid_value_indices,
                ) = self.prepare_decode_input_metadata()
                forward_kwargs = {
                    "input_ids": input_ids,
                    "attention_mask": left_slice_attention_mask.bool(),
                    "causal_mask": None,
                    "position_ids": position_ids,
                    "past_key_values": key_value_blocks,
                    "new_key_location": new_key_location,
                    "new_value_location": new_value_location,
                    "past_valid_key_indices": past_valid_key_indices,
                    "past_valid_value_indices": past_valid_value_indices,
                    "is_prefill": is_prefill,
                    "bucket_size": bucket_size,
                    "use_cache": False,
                }

            # For llama3 merged_idx models, unify kv indices.
            if use_unified_kv_indices:
                past_valid_kv_indices = forward_kwargs["past_valid_key_indices"]
                new_kv_location = forward_kwargs["new_key_location"]
                del forward_kwargs["past_valid_key_indices"]
                del forward_kwargs["past_valid_value_indices"]
                del forward_kwargs["new_key_location"]
                del forward_kwargs["new_value_location"]
                forward_kwargs["past_valid_kv_indices"] = past_valid_kv_indices
                forward_kwargs["new_kv_location"] = new_kv_location

            outputs = self.model(**forward_kwargs)

            if not is_prefill:
                # now copy the new_key location back to original place for decode_phase
                # based on its actual sequence length
                batch_size = left_slice_attention_mask.shape[0]

                for batch_idx in range(batch_size):
                    sequence_length = torch.sum(left_slice_attention_mask[batch_idx]).item()
                    actual_seq_idx = sequence_length - 1  # -1 because we index from 0

                    self.move_kv_cache_block_in_place(
                        seq_idx=actual_seq_idx,
                        new_location=new_key_location[batch_idx : batch_idx + 1],
                        existing_block_indices=[self.active_key_block_indices[batch_idx]],
                    )
                    self.move_kv_cache_block_in_place(
                        seq_idx=actual_seq_idx,
                        new_location=new_value_location[batch_idx : batch_idx + 1],
                        existing_block_indices=[self.active_value_block_indices[batch_idx]],
                    )
            # done
            outputs = handle_outputs(outputs)

            # done
            next_tokens = self.find_next_tokens(
                outputs,
                starting_input_ids,
                logits_processor,
                unfinished_sequences,
                pad_token_id,
                is_prefill,
            )

            starting_input_ids = torch.cat([starting_input_ids, next_tokens[:, None]], dim=-1)

            if eos_token_id is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            if stopping_criteria(starting_input_ids, scores).all():
                break

            sequence_idx += 1

            # prepare for next phase
            is_prefill = False

        # reset must be called
        self.reset()
        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=starting_input_ids, scores=scores)
        return starting_input_ids

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-1])
            valid_value_indices.extend(value_batch[:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    def prepare_prefill_inputs(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
        batch_size, bucket_size = input_ids.shape
        device = input_ids.device
        causal_mask = torch.zeros((batch_size, bucket_size, bucket_size), dtype=torch.bool).to(
            device
        )
        sequence_length = torch.sum(attention_mask, dim=-1)
        for i in range(batch_size):
            N = sequence_length[i].item()
            causal_mask[i][:N, :N] = torch.triu(torch.ones((N, N), dtype=torch.bool))

        return causal_mask

    def prepare_decode_inputs(
        self,
        next_input_ids: torch.Tensor,
        prev_attention_mask: torch.Tensor,
        is_first_decode: bool,
        seq_idx: int,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (input_ids, attention_mask, position_ids)
        """
        next_attention_mask = prev_attention_mask.clone()

        if is_first_decode:
            # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
            # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            next_attention_mask[:, -1] = 1
        else:
            for batch_idx in range(next_attention_mask.shape[0]):
                mask = next_attention_mask[batch_idx]
                # Find the first 0 position (first padding position after the sequence)
                zero_positions = (mask == 0).nonzero(as_tuple=True)[0]
                if len(zero_positions) > 0:
                    # Convert the first 0 to 1 to mark the new token position
                    first_zero_pos = zero_positions[0].item()
                    next_attention_mask[batch_idx, first_zero_pos] = 1

        # Calculate position_ids based on the updated attention mask
        next_position_ids = next_attention_mask.long().cumsum(-1) - 1
        next_position_ids = next_position_ids[:, -1:]

        return (next_input_ids[:, None], next_attention_mask, next_position_ids)

    def find_next_tokens(
        self,
        logits: torch.Tensor,
        input_ids: torch.Tensor,
        logits_processor: Optional[LogitsProcessorList],
        unfinished_sequences: torch.Tensor,
        pad_token_id: int,
        is_prefill: bool,
    ) -> torch.Tensor:
        next_tokens_scores: torch.Tensor
        if is_prefill:
            # left slice generator gets prefill logit from front.
            next_token_logits = logits[:, 0, :]
        else:
            next_token_logits = logits[:, 0, :]  # for decode seq_len would just be 1

        next_tokens_scores = logits_processor(input_ids, next_token_logits)
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens
