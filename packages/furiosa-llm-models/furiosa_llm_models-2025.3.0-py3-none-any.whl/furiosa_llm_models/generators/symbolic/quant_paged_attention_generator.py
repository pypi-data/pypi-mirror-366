import copy
import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import torch
from transformers import (
    BeamScorer,
    BeamSearchScorer,
    GenerationConfig,
    GenerationMixin,
    LogitsProcessorList,
    MaxLengthCriteria,
    MaxTimeCriteria,
    StoppingCriteriaList,
)

from ...gptj.symbolic.paged_attention_utils import InputMetadata
from ..generator import BaseGenerator


class QuantPagedAttentionGenerator(BaseGenerator, GenerationMixin):
    def __init__(
        self,
        model,
        model_type,
        total_block_space: Tuple[Tuple[torch.Tensor]],  # num layer, key, value
        bucket_size: int,
    ) -> None:
        self.model = model
        self.model_type = model_type
        self.input_metadata = None
        # initialize past key values here
        assert len(total_block_space) == self.model.config.n_layer, "KV cache initialization failed"

        # all layers are treated equal here thus indices only need to represent one
        self.past_key_values = total_block_space
        block_indices, block_size, head, head_size = total_block_space[0][0].shape

        assert bucket_size % block_size == 0

        self.block_size = block_size
        # exist for each sequence
        self.active_key_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd
        self.active_value_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd

        # keep track of last real block id for each batch
        # ((key_block, key_token), (value_block, value_token))
        self.valid_block_meta: List[Tuple[Tuple[int, int]]] = []

        self.available_block_indices = list(range(1, block_indices))
        self.zero_block_index = 0  # this is a special zero block
        self.total_block_count = block_indices
        self.bucket_size = bucket_size
        self.num_max_block = int(bucket_size / block_size)

    def _validate_model_kwargs(self, model_kwargs: Dict[str, Any]):
        """Validates model kwargs for generation. Generate argument typos will also be caught here."""  # noqa: E501
        # Excludes arguments that are handled before calling any model function
        if self.model.config.is_encoder_decoder:
            for key in ["decoder_input_ids"]:
                model_kwargs.pop(key, None)

        unused_model_args = []
        model_args = set(
            inspect.signature(self.model_type.prepare_inputs_for_generation).parameters
        )
        # `kwargs`/`model_kwargs` is often used to handle optional forward pass inputs like `attention_mask`. If  # noqa: E501
        # `prepare_inputs_for_generation` doesn't accept them, then a stricter check can be made ;)
        if "kwargs" in model_args or "model_kwargs" in model_args:
            model_args |= set(inspect.signature(self.model_type.forward).parameters)
        for key, value in model_kwargs.items():
            if value is not None and key not in model_args:
                unused_model_args.append(key)

        if unused_model_args:
            raise ValueError(
                f"The following `model_kwargs` are not used by the model: {unused_model_args} (note: typos in the"  # noqa: E501
                " generate arguments will also show up in this list)"
            )

    # The method below is overriden from GenerationMixin to allow QuantPagedAttentionGenerator to support various gen_kwargs.  # noqa: E501
    def _get_stopping_criteria(
        self,
        generation_config: GenerationConfig,
        stopping_criteria: Optional[StoppingCriteriaList],
    ) -> StoppingCriteriaList:
        criteria = StoppingCriteriaList()
        if generation_config.max_length is not None:
            max_position_embeddings = getattr(
                self.model.generation_config, "max_position_embeddings", None
            )
            criteria.append(
                MaxLengthCriteria(
                    max_length=generation_config.max_length,
                    max_position_embeddings=max_position_embeddings,
                )
            )
        if generation_config.max_time is not None:
            criteria.append(MaxTimeCriteria(max_time=generation_config.max_time))
        criteria = self._merge_criteria_processor_list(criteria, stopping_criteria)
        return criteria

    def prepare_inputs_for_generation(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        position_ids,
        past_key_values,
        device,
        cur_iter_num,
        prompt_len,
        selected_beam_idx,
    ):
        for first_idx in range(len(past_key_values)):
            past_key_values[first_idx] = list(past_key_values[first_idx])
            for second_idx in range(len(past_key_values[first_idx])):
                past_key_values[first_idx][second_idx] = past_key_values[first_idx][second_idx].to(
                    device
                )

        model_inputs = {"past_key_values": past_key_values}

        # updated_input_ids = input_ids
        batch_beam_size = input_ids.shape[0]
        if cur_iter_num == 0:  # prefill_mode
            # input_ids is unpadded at the moment
            current_logit_idx = input_ids.shape[1] - 1

            _, starting_input_len = input_ids.shape

            assert starting_input_len == prompt_len

            bucketized_attention_mask = torch.zeros(
                (batch_beam_size, self.bucket_size), dtype=torch.int
            )
            bucketized_attention_mask[:, :prompt_len] = attention_mask

            self.update_input_metadata(bucketized_attention_mask.tolist())

            starting_position_id = []
            for single_attention_mask in attention_mask.tolist():
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

            padded_position_ids = torch.repeat_interleave(
                starting_position_ids, batch_beam_size, dim=0
            )

            bucketized_input_ids = torch.zeros((batch_beam_size, self.bucket_size), dtype=torch.int)
            bucketized_input_ids[:, :starting_input_len] = input_ids

            model_inputs.update(
                {
                    "input_ids": bucketized_input_ids.to(device),
                    "attention_mask": bucketized_attention_mask.to(device),
                    "position_ids": padded_position_ids.to(device),
                }
            )

            # renaming viarab

        else:  # decode mode
            current_logit_idx = -1
            index = prompt_len - 1 + cur_iter_num
            attention_mask[:, index] = 1
            if cur_iter_num == 1:
                last_column = position_ids[:, prompt_len - 1]
                position_ids = (last_column + 1).reshape(batch_beam_size, -1)
            else:
                position_ids = position_ids + 1

            self.update_input_metadata(attention_mask.tolist(), selected_beam_idx)
            updated_input_ids = input_ids[:, current_logit_idx][:, None]

            model_inputs.update(
                {
                    "input_ids": updated_input_ids.to(device),
                    "attention_mask": attention_mask.to(device),
                    "position_ids": position_ids.to(device),
                }
            )

        for idx, item in enumerate(self.input_metadata):
            if isinstance(item, torch.Tensor):
                self.input_metadata[idx] = self.input_metadata[idx].to(device)

        model_inputs["input_metadata"] = self.input_metadata

        return current_logit_idx, model_inputs

    def generate(
        self,
        input_batch,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], List[int]]] = None,
        max_length: int = None,
        do_sample: bool = False,
        temperature: float = 1.0,
        **kwargs,
    ):
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """

        # max length will be used only for greedy search

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

        # 1. Handle `generation_config` and kwargs that might update it, and validate the `.generate()` call  # noqa: E501
        if generation_config is None:
            # legacy: users may modify the model configuration to control generation -- update the generation config  # noqa: E501
            # model attribute accordingly, if it was created from the model config
            if self.model.generation_config._from_model_config:
                new_generation_config = GenerationConfig.from_model_config(self.model.config)
                if new_generation_config != self.model.generation_config:
                    self.model.generation_config = new_generation_config
            generation_config = self.model.generation_config

        generation_config = copy.deepcopy(generation_config)
        model_kwargs = generation_config.update(**kwargs)  # All unused kwargs must be model kwargs
        generation_config.validate()
        self._validate_model_kwargs(model_kwargs.copy())
        num_beams = kwargs["num_beams"] if "num_beams" in kwargs.keys() else 1

        # 2. Set generation parameters if not already defined
        logits_processor = (
            logits_processor if logits_processor is not None else LogitsProcessorList()
        )
        stopping_criteria = (
            stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
        )

        if generation_config.pad_token_id is None and generation_config.eos_token_id is not None:
            eos_token_id = generation_config.eos_token_id
            if isinstance(eos_token_id, list):
                eos_token_id = eos_token_id[0]
            generation_config.pad_token_id = eos_token_id

        # Processing inputs
        starting_input_ids = input_batch["input_ids"]
        final_input_ids = starting_input_ids
        starting_attention_mask = input_batch["attention_mask"]

        # Prepare 'max_length' depending on other stopping criteria.
        input_ids_seq_length = starting_input_ids.shape[-1]
        if generation_config.max_new_tokens is not None:
            generation_config.max_length = generation_config.max_new_tokens + input_ids_seq_length

        # prepare logit processor and stopping criteria
        logits_processor = self._get_logits_processor(
            generation_config=generation_config,
            input_ids_seq_length=input_ids_seq_length,
            encoder_input_ids=starting_input_ids,
            prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
            logits_processor=logits_processor,
        )

        stopping_criteria = self._get_stopping_criteria(
            generation_config=generation_config, stopping_criteria=stopping_criteria
        )

        # Related to generation configurations
        config = self.model.config
        # Set generation parameters if not already defined
        # https://github.com/huggingface/transformers/blob/main/src/transformers/generation/utils.py#L1542
        eos_token_id = config.eos_token_id
        if isinstance(eos_token_id, (list, tuple)):
            eos_token_id = eos_token_id[0]
        # Required for batch support
        pad_token_id = eos_token_id

        # About stopping criteria
        # https://github.com/huggingface/transformers/blob/80377eb018c077dba434bc8e7912bcaed3a64d09/src/transformers/generation/utils.py#L1103
        # https://github.com/huggingface/transformers/blob/80377eb018c077dba434bc8e7912bcaed3a64d09/src/transformers/generation/utils.py#L1613
        max_position_embeddings = config.max_position_embeddings
        if max_length is None:
            max_length = max_position_embeddings
        if max_length > max_position_embeddings:
            # warning
            max_length = max_position_embeddings

        if num_beams == 1:
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
            max_length = (
                starting_input_len * 2 if max_length is None else max_length
            )  # artibrarily set considering the charactersitic of summary task
            ### The code here won't be used for graph validation as MLPerf requires beam search
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

                outputs = self.model(
                    input_metadata=self.input_metadata,
                    past_key_values=self.past_key_values,
                    **model_inputs,
                    position_ids=position_ids,  # LongTensor
                    return_dict=True,
                    output_attentions=False,
                    output_hidden_states=False,
                )

                next_token_logits = outputs[:, current_logit_idx, :]
                next_token_scores = next_token_logits.reshape(
                    batch_size, next_token_logits.size(-1)
                )
                next_tokens = torch.argmax(next_token_scores, dim=-1)

                logging.info("Next tokens is: {}".format(next_tokens))

                # prepare for next phase
                current_logit_idx = 0  # for decode phase logit only has one value
                input_ids = next_tokens.reshape(batch_size, -1)
                final_input_ids = torch.cat([final_input_ids, input_ids], dim=-1)

            return final_input_ids

        elif num_beams > 1:
            # beam search

            # prepare beam searchscorer
            beam_scorer = BeamSearchScorer(
                batch_size=starting_input_ids.shape[0],
                num_beams=generation_config.num_beams,
                device=starting_input_ids.device,
                length_penalty=generation_config.length_penalty,
                do_early_stopping=generation_config.early_stopping,
                num_beam_hyps_to_keep=generation_config.num_return_sequences,
                max_length=generation_config.max_length,
            )

            starting_input_ids, model_kwargs = self._expand_inputs_for_generation(
                input_ids=starting_input_ids,
                expand_size=generation_config.num_beams,
                is_encoder_decoder=self.model.config.is_encoder_decoder,
                **model_kwargs,
            )

            return self.beam_search(
                starting_input_ids,
                starting_attention_mask,
                num_beams,
                beam_scorer,
                logits_processor,
                stopping_criteria,
                generation_config,
                max_length,
                pad_token_id,
                eos_token_id,
                output_scores=generation_config.output_scores,
                return_dict_in_generate=generation_config.return_dict_in_generate,
                **model_kwargs,
            )

    def beam_search(
        self,
        input_ids,
        attention_mask,
        num_beams,
        beam_scorer: BeamScorer,
        logits_processor,
        stopping_criteria,
        generation_config,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        output_scores: Optional[bool] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ):
        pad_token_id = (
            pad_token_id if pad_token_id is not None else self.model.generation_config.pad_token_id
        )
        eos_token_id = (
            eos_token_id if eos_token_id is not None else self.model.generation_config.eos_token_id
        )
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        output_scores = (
            output_scores
            if output_scores is not None
            else self.model.generation_config.output_scores
        )
        output_attentions = (
            output_attentions
            if output_attentions is not None
            else self.model.generation_config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.model.generation_config.output_hidden_states
        )
        return_dict_in_generate = (
            return_dict_in_generate
            if return_dict_in_generate is not None
            else self.model.generation_config.return_dict_in_generate
        )

        batch_size = len(beam_scorer._beam_hyps)
        batch_beam_size, cur_len = input_ids.shape

        unpadded_input_ids = input_ids
        # start generating new token

        input_ids = None
        position_ids = None

        if num_beams * batch_size != batch_beam_size:
            raise ValueError(
                f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but is {batch_beam_size}."  # noqa: E501
            )

        # init attention / hidden states / scores tuples
        scores = () if (return_dict_in_generate and output_scores) else None
        beam_indices = (
            tuple(() for _ in range(batch_beam_size))
            if (return_dict_in_generate and output_scores)
            else None
        )
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None

        # if model is an encoder-decoder, retrieve encoder attention weights and hidden states
        if return_dict_in_generate and self.config.is_encoder_decoder:
            encoder_attentions = (  # noqa: F841
                model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
            )
            encoder_hidden_states = (  # noqa: F841
                model_kwargs["encoder_outputs"].get("hidden_states")
                if output_hidden_states
                else None
            )

        # initialise score of first beam with 0 and the rest with -1e9. This makes sure that only tokens  # noqa: E501
        # of the first beam are considered to avoid sampling the exact same tokens across all beams.
        beam_scores = torch.zeros(
            (batch_size, num_beams), dtype=torch.float, device=self.model.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        beam_idx = None

        this_peer_finished = False  # used by synced_gpus only  # noqa: F841

        prompt_len = unpadded_input_ids.shape[1]
        # run prefill model with [batch_size, prompt_len] shape, not [batch_size * beam_size, prompt_len]  # noqa: E501
        cur_iter_num = 0
        while True:
            current_logit_idx, model_inputs = self.prepare_inputs_for_generation(
                input_ids=unpadded_input_ids,
                attention_mask=attention_mask,
                position_ids=position_ids,
                past_key_values=self.past_key_values,
                device=self.model.device,
                cur_iter_num=cur_iter_num,
                prompt_len=prompt_len,
                selected_beam_idx=beam_idx,
            )  # In this method, unpadded input ids & attention masks are bucketized and the input metadata are updated accordingly. Also,  # noqa: E501

            outputs = self.model(**model_inputs)

            vocab_size = outputs.size(2)

            next_token_logits = outputs[:, current_logit_idx, :]
            next_token_scores = torch.nn.functional.log_softmax(next_token_logits, dim=-1)

            next_token_scores_processed = logits_processor(unpadded_input_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                next_token_scores
            )

            # select num_beams next tokens from each batch
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

            next_token_scores, next_tokens = torch.topk(
                next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
            )

            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size

            # stateless
            beam_outputs = beam_scorer.process(
                unpadded_input_ids,
                next_token_scores,
                next_tokens,
                next_indices,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                beam_indices=beam_indices,
            )

            beam_scores = beam_outputs["next_beam_scores"]
            beam_next_tokens = beam_outputs["next_beam_tokens"]  # beam_next_tokens
            beam_idx = beam_outputs["next_beam_indices"]  # next_beam_origin_indices

            cur_iter_num = cur_iter_num + 1

            # update the inputs
            unpadded_input_ids = torch.cat(
                (unpadded_input_ids[beam_idx, :], beam_next_tokens.unsqueeze(1)), dim=1
            )

            attention_mask = model_inputs["attention_mask"]
            position_ids = model_inputs["position_ids"]

            # Store scores, attentions and hidden_states when required
            if return_dict_in_generate:
                if output_scores:
                    scores += (next_token_scores_processed,)
                if output_attentions:
                    decoder_attentions += (
                        (outputs.decoder_attentions,)
                        if self.config.is_encoder_decoder
                        else (outputs.attentions,)
                    )
                    if self.config.is_encoder_decoder:
                        cross_attentions += (outputs.cross_attentions,)

                if output_hidden_states:
                    decoder_hidden_states += (
                        (outputs.decoder_hidden_states,)
                        if self.config.is_encoder_decoder
                        else (outputs.hidden_states,)
                    )

            if beam_scorer.is_done or stopping_criteria(unpadded_input_ids, scores):
                break

            if return_dict_in_generate and output_scores:
                beam_indices = tuple(
                    (beam_indices[beam_idx[i]] + (beam_idx[i],) for i in range(len(beam_indices)))
                )

            if cur_iter_num == 1:
                # After the prefill phase step, there is no need to update the past key-value memory
                beam_idx = None

        sequence_outputs = beam_scorer.finalize(
            unpadded_input_ids,
            beam_scores,
            next_tokens,
            next_indices,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            max_length=stopping_criteria.max_length,
            beam_indices=beam_indices,
        )

        self.reinitialize()
        return sequence_outputs["sequences"]

    def reinitialize(self):
        self.input_metadata = None

        for tensor_list in self.past_key_values:
            for layer_idx in range(len(tensor_list)):
                tensor_list[layer_idx] = tensor_list[layer_idx].zero_()

        block_indices = self.past_key_values[0][0].shape[0]

        # exist for each sequence
        self.active_key_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd
        self.active_value_block_indices: List[
            List[int]
        ] = []  # key is batch_idx, value is block indicesd

        # keep track of last real block id for each batch
        # ((key_block, key_token), (value_block, value_token))
        self.valid_block_meta: List[Tuple[Tuple[int, int]]] = []

        self.available_block_indices = list(range(1, block_indices))

    def update_input_metadata(
        self,
        updated_attention_mask: List[List[int]],
        selected_beam_idx: torch.Tensor = None,
    ):
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
            # 일단 앞에서부터 하나씩 block 들을 만들고 block indices 를 부여하고 진짜인지 아닌지를 판단하기  # noqa: E501
            # 앞에서부터 하나씩 끊어서 block 을 만들면 됨
            for batch_idx, single_attention_mask in enumerate(updated_attention_mask):
                new_key_location = []
                new_value_location = []
                split_blocks = [
                    single_attention_mask[i : i + self.block_size]
                    for i in range(0, len(single_attention_mask), self.block_size)
                ]

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
            # if that block is full, assign a new block and replace zero block that should be in that place  # noqa: E501
            # if that block is NOT full, find the location

            decode_key_new_block_location = []
            decode_value_new_block_location = []

            new_active_key_blocks = []
            new_active_value_blocks = []
            if selected_beam_idx is not None:
                selected_beam_idx = selected_beam_idx.tolist()

            for batch_idx, single_attention_mask in enumerate(updated_attention_mask):
                (
                    (last_valid_key_block_idx, last_token_idx),
                    (last_valid_value_block_idx, last_token_idx),
                ) = self.valid_block_meta[batch_idx]

                if last_token_idx == self.block_size - 1:
                    if selected_beam_idx is not None:
                        new_active_key_block = self.active_key_block_indices[
                            selected_beam_idx[batch_idx]
                        ][:]
                        new_active_value_block = self.active_value_block_indices[
                            selected_beam_idx[batch_idx]
                        ][:]
                    else:
                        new_active_key_block = self.active_key_block_indices[batch_idx]
                        new_active_value_block = self.active_value_block_indices[batch_idx]

                    # this block is full, so replace
                    new_key_block_idx = self.available_block_indices.pop()
                    last_zero_block_idx = len(self.active_key_block_indices[batch_idx])
                    for i, val in enumerate(self.active_key_block_indices[batch_idx]):
                        if val == last_valid_key_block_idx:
                            # this i+1 will be the next zero block
                            last_zero_block_idx = i + 1
                            break

                    new_active_key_block[last_zero_block_idx] = new_key_block_idx
                    new_active_key_blocks.append(new_active_key_block)

                    new_value_block_idx = self.available_block_indices.pop()
                    last_zero_block_idx = len(self.active_value_block_indices[batch_idx])
                    for i, val in enumerate(self.active_value_block_indices[batch_idx]):
                        if val == last_valid_value_block_idx:
                            # this i+1 will be the next zero block
                            last_zero_block_idx = i + 1
                            break

                    new_active_value_block[last_zero_block_idx] = new_value_block_idx
                    new_active_value_blocks.append(new_active_value_block)
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

            if new_active_key_blocks:
                self.active_key_block_indices = new_active_key_blocks
            if new_active_value_blocks:
                self.active_value_block_indices = new_active_value_blocks

            self.input_metadata = InputMetadata(
                key_cache_idx=self.active_key_block_indices,
                value_cache_idx=self.active_value_block_indices,
                block_max_seq_len=self.num_max_block,
                block_size=self.block_size,
                is_prefill=False,
                new_key_location=decode_key_new_block_location,
                new_value_location=decode_value_new_block_location,
            )

        self.input_metadata = [
            self.input_metadata.new_key_location,
            self.input_metadata.new_value_location,
            self.input_metadata.bucket_size,
            self.input_metadata.valid_key_indices,
            self.input_metadata.valid_value_indices,
        ]  # The input metadata must be converted to list to enable tracing.
