import copy
from typing import Callable, List, Optional, Union

import torch
from transformers import (
    BeamScorer,
    BeamSearchScorer,
    GenerationConfig,
    LogitsProcessorList,
    StoppingCriteriaList,
)

from furiosa_llm_models.generators.v2.generator import Generator, PreAllocatedGenerator


class QuantPreAllocatedConcatGenerator(PreAllocatedGenerator):
    def __init__(
        self,
        quant_causallm,
        bucket_size: int,
        **kwargs,
    ) -> None:
        super().__init__(quant_causallm, bucket_size, **kwargs)

    def is_required_kv_index(self):
        return False

    def decode_inputs(self, attention_mask, past_key_values, next_tokens, sequence_idx):
        batch_size = attention_mask.shape[0]

        if attention_mask.shape[1] < self.bucket_size:
            # Before: [[1, 1, 1, 0, 0, 0, 0],    [0, 1, 1, 0, 0, 0, 0]]
            # After:  [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            attention_mask = torch.cat(
                [attention_mask, attention_mask.new_ones((batch_size, 1))], dim=-1
            )
        else:
            # Set 1 to attention_masks at pos;e.g,
            # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
            # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
            pos = sequence_idx - 1
            attention_mask[:, pos] += attention_mask.new_ones(batch_size)

        # pos = sequence_idx - 1
        # attention_mask[:, pos] += attention_mask.new_ones(batch_size)
        # Create position_ids on the fly for batch generation; e.g.,
        # attention_masks [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]] -> position_ids [[3], [2]]  # noqa: E501
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids = position_ids[:, -1:]

        return next_tokens[:, None], attention_mask, position_ids, past_key_values

    def handle_outputs(self, outputs, past_key_values, sequence_idx, is_prefill_phase):
        logits, new_keys, new_values = outputs

        if hasattr(self.model.config, "n_layer"):
            n_layer = self.model.config.n_layer
        elif hasattr(self.model.config, "num_hidden_layers"):
            n_layer = self.model.config.num_hidden_layers
        else:
            NotImplementedError

        if hasattr(self.model.config, "n_head"):
            n_head = self.model.config.n_head
        elif hasattr(self.model.config, "num_key_value_heads"):
            n_head = self.model.config.num_key_value_heads

        batch_size = logits.shape[0]

        if is_prefill_phase:
            # the prefill forward returns the past_key_values via new_keys and new_values.
            # Both new_keys and new_values have the shape: [batch_size, n_head, bucket_size - 1, hidden_size].  # noqa: E501
            # Preallocated Concat version uses the last sequence of past_key_values to concat
            # temporarily new key, values in order to compute the new attention score.
            # That's why the sequence length of past_key_values must be bucket_size - 1.
            past_key_values = [(key, value) for key, value in zip(new_keys, new_values)]
            return logits, past_key_values
        else:
            # new_keys and new_values have only newly computed result,
            # so its shape is [batch_size, n_head, 1, hidden_size].
            # past_key_values has the same shape: [batch_size, n_head, bucket_size - 1, hidden_size].  # noqa: E501
            for layer_idx in range(n_layer):
                past_keys, past_values = past_key_values[layer_idx]
                past_keys[:, :, sequence_idx, :] = new_keys[layer_idx].reshape(
                    batch_size, n_head, -1
                )
                past_values[:, :, sequence_idx, :] = new_values[layer_idx].reshape(
                    batch_size, n_head, -1
                )

        return logits, past_key_values

    @torch.no_grad()
    def generate(
        self,
        inputs,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        prefix_allowed_tokens_fn: Optional[Callable[[int, torch.Tensor], List[int]]] = None,
        max_length=None,
        do_sample: bool = False,
        temperature: float = 1.0,
        **kwargs,
    ):
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
        self.model._validate_model_kwargs(model_kwargs.copy())
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

        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        # Prepare 'max_length' depending on other stopping criteria.
        input_ids_seq_length = input_ids.shape[-1]
        if generation_config.max_new_tokens is not None:
            generation_config.max_length = generation_config.max_new_tokens + input_ids_seq_length

        # prepare logit processor and stopping criteria
        logits_processor = self.model._get_logits_processor(
            generation_config=generation_config,
            input_ids_seq_length=input_ids_seq_length,
            encoder_input_ids=input_ids,
            prefix_allowed_tokens_fn=prefix_allowed_tokens_fn,
            logits_processor=logits_processor,
        )

        stopping_criteria = self.model._get_stopping_criteria(
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
            return self.greedy_search(
                input_ids, attention_mask, max_length, pad_token_id, eos_token_id
            )
        else:
            # prepare beam searchscorer
            beam_scorer = BeamSearchScorer(
                batch_size=input_ids.shape[0],
                num_beams=generation_config.num_beams,
                device=input_ids.device,
                length_penalty=generation_config.length_penalty,
                do_early_stopping=generation_config.early_stopping,
                num_beam_hyps_to_keep=generation_config.num_return_sequences,
                max_length=generation_config.max_length,
            )

            input_ids, model_kwargs = self.model._expand_inputs_for_generation(
                input_ids=input_ids,
                expand_size=generation_config.num_beams,
                is_encoder_decoder=self.model.config.is_encoder_decoder,
                **model_kwargs,
            )

            return self.beam_search(
                input_ids,
                attention_mask,
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

    def greedy_search(self, input_ids, attention_mask, max_length, pad_token_id, eos_token_id):
        eos_token_id_tensor = torch.tensor([eos_token_id]).to(input_ids.device)
        pad_token_id = (
            pad_token_id if pad_token_id is not None else self.model.generation_config.pad_token_id
        )
        eos_token_id = (
            eos_token_id if eos_token_id is not None else self.model.generation_config.eos_token_id
        )
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]

        # keep track of which sequences are already finished
        unfinished_sequences = torch.ones(
            input_ids.shape[0], dtype=torch.long, device=input_ids.device
        )
        past_key_values = None
        next_input_ids = input_ids
        sequence_idx = input_ids.shape[1] - 1  # which sequence is working for generation
        is_prefill_phase = True
        device = self.model.prefill_model.device
        next_tokens = None

        while True:
            if is_prefill_phase:
                next_input_ids, attention_mask, position_ids = self.prefill_inputs(
                    next_input_ids, attention_mask
                )
            else:
                # make input ids, attention, position_ids for decode
                next_input_ids, attention_mask, position_ids, past_key_values = self.decode_inputs(
                    attention_mask, past_key_values, next_tokens, sequence_idx
                )

            forward_kwargs = {
                "input_ids": next_input_ids.to(device),
                "attention_mask": attention_mask.to(device),
                "position_ids": position_ids.to(device),
            }

            if past_key_values:
                for first_idx in range(len(past_key_values)):
                    past_key_values[first_idx] = list(past_key_values[first_idx])
                    for second_idx in range(len(past_key_values[first_idx])):
                        past_key_values[first_idx][second_idx] = past_key_values[first_idx][
                            second_idx
                        ]
                forward_kwargs["past_key_values"] = past_key_values

            # PreAllocated version (required input_put) requires the additional parameter 'new_index'.  # noqa: E501
            if self.is_required_kv_index():
                # add new_index to forward_kwargs
                forward_kwargs["new_index"] = (
                    torch.IntTensor([sequence_idx]) if not is_prefill_phase else None
                )

            if is_prefill_phase:
                outputs = self.model.prefill_model.forward(**forward_kwargs)
            else:
                outputs = self.model.decode_model.forward(**forward_kwargs)

            logits, past_key_values = self.handle_outputs(
                outputs, past_key_values, sequence_idx, is_prefill_phase
            )

            ##################################################################################################
            # greedy_search() after forward()
            ##################################################################################################
            logit_idx = sequence_idx if is_prefill_phase else 0
            logits = logits.to(input_ids.device)
            next_tokens = Generator.find_next_tokens(
                logits, logit_idx, unfinished_sequences, pad_token_id
            )
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)

            # if eos_token was found in one sentence, set sentence to finished
            unfinished_sequences = unfinished_sequences.mul(
                next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                .ne(eos_token_id_tensor.unsqueeze(1))
                .prod(dim=0)
            )

            sequence_idx += 1
            assert (sequence_idx + 1) == input_ids.shape[1]
            # stop when each sentence is finished
            if unfinished_sequences.max() == 0 or (sequence_idx + 1) >= max_length:
                break

            is_prefill_phase = False

        return input_ids

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
            (batch_size, num_beams), dtype=torch.float, device=input_ids.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))

        # run prefill model with [batch_size, prompt_len] shape, not [batch_size * beam_size, prompt_len]  # noqa: E501
        next_input_ids, attention_mask, position_ids = self.prefill_inputs(
            input_ids, attention_mask
        )  # Given an unpadded input_ids and attention_mask, it creates the padded input_ids, attention_mask, and position_ids.  # noqa: E501

        device = self.model.prefill_model.device

        outputs = self.model.prefill_model.forward(
            input_ids=next_input_ids.to(device),
            attention_mask=attention_mask.to(device),
            position_ids=position_ids.to(device),
        )

        logits, past_key_values = self.handle_outputs(
            outputs, None, cur_len - 1, True
        )  # storing the KV_Cache to the appropriate index.

        is_prefill_mode = True

        while True:
            vocab_size = logits.size(2)
            next_token_logits = (
                logits[:, cur_len - 1] if is_prefill_mode else logits[:, -1]
            )  # During prefill, one must take the logit of the last token of the input prompt.
            is_prefill_mode = False

            # multiply prev scores of each sequence with next token scores, but in logarithm
            next_token_logits = self.model.adjust_logits_during_generation(
                next_token_logits, cur_len=cur_len
            )
            next_token_scores = torch.nn.functional.log_softmax(
                next_token_logits, dim=-1
            )  # [batch_Size * num_beams, vocab_size]

            next_token_scores_processed = logits_processor(input_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                next_token_scores
            )

            # select num_beams next tokens from each batch
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

            # Sample 2 next tokens for each beam (so we have some spare tokens and match output of beam search)  # noqa: E501
            next_token_scores, next_tokens = torch.topk(
                next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
            )

            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size
            cur_len = cur_len + 1

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

            # stateless
            beam_outputs = beam_scorer.process(
                input_ids,
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

            sequence_idx = input_ids.size(1)

            input_ids = torch.cat((input_ids[beam_idx, :], beam_next_tokens.unsqueeze(1)), dim=1)

            if beam_scorer.is_done or stopping_criteria(input_ids, scores):
                break

            if return_dict_in_generate and output_scores:
                beam_indices = tuple(
                    (beam_indices[beam_idx[i]] + (beam_idx[i],) for i in range(len(beam_indices)))
                )

            # past_key_values = map_cache(past_key_values, lambda t: t[next_beam_origin_indices])

            next_input_ids, attention_mask, position_ids, past_key_values = self.decode_inputs(
                attention_mask, past_key_values, beam_next_tokens, sequence_idx
            )  # Must set the attention mask element that corresponds to the currently generated token.  # noqa: E501

            if past_key_values is not None:
                past_key_values = self.model._reorder_cache(past_key_values, beam_idx)

            forward_kwargs = {
                "input_ids": next_input_ids.to(device),
                "attention_mask": attention_mask.to(device),
                "position_ids": position_ids.to(device),
                "past_key_values": past_key_values,
            }

            # PreAllocated version (required input_put) requires the additional parameter 'new_index'.  # noqa: E501
            if self.is_required_kv_index():
                # add new_index to forward_kwargs
                forward_kwargs["new_index"] = torch.IntTensor([sequence_idx])

            outputs = self.model.decode_model.forward(**forward_kwargs)

            logits, past_key_values = self.handle_outputs(
                outputs, past_key_values, sequence_idx, False
            )

        sequence_outputs = beam_scorer.finalize(
            input_ids,
            beam_scores,
            next_tokens,
            next_indices,
            pad_token_id=pad_token_id,
            eos_token_id=eos_token_id,
            max_length=stopping_criteria.max_length,
            beam_indices=beam_indices,
        )

        return sequence_outputs["sequences"]
