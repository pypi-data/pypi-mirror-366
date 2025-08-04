"""Generator provides decoding algorithms of our modified models.

Each generator implementation assumes the model
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

import torch
from transformers import (
    BatchEncoding,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)
from transformers.modeling_outputs import CausalLMOutputWithCrossAttentions, CausalLMOutputWithPast

from furiosa_llm_models.generators.v2.tokenizer import get_tokenizer

USE_CACHE = True
OUTPUT_ATTENTIONS = False
OUTPUT_HIDDEN_STATES = False
RETURN_DICT = False

SUPPORTED_GENERATION_RETURN_DICT_TYPES = (CausalLMOutputWithPast, CausalLMOutputWithCrossAttentions)


def map_cache(kv_cache, f):
    return tuple(tuple(f(t) for t in kv) for kv in kv_cache)


def get_generation_output_kwargs(
    output_attentions: bool, output_hidden_states: bool, return_dict: bool, use_cache: bool
) -> Dict:
    if output_attentions:
        raise ValueError(
            f"model.forward with output_attentions={output_attentions} is not supported."
        )
    if output_hidden_states:
        raise ValueError(
            f"model.forward with output_hidden_states={output_hidden_states} is not supported."
        )
    if not use_cache:
        raise ValueError(f"model.forward with use_cache={use_cache} is not supported.")

    return {
        "output_attentions": output_attentions,
        "output_hidden_states": output_hidden_states,
        "return_dict": return_dict,
        "use_cache": use_cache,
    }


class Generator(ABC):
    eos_token_id = None
    output_attentions = OUTPUT_ATTENTIONS
    output_hidden_states = OUTPUT_HIDDEN_STATES
    return_dict = RETURN_DICT
    use_cache = USE_CACHE

    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: Optional[Union[PreTrainedTokenizer, PreTrainedTokenizerFast]] = None,
        **kwargs,
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer if tokenizer is not None else get_tokenizer(model)
        # This flag is used to determine whether to return the generated text or torch tensor
        # in self.greedy_search() and self.beam_search().
        self.return_generated_text = False

    @abstractmethod
    def is_required_kv_index(self): ...

    def generate(
        self,
        prompts: Optional[Union[List[str], str]] = None,
        num_beams: int = 1,
        do_sample: bool = False,
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/configuration_utils.py#L234
        max_length: int = 20,
        max_new_tokens: Optional[int] = None,
        early_stopping: bool = True,
        temperature: float = 1.0,
        **kwargs,
    ):
        # Taking prompts as input is suitable for API like Huggingface's TextGenerationPipeline.
        # ref: https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/pipelines/text_generation.py#L25-L36
        # This is a temporary implementation for the purpose of MLPerf testing.
        # The final API design needs to be discussed and implemented.
        # If we decide to exclude the prompts,
        # we can use input_ids and attention_mask as positional arguments.
        if prompts is not None:
            prompts = [prompts] if isinstance(prompts, str) else prompts
            inputs: BatchEncoding = self.tokenizer.encode_auto(prompts, return_tensors="pt")
            input_ids: torch.Tensor = inputs.input_ids
            attention_mask: torch.Tensor = inputs.attention_mask
            # For MLPerf test scenario, we need to return the generated text.
            self.return_generated_text = True
        else:
            input_ids: torch.Tensor = kwargs.get("input_ids", None)
            attention_mask: torch.Tensor = kwargs.get("attention_mask", None)

        if input_ids is None:
            raise ValueError("input_ids is required.")
        if attention_mask is None:
            raise ValueError("attention_mask is required.")

        # Related to generation configurations
        config = self.model.config
        # Set generation parameters if not already defined
        # https://github.com/huggingface/transformers/blob/main/src/transformers/generation/utils.py#L1542
        eos_token_id = config.eos_token_id
        if isinstance(eos_token_id, (list, tuple)):
            eos_token_id = eos_token_id[0]
        # Required for batch support
        pad_token_id = eos_token_id

        # TODO: Get generation configuration from generation_config first, then from model.config
        # ref: # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1194-L1200
        input_ids_seq_length = input_ids.shape[-1]

        if max_new_tokens is not None:
            # Override max_length if max_new_tokens is provided, even if max_length is given.
            # ref: https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1383
            max_length = input_ids_seq_length + max_new_tokens

        if input_ids_seq_length >= max_length:
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1390-L1396
            # https://github.com/huggingface/transformers/blob/v4.40.2/src/transformers/generation/utils.py#L1147-L1153
            # In the latest version(v4.40.2), it raises ValueError if
            # input_ids_seq_length >= max_length
            raise ValueError(
                f"Input length {input_ids_seq_length} is already longer than the maximum "
                "generation length {max_length}. This can lead to unexpected behavior. "
                "You should consider increasing `max_length` or, better yet, "
                "setting `max_new_tokens`."
            )

        # This is the maximum length that the model can generate up to.
        max_gen_limit = (
            min(max_length, config.max_position_embeddings)
            if config.max_position_embeddings is not None
            else max_length
        )

        # TODO: Implement logic to determine the min_length and use it for decoding strategy
        # when it becomes clear that not dealing with min_length affects the model's accuracy.

        if do_sample is True:
            raise ValueError(f"{do_sample=} is not supported yet.")

        # TODO - currently it supports only greedy/beam search. Let's expand for more various
        # decoding algorithms
        if num_beams == 1 and not do_sample:
            return self.greedy_search(
                input_ids, attention_mask, max_gen_limit, pad_token_id, eos_token_id
            )
        elif num_beams > 1 and not do_sample:
            return self.beam_search(
                input_ids,
                attention_mask,
                max_gen_limit,
                pad_token_id,
                eos_token_id,
                num_beams,
                early_stopping,
            )
        else:
            # For all generation strategies that Hugging Face supports in v4.31.0 are:
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L475-L489
            # For detailed explanation at algorithm level, see:
            # https://huggingface.co/docs/transformers/generation_strategies
            raise NotImplementedError(
                "Generation sterategy other than greedy/beam search is not supported yet."
            )

    def greedy_search(
        self, input_ids, attention_mask, max_gen_limit, pad_token_id, eos_token_id
    ) -> Union[torch.Tensor, List[List[str]]]:
        # init values / init attention / hidden states / scores tuples
        batch_size = input_ids.shape[0]
        eos_token_id_tensor = torch.tensor([eos_token_id]).to(input_ids.device)

        # https://github.com/huggingface/transformers/blob/0ea42ef0f9f71deba7775ead33afa0e493823d60/src/transformers/generation/utils.py#L2553C2-L2553C2
        # keep track of which sequences are already finished: 1 means unfinished, 0 means finished.
        unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
        past_key_values = None
        next_input_ids = input_ids
        sequence_idx = input_ids.shape[1] - 1  # which sequence is working for generation
        is_prefill_phase = True

        forward_kwargs = get_generation_output_kwargs(
            self.output_attentions, self.output_hidden_states, self.return_dict, self.use_cache
        )

        while True:
            # A simplified version of _update_model_kwargs_for_generation() in
            # transformers/generation_utils.py
            if is_prefill_phase:
                next_input_ids, attention_mask, position_ids = self.prefill_inputs(
                    next_input_ids, attention_mask
                )
            else:
                # make input ids, attention, position_ids for decode
                next_input_ids, attention_mask, position_ids, past_key_values = self.decode_inputs(
                    attention_mask,
                    past_key_values,
                    next_tokens,  # noqa: F821
                    sequence_idx,
                )

            forward_kwargs.update(
                {
                    "input_ids": next_input_ids,
                    "attention_mask": attention_mask,
                    "position_ids": position_ids,
                    "past_key_values": past_key_values,
                }
            )

            # PreAllocated (required input_put) requires the additional parameter 'new_index'.
            if self.is_required_kv_index():
                # add new_index to forward_kwargs
                forward_kwargs["new_index"] = (
                    torch.IntTensor([sequence_idx]) if not is_prefill_phase else None
                )

            outputs = self.model.forward(**forward_kwargs)
            logits, past_key_values = self.handle_outputs(
                outputs, past_key_values, sequence_idx, is_prefill_phase
            )

            #######################################################################################
            # greedy_search() after forward()
            #######################################################################################
            logit_idx = sequence_idx if is_prefill_phase else 0
            next_tokens = Generator.find_next_tokens(
                logits, logit_idx, unfinished_sequences, pad_token_id
            )
            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)

            # Update unfinished_sequences
            # (If any next token in a batch is EOS, it updates to 0 or keep 1)
            unfinished_sequences = unfinished_sequences.mul(
                next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                .ne(eos_token_id_tensor.unsqueeze(1))
                .prod(dim=0)
            )

            sequence_idx += 1
            assert (sequence_idx + 1) == input_ids.shape[1]
            # Borrowed from MaxLengthCriteria in stopping_criteria.py but simplified.
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/stopping_criteria.py#L64-L69
            # Checking if no more unfinished sequences or max_gen_limit is reached
            if unfinished_sequences.max() == 0 or (sequence_idx + 1) >= max_gen_limit:
                break

            is_prefill_phase = False

        return (
            input_ids
            if not self.return_generated_text
            else [[self.tokenizer.decode(output, skip_special_tokens=True)] for output in input_ids]
        )

    def beam_search(
        self,
        input_ids,
        attention_mask,
        max_gen_limit,
        pad_token_id,
        eos_token_id,
        num_beams,
        early_stopping,
    ) -> Union[torch.Tensor, List[List[str]]]:
        if early_stopping is not True:
            raise ValueError(f"{early_stopping=} is not supported yet.")

        batch_size, decoder_prompt_len = input_ids.shape

        # initialise score of first beam with 0 and the rest with -1e9.
        # This makes sure that only tokens of the first beam are considered to avoid sampling the
        # exact same tokens across all beams.
        beam_scores = torch.zeros(
            (batch_size, num_beams), dtype=torch.float, device=input_ids.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))

        # run prefill model with [batch_size, prompt_len] shape, not
        # [batch_size * beam_size, prompt_len]
        next_input_ids, attention_mask, position_ids = self.prefill_inputs(
            input_ids, attention_mask
        )
        outputs = self.model.forward(
            input_ids=input_ids, attention_mask=attention_mask, position_ids=position_ids
        )
        logits, past_key_values = self.handle_outputs(outputs, None, decoder_prompt_len - 1, True)

        # stretch tensors to beam size
        input_ids = input_ids.repeat_interleave(
            num_beams, 0
        )  # [batch_size * num_beams, sequence_length]
        attention_mask = attention_mask.repeat_interleave(
            num_beams, 0
        )  # [batch_size * num_beams, sequence_length]
        logits = logits.repeat_interleave(
            num_beams, 0
        )  # [batch_size * num_beams, sequence_length, vocab_size]
        past_key_values = map_cache(
            past_key_values, lambda t: t.repeat_interleave(num_beams, 0)
        )  # [batch_size * num_beams, ...]
        beam_done = torch.full((batch_size * num_beams,), False)

        forward_kwargs = get_generation_output_kwargs(
            self.output_attentions,
            self.output_hidden_states,
            self.return_dict,
            self.use_cache,
        )

        while True:
            vocab_size = logits.size(2)

            # multiply prev scores of each sequence with next token scores, but in logarithm
            next_token_scores = torch.nn.functional.log_softmax(
                logits[:, -1], dim=-1
            )  # [batch_Size * num_beams, vocab_size]
            next_token_scores = next_token_scores + beam_scores[:, None]

            # select num_beams next tokens from each batch
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)
            beam_scores, next_tokens = torch.topk(
                next_token_scores, num_beams, dim=1
            )  # [batch_size, num_beams]
            beam_scores = beam_scores.view(batch_size * num_beams)

            # find beam index from each tokens selected
            # TODO: it might reduce kv-cache copying to reorder this tensor in smart way
            next_token_origin_indices = next_tokens // vocab_size  # [batch_size, num_beams]
            next_beam_origin_indices = next_token_origin_indices + (
                torch.arange(batch_size) * num_beams
            ).unsqueeze(1)
            next_beam_origin_indices = next_beam_origin_indices.view(batch_size * num_beams)

            # copy/reorder prev state based on next tokens selected
            next_tokens = next_tokens % vocab_size  # [batch_size, num_beams]
            next_beam_tokens = next_tokens.view(batch_size * num_beams)
            next_beam_tokens[beam_done] = pad_token_id
            beam_done = beam_done | (next_beam_tokens == eos_token_id)
            input_ids = torch.cat(
                (input_ids[next_beam_origin_indices], next_beam_tokens.unsqueeze(1)), dim=1
            )

            if input_ids.size(1) >= max_gen_limit or beam_done.all():
                break

            attention_mask = attention_mask[next_beam_origin_indices]
            past_key_values = map_cache(past_key_values, lambda t: t[next_beam_origin_indices])
            sequence_idx = input_ids.size(1) - 1

            # run decode model with [batch_size * num_beams, sequence_length] shape
            next_input_ids, attention_mask, position_ids, past_key_values = self.decode_inputs(
                attention_mask, past_key_values, next_beam_tokens, sequence_idx
            )

            forward_kwargs.update(
                {
                    "input_ids": next_input_ids,
                    "attention_mask": attention_mask,
                    "position_ids": position_ids,
                    "past_key_values": past_key_values,
                }
            )

            # PreAllocated (required input_put) requires the additional parameter 'new_index'.
            if self.is_required_kv_index():
                # add new_index to forward_kwargs
                forward_kwargs["new_index"] = torch.IntTensor([sequence_idx])

            outputs = self.model.forward(**forward_kwargs)
            logits, past_key_values = self.handle_outputs(
                outputs, past_key_values, sequence_idx, False
            )

        return (
            input_ids
            if not self.return_generated_text
            else [
                [self.tokenizer.decode(output, skip_special_tokens=True) for output in sample]
                for sample in input_ids.view(batch_size, num_beams, -1)
            ]
        )

    def handle_outputs(self, outputs, past_key_values, kv_index, is_prefill_phase):
        if isinstance(outputs, SUPPORTED_GENERATION_RETURN_DICT_TYPES):
            return outputs.to_tuple()
        elif isinstance(outputs, tuple):
            return outputs
        else:
            raise ValueError(f"Unsupported generation output type: {type(outputs)}")

    @abstractmethod
    def prefill_inputs(self, input_ids, attention_mask): ...

    @abstractmethod
    def decode_inputs(self, attention_mask, past_key_values, next_tokens, sequence_idx): ...

    @staticmethod
    def find_next_tokens(logits, logit_idx, unfinished_sequences, pad_token_id):
        # Get the logit for the current token:
        # [batch size, prompt_length, vocab_size] -> [batch size, vocab_size]
        next_tokens_scores = logits[:, logit_idx, :]
        # For greedy search, Transformers doesn't use softmax
        next_tokens = torch.argmax(next_tokens_scores, dim=-1)
        # Fill the next token with pad_token_id if the sequence is not finished,
        # or fill pad_token_id.
        next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)
        return next_tokens


class OriginalGenerator(Generator):
    """This generator assumes"""

    def __init__(
        self,
        model: PreTrainedModel,
        **kwargs,
    ) -> None:
        super().__init__(model, **kwargs)

    def is_required_kv_index(self):
        return False

    def prefill_inputs(self, input_ids, attention_mask):
        # When attention masks is [[1, 1, 1] [0, 1, 1]], the result becomes [[0, 1, 2], [-1, 0, 1]].
        position_ids = attention_mask.long().cumsum(-1) - 1
        # attention_masks [[0, 1, 2], [-1, 0, 1]] -> position_ids [[0, 1, 2], [ 1, 0, 1]]
        # It's necessary to avoid out of index of position embeddings.
        position_ids.masked_fill_(attention_mask == 0, 1)
        return input_ids, attention_mask, position_ids

    def decode_inputs(self, attention_mask, past_key_values, next_tokens, sequence_idx):
        # Update attention mask; e.g.,
        # [[1, 1, 1], [0, 1, 1]] -> [[1, 1, 1, 1], [0, 1, 1, 1]]
        attention_mask = torch.cat(
            [attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1
        )
        # Create position_ids on the fly for batch generation; e.g.,
        # attention_masks [[1, 1, 1, 1], [0, 1, 1, 1]] -> position_ids [[3], [2]]
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids.masked_fill_(attention_mask == 0, 1)
        position_ids = position_ids[:, -1:]

        return next_tokens[:, None], attention_mask, position_ids, past_key_values


class PreAllocatedGenerator(Generator):
    def __init__(
        self,
        model: PreTrainedModel,
        bucket_size: int,
        **kwargs,
    ) -> None:
        super().__init__(model, **kwargs)
        self.bucket_size = bucket_size

    def is_required_kv_index(self):
        return True

    def prefill_inputs(self, input_ids, attention_mask):
        batch_size = input_ids.shape[0]

        # Padded input_ids(bucket_size=7); e.g.,
        # [[5661, 1492, 318, 0, 0, 0, 0], [50256, 5661, 318, 0, 0, 0, 0]]
        padded_inputs = torch.zeros((batch_size, self.bucket_size - 1), dtype=torch.int64)
        padded_inputs[:, : input_ids.shape[1]] = input_ids

        # Padded attention_masks(bucket_size=7); e.g.,
        # [[1, 1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0]]
        padded_attention_mask = torch.zeros((batch_size, self.bucket_size - 1), dtype=torch.int64)
        padded_attention_mask[:, : input_ids.shape[1]] = attention_mask

        # Padded position_ids (bucket_size=7); e.g.,
        # [[0, 1, 2, 0, 0, 0, 0], [1, 0, 1, 0, 0, 0, 0]]
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids.masked_fill_(attention_mask == 0, 1)
        padded_position_ids = torch.zeros((batch_size, self.bucket_size - 1), dtype=torch.int64)
        padded_position_ids[:, : input_ids.shape[1]] = position_ids

        return padded_inputs, padded_attention_mask, padded_position_ids

    def decode_inputs(self, attention_mask, past_key_values, next_tokens, sequence_idx):
        batch_size = attention_mask.shape[0]
        # Update 1 to the existing attention_mask at the specific; e.g.,
        # [[1, 1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0]] -> [[1, 1, 1, 1, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0]]  # noqa: E501
        attention_mask[:, sequence_idx] += attention_mask.new_ones(batch_size)

        # Create position_ids on the fly for batch generation
        # attention_masks [[1, 1, 1, 1, 0, 0, 0], [0, 1, 1, 1, 0, 0, 0]] -> position_ids [[3], [2]]
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids = position_ids[:, -1:]

        return next_tokens[:, None], attention_mask, position_ids, past_key_values


class PreAllocatedConcatGenerator(PreAllocatedGenerator):
    def __init__(
        self,
        model: PreTrainedModel,
        bucket_size: int,
        **kwargs,
    ) -> None:
        super().__init__(model, bucket_size, **kwargs)

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

        # Create position_ids on the fly for batch generation; e.g.,
        # attention_masks [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]] -> position_ids [[3], [2]]  # noqa: E501
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids = position_ids[:, -1:]

        return next_tokens[:, None], attention_mask, position_ids, past_key_values

    def handle_outputs(self, outputs, past_key_values, sequence_idx, is_prefill_phase):
        # SUPPORTED_GENERATION_RETURN_DICT_TYPES[1],
        # i.e., CausalLMOutputWithCrossAttentions is not yet checked.
        if isinstance(outputs, SUPPORTED_GENERATION_RETURN_DICT_TYPES[0]):
            outputs = outputs.to_tuple()
        elif isinstance(outputs, tuple):
            pass
        else:
            ValueError(f"Unsupported generation output type: {type(outputs)}")

        logits, new_key_values = outputs
        new_keys, new_values = tuple(zip(*new_key_values))

        n_layer = self.model.config.n_layer
        n_head = self.model.config.n_head
        batch_size = logits.shape[0]

        if is_prefill_phase:
            # the prefill forward returns the past_key_values via new_keys and new_values.
            # Both new_keys and new_values have the shape:
            #     [batch_size, n_head, bucket_size - 1, hidden_size].
            # Preallocated Concat version uses the last sequence of past_key_values to concat
            # temporarily new key, values in order to compute the new attention score.
            # That's why the sequence length of past_key_values must be bucket_size - 1.
            past_key_values = [(key, value) for key, value in zip(new_keys, new_values)]
            return logits, past_key_values
        else:
            # new_keys and new_values have only newly computed result,
            # so its shape is [batch_size, n_head, 1, hidden_size].
            # past_key_values has the same shape: [batch_size, n_head, bucket_size - 1, hidden_size]
            for layer_idx in range(n_layer):
                past_keys, past_values = past_key_values[layer_idx]
                past_keys[:, :, sequence_idx, :] = new_keys[layer_idx].reshape(
                    batch_size, n_head, -1
                )
                past_values[:, :, sequence_idx, :] = new_values[layer_idx].reshape(
                    batch_size, n_head, -1
                )

        return logits, past_key_values
