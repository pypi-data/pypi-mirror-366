import logging
from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from torch import nn
from transformers.generation.beam_search import BeamScorer
from transformers.generation.logits_process import LogitsProcessorList
from transformers.generation.stopping_criteria import (
    StoppingCriteriaList,
    validate_stopping_criteria,
)
from transformers.generation.utils import (
    BeamSearchDecoderOnlyOutput,
    BeamSearchOutput,
    GreedySearchDecoderOnlyOutput,
    GreedySearchOutput,
)
from transformers.utils import ModelOutput

from ..base import GeneratorForDecoderOnlyModels

logger = logging.getLogger(__name__)


class Generator(GeneratorForDecoderOnlyModels):
    # Greedy search for generation
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2194-L2451
    def _greedy_search(
        self,
        input_ids: torch.LongTensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ) -> Union[GreedySearchOutput, torch.LongTensor]:
        logits_processor = logits_processor or LogitsProcessorList()
        stopping_criteria = stopping_criteria or StoppingCriteriaList()

        if max_length is not None:
            logger.warning(
                "`max_length` is deprecated in this function, use "
                "`stopping_criteria=StoppingCriteriaList([MaxLengthCriteria(max_length=max_length)])`\
                      instead."
            )
            stopping_criteria = validate_stopping_criteria(stopping_criteria, max_length)

        pad_token_id = pad_token_id or self.model.generation_config.pad_token_id
        eos_token_id = eos_token_id or self.model.generation_config.eos_token_id
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]
        eos_token_id_tensor = (
            torch.tensor(eos_token_id).to(input_ids.device) if eos_token_id is not None else None
        )

        return_dict_in_generate = (
            return_dict_in_generate or self.model.generation_config.return_dict_in_generate
        )

        scores = None
        unfinished_sequences = torch.ones(
            input_ids.shape[0], dtype=torch.long, device=input_ids.device
        )

        while True:
            model_inputs = self._prepare_inputs_for_generation(input_ids, **model_kwargs)
            outputs = self.model(**model_inputs, return_dict=True)

            next_token_logits = outputs.logits[:, -1, :]
            next_tokens_scores = logits_processor(input_ids, next_token_logits)
            next_tokens = torch.argmax(next_tokens_scores, dim=-1)

            if eos_token_id is not None:
                if pad_token_id is None:
                    raise ValueError(
                        "If `eos_token_id` is defined, make sure that `pad_token_id` is defined."
                    )
                next_tokens = next_tokens * unfinished_sequences + pad_token_id * (
                    1 - unfinished_sequences
                )

            input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs)

            # if eos_token was found in one sentence, set sentence to finished
            if eos_token_id_tensor is not None:
                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )
                if unfinished_sequences.max() == 0:
                    break

            if stopping_criteria(input_ids, scores):
                break

        if return_dict_in_generate:
            return GreedySearchDecoderOnlyOutput(sequences=input_ids, scores=scores)
        else:
            return input_ids

    # Beam search for generation
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2735-L3056
    def _beam_search(
        self,
        input_ids: torch.LongTensor,
        beam_scorer: BeamScorer,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[Union[int, List[int]]] = None,
        return_dict_in_generate: Optional[bool] = None,
        **model_kwargs,
    ) -> Union[BeamSearchOutput, torch.LongTensor]:
        logits_processor = logits_processor or LogitsProcessorList()
        stopping_criteria = stopping_criteria or StoppingCriteriaList()

        if max_length is not None:
            logger.warning(
                "`max_length` is deprecated in this function, use "
                "`stopping_criteria=StoppingCriteriaList(MaxLengthCriteria(max_length=max_length))`\
                      instead."
            )
            stopping_criteria = validate_stopping_criteria(stopping_criteria, max_length)

        pad_token_id = pad_token_id or self.model.generation_config.pad_token_id
        eos_token_id = eos_token_id or self.model.generation_config.eos_token_id
        if isinstance(eos_token_id, int):
            eos_token_id = [eos_token_id]

        return_dict_in_generate = (
            return_dict_in_generate or self.model.generation_config.return_dict_in_generate
        )

        batch_size = len(beam_scorer._beam_hyps)
        num_beams = beam_scorer.num_beams
        batch_beam_size, cur_len = input_ids.shape
        # if model_kwargs.get("input_ids_length"):
        #     cur_len = model_kwargs["input_ids_length"]

        if num_beams * batch_size != batch_beam_size:
            raise ValueError(
                f"Batch dimension of `input_ids` should be {num_beams * batch_size}, but \
                    is {batch_beam_size}."
            )

        beam_scores = torch.zeros(
            (batch_size, num_beams), dtype=torch.float, device=input_ids.device
        )
        beam_scores[:, 1:] = -1e9
        beam_scores = beam_scores.view((batch_size * num_beams,))
        scores = None
        beam_indices = None

        while True:
            model_inputs = self._prepare_inputs_for_generation(input_ids, **model_kwargs)
            outputs = self.model(**model_inputs, return_dict=True)

            next_token_logits = outputs.logits[:, -1, :]
            # hack: adjust tokens for Marian. For Marian we have to make sure that the `pad_token_id` # noqa
            # cannot be generated both before and after the `nn.functional.log_softmax` operation.
            next_token_logits = self.adjust_logits_during_generation(
                next_token_logits, cur_len=cur_len
            )
            next_token_scores = nn.functional.log_softmax(next_token_logits, dim=-1)

            next_token_scores_processed = logits_processor(input_ids, next_token_scores)
            next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                next_token_scores
            )

            vocab_size = next_token_scores.shape[-1]
            next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

            # Sample 2 next tokens for each beam (so we have some spare tokens and match output of
            # beam search)
            next_token_scores, next_tokens = torch.topk(
                next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
            )
            next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
            next_tokens = next_tokens % vocab_size

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
            beam_next_tokens = beam_outputs["next_beam_tokens"]
            beam_idx = beam_outputs["next_beam_indices"]

            input_ids = torch.cat([input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1)
            model_kwargs = self._update_model_kwargs_for_generation(outputs, model_kwargs)
            if model_kwargs.get("past_key_values") is not None:
                model_kwargs["past_key_values"] = self._reorder_cache_alignment(
                    model_kwargs["past_key_values"], beam_idx
                )

            cur_len = cur_len + 1
            if beam_scorer.is_done or stopping_criteria(input_ids, scores):
                break

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

        if return_dict_in_generate:
            return BeamSearchDecoderOnlyOutput(
                sequences=sequence_outputs["sequences"],
                sequences_scores=sequence_outputs["sequence_scores"],
                scores=scores,
                beam_indices=sequence_outputs["beam_indices"],
            )
        else:
            return sequence_outputs["sequences"]

    def _prepare_inputs_for_generation(
        self, input_ids: torch.Tensor, **kwargs: Any
    ) -> Dict[str, Any]:
        is_prefill: bool = kwargs.get("is_prefill", True)
        if is_prefill:
            return self._prepare_prefill_inputs_for_generation(input_ids, **kwargs)
        else:
            return self._prepare_decode_inputs_for_generation(input_ids, **kwargs)

    def _prepare_prefill_inputs_for_generation(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        position_ids: Optional[torch.Tensor] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        # Example:
        # input_ids = torch.tensor([[1, 2, 3, 4], [5, 6, 7, 8]])
        # attention_mask = torch.tensor([[1.0, 1.0, 1.0, 1.0], [1.0, 1.0, 1.0, 0.0]])
        #
        # Step-by-step:
        # 1. Convert attention_mask to long type:
        #    attention_mask.long()
        #    tensor([[1, 1, 1, 1], [1, 1, 1, 0]])
        #
        # 2. Generate cumulative sum along the last dimension:
        #    attention_mask.long().cumsum(-1)
        #    tensor([[1, 2, 3, 4], [1, 2, 3, 3]])
        #
        # 3. Subtract 1 to start positions from 0:
        #    attention_mask.long().cumsum(-1) - 1
        #    tensor([[0, 1, 2, 3], [0, 1, 2, 2]])
        #
        # 4. Mask positions where attention_mask is 0:
        #    position_ids.masked_fill_(attention_mask == 0, 1)
        #    tensor([[0, 1, 2, 3], [0, 1, 2, 1]])
        #
        # Resulting position_ids:
        # tensor([[0, 1, 2, 3],
        #         [0, 1, 2, 1]])

        # create position_ids on the fly for batch generation
        if position_ids is None:
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)

        return {
            "input_ids": input_ids,
            "past_key_values": None,
            "use_cache": kwargs.get("use_cache"),
            "position_ids": position_ids,
            "attention_mask": attention_mask,
        }

    def _prepare_decode_inputs_for_generation(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        position_ids: Optional[torch.Tensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        # Example:
        # past_key_values simulates cached key and value states from a previous generation step
        # past_key_values = (
        #     (
        #         torch.tensor([[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]]),  # Shape: (1, 3, 2)
        #         torch.tensor([[[0.7, 0.8], [0.9, 1.0], [1.1, 1.2]]])   # Shape: (1, 3, 2)
        #     ),
        # )
        # input_ids = torch.tensor([[101, 102, 103, 104, 105, 106, 107]])  # Shape: (1, 7)
        # attention_mask = torch.tensor([[1., 1., 1., 1., 1., 1., 1.]])  # Shape: (1, 7)
        #
        # past_length = past_key_values[0][0].shape[2]
        # The shape of past_key_values[0][0] is (1, 3, 2), so past_length will be 3

        assert past_key_values is not None, "`past_key_values` is required for decoding."
        past_length: int = past_key_values[0][0].shape[2]
        if not input_ids.shape[1] > past_length:
            raise ValueError(
                f"We don't handle the case where `input_ids` length is less than or equal to \
                    `past_length`. "
                f"`input_ids` length: {input_ids.shape[1]}, `past_length`: {past_length}"
            )
        # The resulting input_ids will be:
        # tensor([[104, 105, 106, 107]])
        input_ids = input_ids[:, past_length:]

        if position_ids is None:
            # Resulting position_ids:
            # tensor([[0, 1, 2, 3, 4, 5, 6]])
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)

        # The resulting position_ids will be:
        # tensor([[3, 4, 5, 6]])
        position_ids = position_ids[:, -input_ids.shape[1] :]

        return {
            "input_ids": input_ids,
            "past_key_values": past_key_values,
            "use_cache": kwargs.get("use_cache"),
            "position_ids": position_ids,
            "attention_mask": attention_mask,
        }

    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L751-L786
    def _update_model_kwargs_for_generation(
        self,
        outputs: ModelOutput,
        model_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        # update past_key_values
        model_kwargs["is_prefill"] = False
        model_kwargs["past_key_values"] = outputs.past_key_values

        # Example:
        # Initial attention_mask:
        # tensor([
        #     [1.0, 1.0, 1.0, 1.0, 1.0],
        #     [0.0, 0.0, 1.0, 1.0, 1.0]
        # ])
        #
        # 1. Create a new column of ones with the same batch size:
        # attention_mask.new_ones((attention_mask.shape[0], 1), dtype=torch.float)
        # tensor([
        #     [1.0],
        #     [1.0]
        # ])
        #
        # 2. Concatenate the new column of ones to the existing attention_mask along the last dimension: # noqa
        # torch.cat([attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1), dtype=torch.float)], dim=-1) # noqa
        # tensor([
        #     [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        #     [0.0, 0.0, 1.0, 1.0, 0.0, 1.0]
        # ])
        attention_mask = model_kwargs["attention_mask"]
        model_kwargs["attention_mask"] = torch.cat(
            [attention_mask, attention_mask.new_ones((attention_mask.shape[0], 1))], dim=-1
        )
        return model_kwargs

    # https://github.com/huggingface/transformers/blob/main/src/transformers/models/gptj/modeling_gptj.py#L1174-L1186
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/models/llama/modeling_llama.py#L882-L889
    @staticmethod
    def _reorder_cache_alignment(
        past_key_values: Tuple[Tuple[torch.Tensor]], beam_indices: torch.Tensor
    ) -> Tuple[Tuple[torch.Tensor]]:
        """
        Reorders the `past_key_values` to match the beam indices (`beam_indices`) during beam search.

        This ensures that the past key and value states are correctly aligned with
        the selected beams at each generation step.

        Args:
            past_key_values (Tuple[Tuple[torch.Tensor]]): Cached key and value states from previous steps.
            beam_indices (torch.Tensor): Indices specifying the new order of beams.

        Returns:
            Tuple[Tuple[torch.Tensor]]: Reordered past key and value states.

        Example:
            >>> past_key_values = (
            ...     (torch.tensor([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]), torch.tensor([[0.7, 0.8], [0.9, 1.0], [1.1, 1.2]])),
            ...     (torch.tensor([[1.3, 1.4], [1.5, 1.6], [1.7, 1.8]]), torch.tensor([[1.9, 2.0], [2.1, 2.2], [2.3, 2.4]]))
            ... )
            >>> beam_indices = torch.tensor([2, 0, 1])
            >>> reordered = Generator._reorder_cache_alignment(past_key_values, beam_indices)
            >>> reordered
            (
                (torch.tensor([[0.5, 0.6], [0.1, 0.2], [0.3, 0.4]]), torch.tensor([[1.1, 1.2], [0.7, 0.8], [0.9, 1.0]])),
                (torch.tensor([[1.7, 1.8], [1.3, 1.4], [1.5, 1.6]]), torch.tensor([[2.3, 2.4], [1.9, 2.0], [2.1, 2.2]]))
            )
        """  # noqa
        return tuple(
            tuple(cache.index_select(0, beam_indices.to(cache.device)) for cache in layer_cache)
            for layer_cache in past_key_values
        )

    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L564-L568
    def adjust_logits_during_generation(
        self, logits: torch.FloatTensor, **kwargs
    ) -> torch.FloatTensor:
        """
        Implement in subclasses of [`PreTrainedModel`] for custom behavior to adjust the logits in \
            the generate method.
        """
        return logits
