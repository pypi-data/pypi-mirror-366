# coding=utf-8
# Copyright 2022 EleutherAI and the HuggingFace Inc. team. All rights reserved.
#
# This code is based on EleutherAI's GPT-NeoX library and the GPT-NeoX
# and OPT implementations in this library. It has been modified from its
# original forms to accommodate minor architectural differences compared
# to GPT-NeoX and OPT used by the Meta AI team that trained the model.
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

from ..gptj.kv_caching import kv_page_update
from .huggingface import LlamaAttention, apply_rotary_pos_emb
from .paged_attention_utils import prepare_inputs_for_paged_attention_generation
from .utils import renew_attention_module

logger = logging.get_logger(__name__)


# LlamaForCausalLM.forward returns Tuple[torch.Tensor]
class NewLlamaAttention(LlamaAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        valid_key_indices: torch.IntTensor,
        valid_value_indices: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        past_key_value: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update,
        **kwargs,
    ) -> Tuple[torch.Tensor]:
        bsz, q_len, _ = hidden_states.size()

        query_states, key_states, value_states = self.proj_qkv(hidden_states, bsz=bsz, q_len=q_len)

        query_states, key_states = self.apply_rope(
            query_states=query_states,
            key_states=key_states,
            value_states=value_states,
            position_ids=position_ids,
        )

        key_states, value_states, _ = kv_update_method(
            present_key=key_states,
            present_value=value_states,
            past_key_value=past_key_value,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            valid_key_indices=valid_key_indices,
            valid_value_indices=valid_value_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            head_first=False,
        )

        present_key_value = None

        attn_output = self.compute_attn(
            query_states, key_states, value_states, attention_mask, bsz=bsz, q_len=q_len
        )

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, present_key_value

    def apply_rope(
        self,
        query_states: torch.Tensor,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        kv_seq_len: Optional[int] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_first: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        sin = self.rotary_emb.sin_cached.to(value_states.dtype)
        cos = self.rotary_emb.cos_cached.to(value_states.dtype)
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, cos, sin, position_ids
        )

        if not head_first:
            key_states = key_states.transpose(1, 2)

        return query_states, key_states


LlamaForCausalLM = renew_attention_module(new_attn=NewLlamaAttention)

# FIXME: remove this.
LlamaForCausalLM.prepare_inputs_for_generation = prepare_inputs_for_paged_attention_generation
