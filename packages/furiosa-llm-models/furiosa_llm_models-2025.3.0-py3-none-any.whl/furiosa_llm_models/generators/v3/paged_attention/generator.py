import logging
from typing import Dict, Optional

from transformers import PreTrainedModel
from transformers.generation.configuration_utils import GenerationConfig

from ..base import GeneratorForDecoderOnlyModels
from .generation_strategy import (
    BeamSearch,
    GreedySearch,
    GreedySearchLeftSlice,
    MLPerfSubmissionBeamSearch,
    MLPerfSubmissionGreedySearch,
    SpecDec,
    SpecDecV2,
)

USE_CACHE = False
logger = logging.getLogger(__name__)


class Generator(GeneratorForDecoderOnlyModels):
    block_size = 1
    max_batch_size = 4

    def __init__(
        self, model: PreTrainedModel, generation_config_helper: Optional[GenerationConfig] = None
    ):
        super().__init__(model, generation_config_helper, logger)
        self.logger = logger
        self._greedy_search = GreedySearch(model)
        self._beam_search = BeamSearch(model)


class MLPerfSubmissionGenerator(GeneratorForDecoderOnlyModels):
    block_size = 1
    max_batch_size = 4

    def __init__(
        self, model: PreTrainedModel, generation_config_helper: Optional[GenerationConfig] = None
    ):
        super().__init__(model, generation_config_helper, logger)
        self.logger = logger
        self._greedy_search = MLPerfSubmissionGreedySearch(model)
        self._beam_search = MLPerfSubmissionBeamSearch(model)


class SpecDecGenerator(GeneratorForDecoderOnlyModels):
    block_size = 1
    max_batch_size = 4

    def __init__(
        self,
        model,
        draft_model,
        sp_len: int,
        non_traced_model=None,
        generation_config_helper: Optional[GenerationConfig] = None,
    ):
        # specdec specific: non_traced_model is only used for initialization of v3 generator.
        if isinstance(model, Dict):
            super().__init__(non_traced_model, generation_config_helper, logger)
        else:
            super().__init__(model, generation_config_helper, logger)
        self.logger = logger
        self._greedy_search = SpecDec(model, draft_model, sp_len)
        # self._beam_search = BeamSearch(model)


class SpecDecGeneratorV2(GeneratorForDecoderOnlyModels):
    block_size = 1
    max_batch_size = 4

    def __init__(
        self,
        model,
        draft_model,
        sp_len: int,
        temperature: float,
        non_traced_model=None,
        generation_config_helper: Optional[GenerationConfig] = None,
    ):
        # specdec specific: non_traced_model is only used for initialization of v3 generator.
        if isinstance(model, Dict):
            super().__init__(non_traced_model, generation_config_helper, logger)
        else:
            super().__init__(model, generation_config_helper, logger)
        self.logger = logger
        self._greedy_search = SpecDecV2(model, draft_model, sp_len, temperature)
        # self._beam_search = BeamSearch(model)


class GeneratorLeftSlice(GeneratorForDecoderOnlyModels):
    block_size = 1
    max_batch_size = 4

    def __init__(
        self, model: PreTrainedModel, generation_config_helper: Optional[GenerationConfig] = None
    ):
        super().__init__(model, generation_config_helper, logger)
        self.logger = logger
        self._greedy_search = GreedySearchLeftSlice(model)
        # self._beam_search = BeamSearch(model)
