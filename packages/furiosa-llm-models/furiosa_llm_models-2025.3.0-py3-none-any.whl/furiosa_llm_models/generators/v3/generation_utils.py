from typing import Any, Dict, List, Optional, Tuple, Union

import torch
from transformers.generation.configuration_utils import GenerationConfig


# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1300-L1307
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L500-L562
def prepare_decoder_only_model_inputs(
    input_name: str, inputs: Optional[torch.Tensor] = None, **model_kwargs: Dict
) -> Tuple[torch.Tensor, Dict]:
    # Ensure the model's main input name is 'input_ids'.
    # Currently, DecoderOnlyGenerator supports only 'input_ids' as the main input.
    if input_name != "input_ids":
        raise ValueError(
            "The model's main input name is not 'input_ids'. Currently, we only support "
            "`DecoderOnlyGenerator` with 'input_ids' as the main input."
        )

    # Remove entries from model_kwargs where the value is None, except for the main input name.
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L520
    model_kwargs = {k: v for k, v in model_kwargs.items() if v is not None}

    # Extract input tensor from model_kwargs if available, ensuring it's not passed alongside inputs. # noqa
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L524-L531
    inputs_kwarg = model_kwargs.pop(input_name, None)
    if inputs_kwarg is not None and inputs is not None:
        raise ValueError(
            f"`inputs`: {inputs}` were passed alongside {input_name} which is not allowed. "
            f"Make sure to either pass `inputs` or `{input_name}=...`, not both."
        )
    if inputs_kwarg is not None:
        inputs = inputs_kwarg

    # Ensure 'input_embeds' is not present in model_kwargs.
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L533-L558
    if "input_embeds" in model_kwargs:
        raise ValueError("`input_embeds` is not allowed as a `model_kwargs` argument.")

    # Always return 'input_ids' in this case.
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1360
    input_ids = inputs

    return input_ids, model_kwargs


# Expand input tensors and model kwargs for beam search
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L709-L734
def expand_inputs_for_generation(
    expand_size: int = 1, input_ids: Optional[torch.LongTensor] = None, **model_kwargs
) -> Tuple[torch.LongTensor, Dict[str, Any]]:
    # Helper function to expand the tensors in the dictionary
    def _expand_dict_for_generation(dict_to_expand):
        for key, value in dict_to_expand.items():
            if value is not None and isinstance(value, torch.Tensor):
                dict_to_expand[key] = value.repeat_interleave(expand_size, dim=0)
        return dict_to_expand

    if input_ids is not None:
        input_ids = input_ids.repeat_interleave(expand_size, dim=0)
    model_kwargs = _expand_dict_for_generation(model_kwargs)

    return input_ids, model_kwargs


# Determine generation mode based on the generation configuration
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1398-L1460
def determine_generation_mode(generation_config: GenerationConfig) -> str:
    is_constraint_gen_mode = (
        generation_config.constraints is not None or generation_config.force_words_ids is not None
    )
    is_contrastive_search_gen_mode = (
        generation_config.num_beams == 1
        and generation_config.top_k
        and generation_config.top_k > 1
        and not generation_config.do_sample
        and generation_config.penalty_alpha
        and generation_config.penalty_alpha > 0
    )
    is_greedy_gen_mode = (
        generation_config.num_beams == 1
        and generation_config.num_beam_groups == 1
        and not generation_config.do_sample
        and not is_constraint_gen_mode
        and not is_contrastive_search_gen_mode
    )
    is_beam_gen_mode = (
        generation_config.num_beams > 1
        and generation_config.num_beam_groups == 1
        and not generation_config.do_sample
        and not is_constraint_gen_mode
        and not is_contrastive_search_gen_mode
    )

    if generation_config.num_beam_groups > generation_config.num_beams:
        raise ValueError("`num_beam_groups` must be smaller or equal to `num_beams`")

    if is_greedy_gen_mode:
        return "greedy_search"
    elif is_beam_gen_mode:
        return "beam_search"
    else:
        raise ValueError("Unsupported generation mode.")


# Block unsupported keyword arguments
# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1167-L1170
def block_unsupported_features(unsupported_keys, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
    for key in unsupported_keys:
        if kwargs.get(key) is not None:
            raise ValueError(f"`{key}` is not supported.")


def bucketize_inputs(
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    bucket_size: Union[int, List[int]],
    pad_token_id: int,
    position_ids: Optional[torch.Tensor] = None,
    **kwargs,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
    """
    Bucketize input tensors to a fixed bucket size by padding the input IDs, attention mask,
    and position IDs. This ensures uniform tensor sizes for batch processing.

    Args:
        input_ids (torch.Tensor): Input IDs tensor of shape (batch_size, input_ids_length).
        attention_mask (torch.Tensor): Attention mask tensor of shape (batch_size, input_ids_length).
        position_ids (Optional[torch.Tensor]): Position IDs tensor of shape (batch_size, input_ids_length).
            If None, position IDs will be generated based on the attention mask.
        bucket_size (Union[int, List[int]]): The fixed bucket size for padding. Only a single integer is supported.
        pad_token_id (int): The token ID used for padding.
        **kwargs: Additional keyword arguments.

    Returns:
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
            - bucketized_input_ids (torch.Tensor): Padded input IDs tensor of shape (batch_size, bucket_size).
            - bucketized_attention_mask (torch.Tensor): Padded attention mask tensor of shape (batch_size, bucket_size).
            - bucketized_position_ids (torch.Tensor): Padded position IDs tensor of shape (batch_size, bucket_size).
            - input_ids_length (int): The original sequence length.

    Raises:
        NotImplementedError: If `bucket_size` is not an integer.
        AssertionError: If `attention_mask` is None.
    """  # noqa
    if not isinstance(bucket_size, int):
        raise NotImplementedError("Bucketization for multiple bucket sizes is not supported.")

    assert attention_mask is not None, "attention_mask is required for bucketization"
    batch_size, input_ids_length = input_ids.shape

    if position_ids is None:
        position_ids = attention_mask.long().cumsum(-1) - 1
        position_ids.masked_fill_(attention_mask == 0, 1)

    bucketized_attention_mask = torch.zeros((batch_size, bucket_size), dtype=torch.int)
    bucketized_attention_mask[:, :input_ids_length] = attention_mask

    bucketized_input_ids = torch.full(
        (batch_size, bucket_size), fill_value=pad_token_id, dtype=torch.int
    )
    bucketized_input_ids[:, :input_ids_length] = input_ids

    bucketized_position_ids = torch.zeros((batch_size, bucket_size), dtype=torch.long)
    bucketized_position_ids[:, :input_ids_length] = position_ids

    return (
        bucketized_input_ids,
        bucketized_attention_mask,
        bucketized_position_ids,
        input_ids_length,
    )
