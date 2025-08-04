import logging
from typing import Dict, List, Tuple

import torch

from furiosa_llm_models.generators.v2.generator import (
    OUTPUT_ATTENTIONS,
    OUTPUT_HIDDEN_STATES,
    RETURN_DICT,
    SUPPORTED_GENERATION_RETURN_DICT_TYPES,
)

from ..gptj.paged_attention_utils import InputMetadata
from .generator import BaseGenerator

# FIXME: Rename this. Since PagedAttentionGenerator "uses" caches,
# yet it does not yield 'past_key_values' as its output.
USE_CACHE = False


def map_cache(kv_cache, f):
    return tuple(tuple(f(t) for t in kv) for kv in kv_cache)


def get_generation_output_kwargs(
    output_attentions: bool,
    output_hidden_states: bool,
    return_dict: bool,
    use_cache: bool,
) -> Dict:
    if output_attentions:
        raise ValueError(
            f"model.forward with output_attentions={output_attentions} is not supported."
        )
    if output_hidden_states:
        raise ValueError(
            f"model.forward with output_hidden_states={output_hidden_states} is not supported."
        )
    if use_cache:
        raise ValueError(f"model.forward with use_cache={use_cache} is not supported.")

    return {
        "output_attentions": output_attentions,
        "output_hidden_states": output_hidden_states,
        "return_dict": return_dict,
        "use_cache": use_cache,
    }


# a generator + runtime mix of some sort just for poc
class PagedAttentionGenerator(BaseGenerator):
    output_attentions = OUTPUT_ATTENTIONS
    output_hidden_states = OUTPUT_HIDDEN_STATES
    return_dict = RETURN_DICT
    use_cache = USE_CACHE

    def __init__(
        self,
        model,
        total_block_space: Tuple[Tuple[torch.Tensor]],  # num layer, key, value
        bucket_size: int,
    ) -> None:
        self.model = model
        self.input_metadata = None
        # initialize past key values here
        assert len(total_block_space) == self.model.config.n_layer, "KV cache initialization failed"

        # all layers are treated equal here thus indices only need to represent one
        self.past_key_values = total_block_space
        block_indices, block_size, head, head_size = total_block_space[0][0].shape

        assert bucket_size % block_size == 0

        self.block_size = block_size

        self.last_key_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd
        self.last_value_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd

        # exist for each sequence
        # key is batch_idx, value is block indices
        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []

        # keep track of last real block id for each batch
        # ((key_block, key_token), (value_block, value_token))
        self.valid_block_meta: List[Tuple[Tuple[int, int]]] = []

        self.available_block_indices = list(range(1, block_indices))
        self.zero_block_index = 0  # this is a special zero block
        self.total_block_count = block_indices
        self.bucket_size = bucket_size
        self.num_max_block = int(bucket_size / block_size)

    def generate(
        self,
        padded_sequences,
        max_length: int,
        # NOTE: This is a temporary argument to determine whether to run
        # paged_attention_concat model or not.
        # If optimize is True, the model will run paged_attention_concat model.
        # Else, the model will run plain paged_attention model.
        # Once the paged_attention_concat model is fully implemented, this argument will be removed.
        optimize: bool = False,
    ):
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """
        # for example
        # 1. for prefill
        # if block size = 3 and input is
        # [[x x a b]
        #  [a b c d]
        #  [x x x a]]
        # then, attention mask should be
        # [[0 0 1 1 0 0]
        #  [1 1 1 1 0 0]
        #  [0 0 0 1 0 0]]

        # and causal mask should be
        # 1. for prefill,
        # [[1 0 0 0 0 0]
        #  [1 1 0 0 0 0]
        #  [1 1 1 0 0 0]
        #  [1 1 1 1 0 0]
        #  [1 1 1 1 1 0]
        #  [1 1 1 1 1 1]]
        # and logit should be selected at position 4, not 6(since 5,6 are padding)

        # 1. for decode
        # if block size = 3 and past sequence is
        # [[x x a b]
        #  [a b c d]
        #  [x x x a]]
        # and input is
        # [[c],
        #  [e],
        #  [b]]
        # then, attention mask should be
        # [[0 0 1 1 1 0]
        #  [1 1 1 1 1 0]
        #  [0 0 0 1 1 0]]

        # and causal mask should be
        # 1. for prefill,
        # [[1 1 1 1 1 0]
        # and logit should be selected at position 5, not 6(since 6 is just padding)

        starting_input_ids = padded_sequences.input_ids
        final_input_ids = starting_input_ids
        starting_attention_mask = padded_sequences.attention_mask
        batch_size, starting_input_len = starting_input_ids.shape
        bucketized_attention_mask = torch.zeros((batch_size, self.bucket_size), dtype=torch.int)
        bucketized_attention_mask[:, :starting_input_len] = starting_attention_mask

        starting_position_id = []
        for single_attention_mask in starting_attention_mask.tolist():
            # find the first 1, then every before that is 1
            # and new indexing from 0 begins there
            # position ids is very similar to attention mask
            # if bucket size = 8
            # [[x x a b]
            #  [a b c d]
            #  [x x x a]]
            # then, position id would be d
            # [[1 1 0 1 2 3]
            #  [0 1 2 3 4 5]
            #  [1 1 1 0 1 2]]
            target_idx = 0
            for idx, value in enumerate(single_attention_mask):
                if value == 1:
                    target_idx = idx
                    break

            single_attention_mask[:target_idx] = [1] * target_idx
            single_attention_mask[target_idx:] = list(
                range(len(single_attention_mask) - target_idx)
            )
            single_position_id = torch.cat(
                [
                    torch.LongTensor(single_attention_mask).reshape(1, -1),
                    torch.zeros((1, self.bucket_size - starting_input_len), dtype=torch.long),
                ],
                dim=1,
            )
            starting_position_id.append(single_position_id)

        starting_position_ids = torch.cat(starting_position_id, dim=0)

        bucketized_input_ids = torch.zeros((batch_size, self.bucket_size), dtype=torch.int)
        bucketized_input_ids[:, :starting_input_len] = starting_input_ids
        # start generating new token
        current_logit_idx = starting_input_len - 1
        input_ids = None
        position_ids = None
        for i in range(max_length - starting_input_len):
            logging.info(">>>>>>>>>>> Generating %dth token <<<<<<<<<<<<", i)
            # update attention mask for this phase
            if i == 0:
                # prefill
                model_kwargs = {}
                model_kwargs["attention_mask"] = bucketized_attention_mask
                input_ids = bucketized_input_ids
                position_ids = starting_position_ids
            else:
                index = starting_input_len - 1 + i
                model_kwargs["attention_mask"][:, index] = 1
                # find the last row of positions ids
                if i == 1:
                    last_column = position_ids[:, starting_input_len - 1]
                    position_ids = (last_column + 1).reshape(batch_size, -1)
                else:
                    position_ids = position_ids + 1

            # this will set the input metadata for this phase
            self.update_input_metadata(model_kwargs["attention_mask"].tolist())

            # update model_inputs here
            model_inputs = self.model.prepare_inputs_for_generation(
                input_ids, self.input_metadata, **model_kwargs
            )
            model_inputs.update(
                get_generation_output_kwargs(
                    self.output_attentions,
                    self.output_hidden_states,
                    self.return_dict,
                    self.use_cache,
                )
            )

            input_metadata = {
                "new_key_location": self.input_metadata.new_key_location,
                "new_value_location": self.input_metadata.new_value_location,
                "is_prefill": self.input_metadata.is_prefill,
            }
            # Without this control flow, the number of compiled graphs will exceed 2.
            if not optimize:
                input_metadata.update(
                    {
                        "valid_key_indices": self.input_metadata.valid_key_indices,
                        "valid_value_indices": self.input_metadata.valid_value_indices,
                        "bucket_size": self.bucket_size,
                    }
                )
            else:
                input_metadata.update(
                    {
                        "past_valid_key_indices": self.input_metadata.past_valid_key_indices,
                        "past_valid_value_indices": self.input_metadata.past_valid_value_indices,
                        "num_generated_tokens": self.input_metadata.num_generated_tokens,
                    }
                )

            outputs = self.model(
                input_metadata=self.input_metadata,
                past_key_values=self.past_key_values,
                **model_inputs,
                position_ids=position_ids,  # LongTensor
                **input_metadata,
            )
            outputs = self.handle_outputs(outputs)

            next_token_logits = outputs[:, current_logit_idx, :]
            next_token_scores = next_token_logits.reshape(batch_size, next_token_logits.size(-1))
            next_tokens = torch.argmax(next_token_scores, dim=-1)

            logging.info("Next tokens is: {}".format(next_tokens))

            # prepare for next phase
            current_logit_idx = 0  # for decode phase logit only has one value
            input_ids = next_tokens.reshape(batch_size, -1)
            final_input_ids = torch.cat([final_input_ids, input_ids], dim=-1)

        return final_input_ids

    def update_input_metadata(self, updated_attention_mask: List[List[int]]):
        # 1. for prefill
        # if block size = 3 and input is
        # [[x x a b]
        #  [a b c d]
        #  [x x x a]]
        # then, block should be should be
        # [[0 0 1 1 0 0]  = [b1, b2]
        #  [1 1 1 1 0 0]  = [b3, b4]
        #  [0 0 0 1 0 0]] = [b5, b6]

        # or this could be possible
        # [[0 0 1 1 0 0 0 0 0]]
        # where last n blocks are for bucket

        # 어디까지 저장이 되어있는가?
        # for prefill -> consider everything
        # for decode -> look at the latest block and figure out if new allocation is needed
        if self.input_metadata is None:
            logging.debug("prefill phase")
            assert len(self.active_key_block_indices) == 0
            assert len(self.active_value_block_indices) == 0

            new_key_locations = []
            new_value_locations = []

            # since it's both padding
            # 일단 앞에서부터 하나씩 block 들을 만들고 block indices 를 부여하고
            # 진짜인지 아닌지를 판단하기, 앞에서부터 하나씩 끊어서 block 을 만들면 됨
            for batch_idx, single_attention_mask in enumerate(updated_attention_mask):
                new_key_location = []
                new_value_location = []
                split_blocks = [
                    single_attention_mask[i : i + self.block_size]
                    for i in range(0, len(single_attention_mask), self.block_size)
                ]
                self.last_key_block_indices.append([])
                self.last_value_block_indices.append([])

                self.active_key_block_indices.append([])
                self.active_value_block_indices.append([])

                last_valid_key_block_idx = None
                last_valid_value_block_idx = None
                last_valid_token_idx = None

                for block in split_blocks:
                    # x x 1 => then block is full
                    # 1 x x => block is not full
                    if sum(block) == 0:
                        # then this is zero block

                        new_key_location.append(torch.IntTensor([0]))
                        new_value_location.append(torch.IntTensor([0]))

                        self.last_key_block_indices[batch_idx].append(0)
                        self.last_value_block_indices[batch_idx].append(0)
                        self.active_key_block_indices[batch_idx].append(0)
                        self.active_value_block_indices[batch_idx].append(0)
                    else:
                        # find the idx of last 1
                        last_idx = 0
                        for idx, val in enumerate(block):
                            if val == 1:
                                last_idx = idx

                        new_key_block_idx = self.available_block_indices.pop()
                        new_value_block_idx = self.available_block_indices.pop()

                        new_key_location.append(torch.IntTensor([new_key_block_idx]))
                        new_value_location.append(torch.IntTensor([new_value_block_idx]))

                        self.last_key_block_indices[batch_idx].append(0)
                        self.last_value_block_indices[batch_idx].append(0)

                        self.active_key_block_indices[batch_idx].append(new_key_block_idx)
                        self.active_value_block_indices[batch_idx].append(new_value_block_idx)

                        last_valid_key_block_idx = new_key_block_idx
                        last_valid_value_block_idx = new_value_block_idx
                        last_valid_token_idx = last_idx

                self.valid_block_meta.append(
                    (
                        (last_valid_key_block_idx, last_valid_token_idx),
                        (last_valid_value_block_idx, last_valid_token_idx),
                    )
                )

                new_key_locations.append(torch.unsqueeze(torch.cat(new_key_location), 0))
                new_value_locations.append(torch.unsqueeze(torch.cat(new_value_location), 0))

            new_key_locations = torch.cat(new_key_locations)
            new_value_locations = torch.cat(new_value_locations)

            self.input_metadata = InputMetadata(
                past_key_cache_idx=self.last_key_block_indices,
                past_value_cache_idx=self.last_value_block_indices,
                key_cache_idx=self.active_key_block_indices,
                value_cache_idx=self.active_value_block_indices,
                new_key_location=new_key_locations,
                new_value_location=new_value_locations,
                block_max_seq_len=self.num_max_block,
                block_size=self.block_size,
                is_prefill=True,
            )

        else:
            logging.debug("decode phase")

            # for each batch, find the right most block excluding the zero blocks
            # if that block is full, assign a new block and replace zero block that should be in
            # that place if that block is NOT full, find the location

            decode_key_new_block_location = []
            decode_value_new_block_location = []
            for batch_idx, single_attention_mask in enumerate(updated_attention_mask):
                (
                    (last_valid_key_block_idx, last_token_idx),
                    (last_valid_value_block_idx, last_token_idx),
                ) = self.valid_block_meta[batch_idx]

                if last_token_idx == self.block_size - 1:
                    # this block is full, so replace
                    new_key_block_idx = self.available_block_indices.pop()
                    last_zero_block_idx = len(self.active_key_block_indices[batch_idx])
                    for i, val in enumerate(self.active_key_block_indices[batch_idx]):
                        if val == last_valid_key_block_idx:
                            # this i+1 will be the next zero block
                            last_zero_block_idx = i + 1
                            break

                    self.last_key_block_indices[batch_idx] = self.active_key_block_indices[
                        batch_idx
                    ][:last_zero_block_idx]
                    self.active_key_block_indices[batch_idx][last_zero_block_idx] = (
                        new_key_block_idx
                    )

                    new_value_block_idx = self.available_block_indices.pop()
                    last_zero_block_idx = len(self.active_value_block_indices[batch_idx])
                    for i, val in enumerate(self.active_value_block_indices[batch_idx]):
                        if val == last_valid_value_block_idx:
                            # this i+1 will be the next zero block
                            last_zero_block_idx = i + 1
                            break

                    self.last_value_block_indices[batch_idx] = self.active_value_block_indices[
                        batch_idx
                    ][:last_zero_block_idx]
                    self.active_value_block_indices[batch_idx][last_zero_block_idx] = (
                        new_value_block_idx
                    )

                    self.valid_block_meta[batch_idx] = (
                        (new_key_block_idx, 0),
                        (new_value_block_idx, 0),
                    )

                else:
                    self.valid_block_meta[batch_idx] = (
                        (
                            last_valid_key_block_idx,
                            last_token_idx + 1,
                        ),
                        (
                            last_valid_value_block_idx,
                            last_token_idx + 1,
                        ),
                    )

                a, b = self.valid_block_meta[batch_idx][0]
                c, d = self.valid_block_meta[batch_idx][1]

                decode_key_new_block_location.append(torch.unsqueeze(torch.IntTensor([a]), 0))
                decode_value_new_block_location.append(torch.unsqueeze(torch.IntTensor([c]), 0))

            decode_key_new_block_location = torch.cat(decode_key_new_block_location)
            decode_value_new_block_location = torch.cat(decode_value_new_block_location)

            self.input_metadata = InputMetadata(
                past_key_cache_idx=self.last_key_block_indices,
                past_value_cache_idx=self.last_value_block_indices,
                key_cache_idx=self.active_key_block_indices,
                value_cache_idx=self.active_value_block_indices,
                block_max_seq_len=self.num_max_block,
                block_size=self.block_size,
                is_prefill=False,
                new_key_location=decode_key_new_block_location,
                new_value_location=decode_value_new_block_location,
            )

    def handle_outputs(self, outputs):
        # SUPPORTED_GENERATION_RETURN_DICT_TYPES[1],
        # i.e., CausalLMOutputWithCrossAttentions is not yet checked.
        if isinstance(outputs, SUPPORTED_GENERATION_RETURN_DICT_TYPES[0]):
            return outputs.to_tuple()[0]
        elif isinstance(outputs, tuple):
            return outputs[0]
        else:
            ValueError(f"Unsupported generation output type: {type(outputs)}")
