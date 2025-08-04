import copy
import logging
from typing import Dict

from transformers import PreTrainedModel
from transformers.generation.configuration_utils import GenerationConfig


class GenerationConfigHelper:
    def __init__(self, model: PreTrainedModel, logger: logging.Logger) -> None:
        self.model_config = model.config
        self.generation_config = model.generation_config
        self.logger = logger

    # Prepare the generation configuration
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1263-L1279
    def prepare_generation_config(self, generation_config: GenerationConfig) -> GenerationConfig:
        if generation_config is None:
            if getattr(self.generation_config, "_from_model_config", True):
                new_generation_config = GenerationConfig.from_model_config(self.model_config)
                if new_generation_config != self.generation_config:
                    self.logger.warning(
                        "You have modified the pretrained model configuration to control \
                            generation."
                        "This is a deprecated strategy and will be removed soon. "
                        "Please use a generation configuration file."
                    )
                    self.generation_config = new_generation_config
            generation_config = self.generation_config

        generation_config.validate()
        return copy.deepcopy(generation_config)

    # Set the pad_token_id for generation
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1288-L1298
    def set_pad_token_id(self, generation_config: GenerationConfig, kwargs: Dict) -> None:
        if generation_config.pad_token_id is None and generation_config.eos_token_id is not None:
            if "attention_mask" not in kwargs:
                raise ValueError(
                    "The attention mask and the pad token id were not set. Please pass your input's\
                         `attention_mask`."
                )
            generation_config.pad_token_id = (
                generation_config.eos_token_id[0]
                if isinstance(generation_config.eos_token_id, list)
                else generation_config.eos_token_id
            )
            self.logger.warning(
                f"Setting `pad_token_id` to `eos_token_id`: {generation_config.pad_token_id} for \
                    open-end generation."
            )

    # Set the max_length for generation
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1365-L1383
    def set_max_length(
        self, generation_config: GenerationConfig, input_ids_length: int, kwargs: Dict
    ) -> None:
        if generation_config.max_length and generation_config.max_new_tokens is None:
            self.logger.warning(
                "Using `max_length`'s default to control the generation length is deprecated. Use \
                    `max_new_tokens` instead."
            )
        elif generation_config.max_new_tokens is not None:
            if kwargs.get("max_length") is not None:
                self.logger.warning(
                    "Both `max_new_tokens` and `max_length` are set. `max_new_tokens` will take \
                        precedence."
                )
            generation_config.max_length = generation_config.max_new_tokens + input_ids_length

    # Check if the min/max generation length is valid
    # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1385-L1396
    def check_generation_length(
        self, generation_config: GenerationConfig, input_ids_length: int
    ) -> None:
        if (
            generation_config.min_length
            and generation_config.min_length > generation_config.max_length
        ):
            raise ValueError(
                "Unfeasible length constraints: the minimum length is larger than the maximum \
                    length."
            )

        if input_ids_length >= generation_config.max_length:
            raise ValueError(
                "Input length of input_ids is too long. Consider increasing `max_new_tokens`."
            )
