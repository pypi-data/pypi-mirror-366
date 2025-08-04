from typing import Optional, Union

import torch
from transformers.generation.configuration_utils import GenerationConfig
from transformers.generation.logits_process import (
    ClassifierFreeGuidanceLogitsProcessor,
    EncoderNoRepeatNGramLogitsProcessor,
    EncoderRepetitionPenaltyLogitsProcessor,
    ExponentialDecayLengthPenalty,
    ForcedBOSTokenLogitsProcessor,
    ForcedEOSTokenLogitsProcessor,
    HammingDiversityLogitsProcessor,
    InfNanRemoveLogitsProcessor,
    LogitNormalization,
    LogitsProcessorList,
    MinLengthLogitsProcessor,
    MinNewTokensLengthLogitsProcessor,
    NoBadWordsLogitsProcessor,
    NoRepeatNGramLogitsProcessor,
    RepetitionPenaltyLogitsProcessor,
    SequenceBiasLogitsProcessor,
    SuppressTokensAtBeginLogitsProcessor,
    SuppressTokensLogitsProcessor,
)
from transformers.generation.stopping_criteria import (
    MaxLengthCriteria,
    MaxTimeCriteria,
    StoppingCriteria,
    StoppingCriteriaList,
)


# Get logits processor list based on generation configuration
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L832-L950
def get_logits_processor(
    generation_config: GenerationConfig,
    input_ids_length: int,
    encoder_input_ids: torch.LongTensor,
    logits_processor: Optional[LogitsProcessorList] = None,
) -> LogitsProcessorList:
    logits_processor = logits_processor or LogitsProcessorList()
    processors = LogitsProcessorList()

    if generation_config.sequence_bias:
        processors.append(
            SequenceBiasLogitsProcessor(sequence_bias=generation_config.sequence_bias)
        )

    if generation_config.diversity_penalty and generation_config.diversity_penalty > 0.0:
        processors.append(
            HammingDiversityLogitsProcessor(
                diversity_penalty=generation_config.diversity_penalty,
                num_beams=generation_config.num_beams,
                num_beam_groups=generation_config.num_beam_groups,
            )
        )

    if (
        generation_config.encoder_repetition_penalty
        and generation_config.encoder_repetition_penalty != 1.0
    ):
        processors.append(
            EncoderRepetitionPenaltyLogitsProcessor(
                penalty=generation_config.encoder_repetition_penalty,
                encoder_input_ids=encoder_input_ids,
            )
        )

    if generation_config.repetition_penalty and generation_config.repetition_penalty != 1.0:
        processors.append(
            RepetitionPenaltyLogitsProcessor(penalty=generation_config.repetition_penalty)
        )

    if generation_config.no_repeat_ngram_size and generation_config.no_repeat_ngram_size > 0:
        processors.append(NoRepeatNGramLogitsProcessor(generation_config.no_repeat_ngram_size))

    if (
        generation_config.encoder_no_repeat_ngram_size
        and generation_config.encoder_no_repeat_ngram_size > 0
    ):
        processors.append(
            EncoderNoRepeatNGramLogitsProcessor(
                generation_config.encoder_no_repeat_ngram_size, encoder_input_ids
            )
        )

    if generation_config.bad_words_ids is not None:
        processors.append(
            NoBadWordsLogitsProcessor(
                generation_config.bad_words_ids, generation_config.eos_token_id
            )
        )

    if generation_config.min_length and generation_config.eos_token_id:
        processors.append(
            MinLengthLogitsProcessor(generation_config.min_length, generation_config.eos_token_id)
        )

    if generation_config.min_new_tokens and generation_config.eos_token_id:
        processors.append(
            MinNewTokensLengthLogitsProcessor(
                input_ids_length, generation_config.min_new_tokens, generation_config.eos_token_id
            )
        )

    if generation_config.forced_bos_token_id is not None:
        processors.append(ForcedBOSTokenLogitsProcessor(generation_config.forced_bos_token_id))

    if generation_config.forced_eos_token_id is not None:
        processors.append(
            ForcedEOSTokenLogitsProcessor(
                generation_config.max_length, generation_config.forced_eos_token_id
            )
        )

    if generation_config.remove_invalid_values:
        processors.append(InfNanRemoveLogitsProcessor())

    if generation_config.exponential_decay_length_penalty:
        processors.append(
            ExponentialDecayLengthPenalty(
                generation_config.exponential_decay_length_penalty,
                generation_config.eos_token_id,
                input_ids_length,
            )
        )

    if generation_config.suppress_tokens:
        processors.append(SuppressTokensLogitsProcessor(generation_config.suppress_tokens))

    if generation_config.begin_suppress_tokens:
        begin_index = (
            input_ids_length
            if input_ids_length > 1 or generation_config.forced_bos_token_id is None
            else input_ids_length + 1
        )
        if generation_config.forced_decoder_ids:
            begin_index += generation_config.forced_decoder_ids[-1][0]
        processors.append(
            SuppressTokensAtBeginLogitsProcessor(
                generation_config.begin_suppress_tokens, begin_index
            )
        )

    if generation_config.guidance_scale and generation_config.guidance_scale > 1:
        processors.append(ClassifierFreeGuidanceLogitsProcessor(generation_config.guidance_scale))

    processors = merge_criteria_processor_list(processors, logits_processor)

    # `LogitNormalization` should always be the last logit processor, when present
    if generation_config.renormalize_logits:
        processors.append(LogitNormalization())
    return processors


# Get stopping criteria list based on generation configuration
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L952-L967
def get_stopping_criteria(
    generation_config: GenerationConfig,
    max_position_embeddings: int,
    stopping_criteria: Optional[StoppingCriteriaList] = None,
) -> StoppingCriteriaList:
    stopping_criteria = stopping_criteria or StoppingCriteriaList()
    criteria = StoppingCriteriaList()

    if generation_config.max_length:
        criteria.append(
            MaxLengthCriteria(
                max_length=generation_config.max_length,
                max_position_embeddings=max_position_embeddings,
            )
        )

    if generation_config.max_time:
        criteria.append(MaxTimeCriteria(max_time=generation_config.max_time))

    return merge_criteria_processor_list(criteria, stopping_criteria)


# Merge default and custom criteria/processor lists
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L969-L988
def merge_criteria_processor_list(
    default_list: Union[LogitsProcessorList, StoppingCriteriaList],
    custom_list: Union[LogitsProcessorList, StoppingCriteriaList],
) -> Union[LogitsProcessorList, StoppingCriteriaList]:
    if not custom_list:
        return default_list

    for default in default_list:
        for custom in custom_list:
            if isinstance(custom, type(default)):
                object_type = (
                    "stopping criteria"
                    if isinstance(custom, StoppingCriteria)
                    else "logits processor"
                )
                raise ValueError(
                    f"A custom {object_type} of type {type(custom)} with values {custom} has been \
                        passed to `.generate()`, "
                    f"but it has already been created with the values {default}."
                )

    default_list.extend(custom_list)
    return default_list
