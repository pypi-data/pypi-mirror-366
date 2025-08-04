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

from typing import Callable, Optional, Tuple

import torch
from transformers.utils import logging

from .huggingface import GPTJAttention
from .kv_caching import kv_page_update
from .paged_attention_utils import prepare_inputs_for_paged_attention_generation
from .utils import renew_attention_module

logger = logging.get_logger(__name__)


# GPTJCausalForLM.forward returns Tuple[torch.Tensor]
class NewGPTJAttention(GPTJAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        valid_key_indices: torch.IntTensor,
        valid_value_indices: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        layer_past: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update,
        **kwargs,
    ) -> Tuple[torch.Tensor]:
        query, key, value = self.proj_qkv(hidden_states)

        query, key = self.apply_rope(query, key, position_ids)

        key, value, _ = kv_update_method(
            present_key=key,
            present_value=value,
            past_key_value=layer_past,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            valid_key_indices=valid_key_indices,
            valid_value_indices=valid_value_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            head_first=False,
        )

        present_key_value = None

        attn_output, attn_weights = self.compute_attn(query, key, value, attention_mask, head_mask)

        outputs = (attn_output, present_key_value)
        if output_attentions:
            outputs += (attn_weights,)

        return outputs


GPTJForCausalLM = renew_attention_module(new_attn=NewGPTJAttention)
# FIXME: remove this.
GPTJForCausalLM.prepare_inputs_for_generation = prepare_inputs_for_paged_attention_generation
