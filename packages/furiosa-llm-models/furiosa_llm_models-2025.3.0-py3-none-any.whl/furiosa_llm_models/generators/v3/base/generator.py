import abc
import logging
from typing import Any, Dict, Optional, Tuple, Union

import torch
from transformers import PretrainedConfig, PreTrainedModel
from transformers.generation.configuration_utils import GenerationConfig
from transformers.generation.logits_process import LogitsProcessorList
from transformers.generation.stopping_criteria import (
    StoppingCriteriaList,
)
from transformers.generation.utils import (
    BeamSearchScorer,
    GenerateOutput,
)

from ..generation_utils import (
    block_unsupported_features,
    determine_generation_mode,
    expand_inputs_for_generation,
    prepare_decoder_only_model_inputs,
)
from ..helper import GenerationConfigHelper
from ..processor import get_logits_processor, get_stopping_criteria

logger = logging.getLogger(__name__)


class BaseGenerator(abc.ABC):
    """
    Abstract base class for all generator models.

    This class defines the interface that all generator models must implement. It serves as a template for
    creating custom generator classes for different model architectures.

    Methods:
        generate(inputs=None, generation_config=None, logits_processor=None, stopping_criteria=None, **kwargs):
            Abstract method to generate sequences of token ids. Must be implemented by subclasses.

    Abstract Methods:
        generate(inputs: Optional[torch.Tensor] = None,
                 generation_config: Optional[GenerationConfig] = None,
                 logits_processor: Optional[LogitsProcessorList] = None,
                 stopping_criteria: Optional[StoppingCriteriaList] = None,
                 **kwargs) -> Union[GenerateOutput, torch.LongTensor]:
            Generate sequences of token ids based on the provided inputs and generation configuration.
            Subclasses must implement this method.
    """  # noqa

    @abc.abstractmethod
    def generate(
        self,
        inputs: Optional[torch.Tensor] = None,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        **kwargs,
    ) -> Union[GenerateOutput, torch.LongTensor]:
        pass


class GeneratorForDecoderOnlyModels(BaseGenerator):
    unsupported_features = [
        "prefix_allowed_tokens_fn",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1167
        "synced_gpus",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1168
        "assistant_model",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1169
        "streamer",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1170
    ]
    unsupported_generation_kwargs = [
        "input_embeds",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L533-L554
        "token_type_ids",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L765-L768
        "output_attentions",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1311
        "output_hidden_states",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1312
        "output_scores",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1544
        "standardize_cache_format",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L756
        "state",  # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L762-L763
    ]

    """
    Base class generator for decoder-only models.
    This class contains only code for decoder-only models, excluding any code related to encoder-decoder models.

    Attributes:
        model (PreTrainedModel): The pretrained model to use for generation.
        model_config (PretrainedConfig): The configuration of the model.
        gen_cfg_helper (GenerationConfigHelper): Helper class for generation configuration.

    Methods:
        generate(inputs=None, generation_config=None, logits_processor=None, stopping_criteria=None, **kwargs):
            Generate sequences of token ids for the given input tensor and configuration.

        _generate(input_ids, generation_config, logits_processor, stopping_criteria, generation_mode, **model_kwargs):
            Internal method to handle the generation logic based on the generation mode.

        _greedy_search(input_ids, logits_processor=None, stopping_criteria=None, max_length=None, pad_token_id=None, eos_token_id=None, output_scores=None, return_dict_in_generate=None, **model_kwargs):
            Generate sequences using greedy search.

        _beam_search(input_ids, beam_scorer, logits_processor=None, stopping_criteria=None, max_length=None, pad_token_id=None, eos_token_id=None, output_scores=None, return_dict_in_generate=None, **model_kwargs):
            Generate sequences using beam search.

        prepare_inputs_for_generation(input_ids, **model_kwargs):
            Abstract method to prepare inputs for generation.

        _update_model_kwargs_for_generation(outputs, model_kwargs):
            Abstract method to update model kwargs during generation.

    Notes:
        This class does not support the following features:
            - "prefix_allowed_tokens_fn"
            - "synced_gpus"
            - "assistant_model"
            - "streamer"

        Any code related to these features is excluded.
    """  # noqa

    def __init__(
        self,
        model: PreTrainedModel,
        generation_config_helper: Optional[GenerationConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        self.model = model
        self.model_config: PretrainedConfig = model.config
        logger = logger or logging.getLogger(__name__)
        self.gen_cfg_helper = generation_config_helper or GenerationConfigHelper(
            model, logger=logger
        )

    @torch.no_grad()
    def generate(
        self,
        inputs: Optional[torch.Tensor] = None,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        **kwargs: Dict,
    ) -> Union[GenerateOutput, torch.LongTensor]:
        (
            input_ids,
            generation_config,
            logits_processor,
            stopping_criteria,
            generation_mode,
            model_kwargs,
        ) = self._prepare(inputs, generation_config, logits_processor, stopping_criteria, **kwargs)

        return self._generate(
            input_ids,
            generation_config,
            logits_processor,
            stopping_criteria,
            generation_mode,
            **model_kwargs,
        )

    def _prepare(
        self,
        inputs: Optional[torch.Tensor] = None,
        generation_config: Optional[GenerationConfig] = None,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        **kwargs: Dict,
    ) -> Tuple[
        torch.Tensor,
        GenerationConfig,
        LogitsProcessorList,
        StoppingCriteriaList,
        str,
        Dict[str, Any],
    ]:
        # Block unsupported arguments
        block_unsupported_features(
            unsupported_keys=self.unsupported_features,
            **kwargs,
        )

        # Prepare the generation configuration
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1264-L1277
        generation_config = generation_config or self.gen_cfg_helper.prepare_generation_config(
            generation_config
        )

        # Update model kwargs based on generation configuration
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1280
        model_kwargs = generation_config.update(**kwargs)

        # Handle inputs.
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1300-L1307
        input_ids, model_kwargs = prepare_decoder_only_model_inputs(
            self.model.main_input_name, inputs, **model_kwargs
        )

        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1318
        model_kwargs["use_cache"] = generation_config.use_cache

        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1375-L1383
        model_kwargs["max_new_tokens"] = generation_config.max_new_tokens

        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1467-L1476
        if self.model.device != input_ids.device:
            raise ValueError(
                f"`input_ids` are on {input_ids.device} but the model is on {self.model.device}. "
                "Please move the input IDs to {self.model.device}."
            )

        # Set pad_token_id and max_length
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1288-L1298
        self.gen_cfg_helper.set_pad_token_id(generation_config, model_kwargs)
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1365-L1383
        self.gen_cfg_helper.set_max_length(generation_config, input_ids.shape[-1], model_kwargs)

        # Check generation length
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1385-L1396
        self.gen_cfg_helper.check_generation_length(generation_config, input_ids.shape[-1])

        # Get logits processor and stopping criteria
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1478-L1485
        logits_processor = get_logits_processor(
            generation_config, input_ids.shape[-1], input_ids, logits_processor=logits_processor
        )

        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1487-L1490
        stopping_criteria = get_stopping_criteria(
            generation_config,
            max_position_embeddings=getattr(self.model_config, "max_position_embeddings", None),
            stopping_criteria=stopping_criteria,
        )

        # Determine generation mode
        # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L1398-L1460
        generation_mode = determine_generation_mode(generation_config)

        return (
            input_ids,
            generation_config,
            logits_processor,
            stopping_criteria,
            generation_mode,
            model_kwargs,
        )

    def _generate(
        self,
        input_ids: torch.Tensor,
        generation_config: Optional[GenerationConfig],
        logits_processor: Optional[LogitsProcessorList],
        stopping_criteria: Optional[StoppingCriteriaList],
        generation_mode: Optional[str],
        **model_kwargs: Dict,
    ) -> Union[GenerateOutput, torch.LongTensor]:
        """
        Notes: The following generation kwargs are not supported:
            - "output_attentions"
            - "output_hidden_states"
            - "output_scores"
            - "synced_gpus"
            - "streamer"
            - "token_type_ids"

        Any code related to these kwargs is excluded.
        """
        block_unsupported_features(
            unsupported_keys=self.unsupported_generation_kwargs,
            **model_kwargs,
        )

        logits_processor = logits_processor or LogitsProcessorList()
        stopping_criteria = stopping_criteria or StoppingCriteriaList()
        max_length = generation_config.max_length or self.model.config.max_length
        pad_token_id = (
            generation_config.pad_token_id
            if generation_config.pad_token_id is not None
            else self.model.config.pad_token_id
        )
        eos_token_id = (
            generation_config.eos_token_id
            if generation_config.eos_token_id is not None
            else self.model.config.eos_token_id
        )
        return_dict_in_generate = (
            generation_config.return_dict_in_generate or self.model.config.return_dict_in_generate
        )

        if generation_mode == "greedy_search":
            if generation_config.num_return_sequences > 1:
                raise ValueError("num_return_sequences has to be 1 when doing greedy search.")
            return self._greedy_search(
                input_ids,
                logits_processor=logits_processor,
                stopping_criteria=stopping_criteria,
                max_length=max_length,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                return_dict_in_generate=return_dict_in_generate,
                **model_kwargs,
            )
        elif generation_mode == "beam_search":
            if generation_config.num_return_sequences > generation_config.num_beams:
                raise ValueError(
                    "`num_return_sequences` has to be smaller or equal to `num_beams`."
                )
            if stopping_criteria.max_length is None:
                raise ValueError("`max_length` needs to be a stopping_criteria for now.")
            beam_scorer = BeamSearchScorer(
                batch_size=input_ids.shape[0],
                num_beams=generation_config.num_beams,
                device=input_ids.device,
                length_penalty=generation_config.length_penalty,
                do_early_stopping=generation_config.early_stopping,
                num_beam_hyps_to_keep=generation_config.num_return_sequences,
                max_length=generation_config.max_length,
            )
            input_ids, model_kwargs = expand_inputs_for_generation(
                input_ids=input_ids, expand_size=generation_config.num_beams, **model_kwargs
            )
            return self._beam_search(
                input_ids,
                beam_scorer=beam_scorer,
                logits_processor=logits_processor,
                stopping_criteria=stopping_criteria,
                max_length=max_length,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                return_dict_in_generate=return_dict_in_generate,
                **model_kwargs,
            )
        else:
            raise ValueError(f"Unsupported generation mode: {generation_mode}.")
