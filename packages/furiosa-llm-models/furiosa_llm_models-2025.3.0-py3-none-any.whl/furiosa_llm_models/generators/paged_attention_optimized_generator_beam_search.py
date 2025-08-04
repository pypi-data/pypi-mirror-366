import copy
from typing import List, Optional, Tuple, Union

import torch
from torch.fx import GraphModule
from transformers.generation import (
    BeamScorer,
    BeamSearchScorer,
    MinNewTokensLengthLogitsProcessor,
)

from furiosa_llm_models.generators.paged_attention_optimized_generator import (
    USE_CACHE,
    PagedAttentionGenerator,
    handle_outputs,
    move_kv_cache_block_in_place,
    prepare_decode_inputs,
    prepare_prefill_inputs,
)


class PagedAttentionGeneratorBeamSearch(PagedAttentionGenerator):
    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor, batch_size: int
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        # beams belonging to same prompts should share blocks

        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for count in range(batch_size):
            idx = count * self.num_beams
            single_attention_mask = attention_mask[idx]
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            # at this point block has been created
            for _ in range(self.num_beams):
                self.active_key_block_indices.append(copy.deepcopy(block_indices))
                self.active_value_block_indices.append(copy.deepcopy(block_indices))

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    # this will handle a single sequence without scheduling
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        max_length: int,
        min_new_tokens: Optional[int] = None,
        **kwargs,
    ) -> Union[List[str], torch.Tensor]:
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """
        # FIXME: This is a hacky way to handle the device.
        # This should be handled in a better way.
        with torch.device(input_ids.device):
            # ----------- initial_settings -----------------
            starting_input_ids = input_ids
            starting_attention_mask = attention_mask
            batch_size, prompt_len = starting_input_ids.shape

            # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
            # In vllm, generate is async and inner scheduler decides which batch to use based on
            # memory allocation
            assert batch_size <= self.max_batch

            starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
            starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

            # ----------- adjust to bucket settings --------
            pad_token_id = self.model.config.eos_token_id

            attention_mask = torch.zeros((batch_size, self.bucket_size), dtype=torch.int)
            attention_mask[:, :prompt_len] = starting_attention_mask

            input_ids = torch.full(
                (batch_size, self.bucket_size), fill_value=pad_token_id, dtype=torch.int
            )
            input_ids[:, :prompt_len] = starting_input_ids

            position_ids = torch.zeros((batch_size, self.bucket_size), dtype=torch.long)
            position_ids[:, :prompt_len] = starting_position_ids

            is_prefill = True

            batch_size = input_ids.shape[0]
            eos_token_id = self.model.config.eos_token_id
            next_tokens = None

            self.logit_processor = MinNewTokensLengthLogitsProcessor(
                prompt_length_to_skip=starting_input_ids.shape[-1],
                min_new_tokens=min_new_tokens,
                eos_token_id=eos_token_id,
                device=input_ids.device,
            )

            # beam search stuff
            beam_scorer: BeamScorer = BeamSearchScorer(
                batch_size=input_ids.shape[0],
                num_beams=self.num_beams,
                device=input_ids.device,
                length_penalty=1.0,  # TODO: Generalize. Fix it as 1.0 for now.
                do_early_stopping=True,  # This should be always True.
                num_beam_hyps_to_keep=1,  # TODO: Generalize. Fix it as 1 for now.
                max_length=max_length,
            )

            input_ids = input_ids.repeat_interleave(
                self.num_beams, 0
            )  # [batch_size * num_beams, sequence_length]
            starting_input_ids = starting_input_ids.repeat_interleave(self.num_beams, 0)
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L727
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L718-L722
            attention_mask = attention_mask.repeat_interleave(
                self.num_beams, 0
            )  # [batch_size * num_beams, sequence_length]

            # beam search config
            batch_size = len(beam_scorer._beam_hyps)
            num_beams = beam_scorer.num_beams

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2889
            batch_beam_size, _ = input_ids.shape
            # TODO(this is because we use bucketization)
            cur_len = prompt_len
            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2891-L2894
            if num_beams * batch_size != batch_beam_size:
                raise ValueError(
                    f"Batch dimension of `input_ids` should be {num_beams * batch_size}, "
                    f"but is {batch_beam_size}."
                )

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2896-L2900
            # Assuming return_dict_in_generate and output_scores are not used in this function.
            # scores = None # not used
            beam_indices = None

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2912-L2916
            beam_scores = torch.zeros(
                (batch_size, num_beams), dtype=torch.float, device=input_ids.device
            )
            beam_scores[:, 1:] = -1e9
            beam_scores = beam_scores.view((batch_size * num_beams,))
            is_first_decode = False
            next_tokens = None
            # start generating new tokens

            # FIXME: This is a temporary solution to handle out-of-bound positional embedding access. # noqa
            # This issue occurs when the maximum length of the generated sequence exceeds the
            # maximum number of embeddings in the model.
            if max_length > self.config.max_position_embeddings:
                max_length = self.config.max_position_embeddings

            count = 0
            while True:
                if is_prefill:
                    (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                        attention_mask, batch_size
                    )
                    (
                        packed_input_ids,
                        _packed_attention_mask,  # this attention mask if for debugging purpose
                        causal_mask,
                        packed_position_ids,
                        logit_target_locations,
                        new_key_location,
                        new_value_location,
                    ) = prepare_prefill_inputs(
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
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": None,
                        "past_valid_value_indices": None,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                    }

                    is_first_decode = True

                    # If the model is a GraphModule, we need to switch the model to prefill.
                    if isinstance(self.model, GraphModule) and self.model != self.prefill:
                        self.model = self.prefill
                else:
                    (next_tokens, attention_mask, position_ids) = prepare_decode_inputs(
                        next_input_ids=next_tokens,
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
                        "input_ids": next_tokens,
                        "attention_mask": attention_mask,
                        "causal_mask": None,
                        "position_ids": position_ids,
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": valid_key_indices,
                        "past_valid_value_indices": valid_value_indices,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                    }

                    is_first_decode = False

                    # If the model is a GraphModule, we need to switch the model to decode.
                    if isinstance(self.model, GraphModule) and self.model != self.decode:
                        self.model = self.decode

                # remove all concrete args from forward_kwargs for they will not be used in the
                # forward pass.
                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs:
                            del forward_kwargs[arg]

                outputs = self.model(**forward_kwargs)

                if not is_prefill:
                    # now copy the new_key location back to original place for decode_phase
                    move_kv_cache_block_in_place(
                        seq_idx=cur_len - 1,
                        new_location=new_key_location,
                        existing_block_indices=self.active_key_block_indices,
                    )
                    move_kv_cache_block_in_place(
                        seq_idx=cur_len - 1,
                        new_location=new_value_location,
                        existing_block_indices=self.active_value_block_indices,
                    )

                # done
                logits = handle_outputs(outputs)

                # logits has shape 4,8
                # because attention has been packe

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2943
                # this is for attention depacking
                # next_token_logits = logits[:, -1, :]
                if is_prefill or not self.model.has_scores_for_decode_output:
                    next_token_logits = find_next_tokens(logits, logit_target_locations, is_prefill)

                    # TODO: Check if self.adjust_logits_during_generation is necessary in this
                    # context
                    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2944-L2946
                    # The following code adjusts the logits during generation. However, it seems to
                    # have no effect on GPT-J and LLaMMA models, as they do not have this function
                    # as an instance method. Additionally, the `adjust_logits_during_generation`
                    # function in `transformers.generation.utils.GenerationMixin` does not modify
                    # the logits, as can be seen in the following code:
                    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L564-L568
                    ####################>>>>>>>>>>>>>>>>>>>>
                    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2947-L2949
                    next_token_scores = torch.nn.functional.log_softmax(
                        next_token_logits, dim=-1
                    )  # [batch_size * num_beams, vocab_size]
                else:
                    # For decode, we will use the logits as scores as model outputs
                    # torch.nn.functional.log_softmax(lm_logits[:, -1], dim=-1)
                    next_token_scores = logits

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2951-L2952
                next_token_scores_processed = self.logit_processor(input_ids, next_token_scores)

                next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                    next_token_scores
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2972-L2974
                vocab_size = next_token_scores.shape[-1]
                next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2976-L2979
                next_token_scores, next_tokens = torch.topk(
                    next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2981-L2982
                next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
                next_tokens = next_tokens % vocab_size

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2984-L2993
                beam_outputs = beam_scorer.process(
                    input_ids,
                    next_token_scores,
                    next_tokens,
                    next_indices,
                    pad_token_id=pad_token_id,
                    eos_token_id=eos_token_id,
                    beam_indices=beam_indices,
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2995-L2997
                beam_scores = beam_outputs["next_beam_scores"]
                beam_next_tokens = beam_outputs["next_beam_tokens"]
                beam_idx = beam_outputs["next_beam_indices"]

                # TODO(DONGHUN) based on this idx adjust the block index
                # we know new beams are chosen at this point

                new_key_block_indices = adjust_kv_cache_block(
                    beam_idx, self.active_key_block_indices
                )
                self.active_key_block_indices = new_key_block_indices
                new_value_block_indices = adjust_kv_cache_block(
                    beam_idx, self.active_value_block_indices
                )
                self.active_value_block_indices = new_value_block_indices

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2999
                starting_input_ids = torch.cat(
                    [starting_input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3010-L3011
                cur_len = cur_len + 1

                # TODO: remove count which is only for debuggin
                count += 1

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3013-L3015
                # cur_len >= max_length is a short version of the stopping criteria in
                # https://github.com/huggingface/transformers/blob/main/src/transformers/generation/stopping_criteria.py#L75-L83
                # TODO: Implement get stopping criteria logic
                # TODO: Implement other stopping criteria logic
                if beam_scorer.is_done or cur_len >= max_length:
                    break

                # v2.Generator specific variables
                is_prefill = False
                next_tokens = beam_next_tokens

            sequence_outputs = beam_scorer.finalize(
                starting_input_ids,
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
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3055-L3056
            outputs = (
                [
                    [self.tokenizer.decode(output, skip_special_tokens=True)]
                    for output in sequence_outputs["sequences"]
                ]
                if not self.return_tensors
                else sequence_outputs["sequences"]
            )
            return outputs


def adjust_kv_cache_block(beam_idx: torch.Tensor, existing_block_indices: List[List[int]]):
    new_block_indices = []
    for idx in beam_idx:
        existing_block_index = existing_block_indices[idx]
        new_block_indices.append(copy.deepcopy(existing_block_index))

    return new_block_indices


def find_next_tokens(
    logits: torch.Tensor,
    logit_target_locations: Optional[List[List[int]]],
    is_prefill: bool,
):
    next_tokens_scores: torch.Tensor
    if is_prefill:
        # outputs should be logits which would have shape of [batch, seq_len, embedding_dimension]
        # loop through each batch and find the logit location due to attention_packing
        next_tokens_scores = []
        for single_batch_logit, single_batch_logit_target_location in zip(
            logits, logit_target_locations
        ):
            assert single_batch_logit.dim() == 2
            # print("single batch logit shape: ", single_batch_logit.shape)
            for logit_target in single_batch_logit_target_location:
                # logit target will just be index

                # hard coding for prefill last block slice
                # for not, packing is not supported
                if single_batch_logit.shape[0] == 1:
                    logit_target = 0
                next_tokens_scores.append(
                    single_batch_logit[logit_target]
                )  # will be [embedding_dimension]

        # stack this back to [batch, vocab_size]
        next_tokens_scores = torch.stack(next_tokens_scores)

    else:
        next_tokens_scores = logits[:, 0, :]  # for decode seq_len would just be 1

    return next_tokens_scores
