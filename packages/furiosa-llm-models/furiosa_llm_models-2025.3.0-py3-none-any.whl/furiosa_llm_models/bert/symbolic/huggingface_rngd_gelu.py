# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""PyTorch BERT model."""

from typing import Dict, List, Tuple

from transformers.utils import logging
from transformers.utils.fx import get_concrete_args

from ...symbolic.helper import QuestionAnsweringSymbolicTrace
from ..huggingface import BertForQuestionAnswering as HfBertForQuestionAnswering

logger = logging.get_logger(__name__)


class BertForQuestionAnswering(HfBertForQuestionAnswering, QuestionAnsweringSymbolicTrace):
    def __init__(self, config):
        config.hidden_act = "rngd_gelu"
        super().__init__(config)

    def get_input_names_and_concrete_args(self, model) -> Tuple[List[str], Dict]:
        model = self

        input_names = [
            "input_ids",
            "token_type_ids",
            "attention_mask",
        ]

        concrete_args = get_concrete_args(model, input_names)

        custom_concrete_args = {}

        for arg in custom_concrete_args:
            if arg in concrete_args:
                concrete_args[arg] = custom_concrete_args[arg]
                continue
            raise ValueError(f"{arg} is not defined in {concrete_args}")

        return input_names, concrete_args
