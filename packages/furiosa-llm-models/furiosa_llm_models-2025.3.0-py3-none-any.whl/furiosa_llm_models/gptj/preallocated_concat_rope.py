# coding=utf-8
# Copyright 2021 The EleutherAI and HuggingFace Teams. All rights reserved.
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
"""PyTorch GPT-J model."""

from typing import Optional, Tuple

import torch
from transformers.utils import logging

from .huggingface_rope import FastGPTJAttention
from .kv_caching import kv_concat_update_reducing_next_kv_size
from .utils import renew_attention_module

logger = logging.get_logger(__name__)


# GPTJCausalForLM.forward returns Tuple[torch.Tensor, Tuple[Tuple[torch.Tensor, torch.Tensor], ...]]
class NewGPTJAttention(FastGPTJAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        layer_past: Optional[Tuple[Tuple[torch.Tensor, torch.Tensor], ...]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        use_cache: bool = False,
        output_attentions: bool = False,
    ) -> Tuple[torch.Tensor, Tuple[Tuple[torch.Tensor, torch.Tensor], ...]]:
        return FastGPTJAttention.forward(
            self,
            hidden_states=hidden_states,
            layer_past=layer_past,
            attention_mask=attention_mask,
            position_ids=position_ids,
            head_mask=head_mask,
            use_cache=use_cache,
            output_attentions=output_attentions,
            kv_update_method=kv_concat_update_reducing_next_kv_size,
        )


GPTJForCausalLM = renew_attention_module(new_attn=NewGPTJAttention)
