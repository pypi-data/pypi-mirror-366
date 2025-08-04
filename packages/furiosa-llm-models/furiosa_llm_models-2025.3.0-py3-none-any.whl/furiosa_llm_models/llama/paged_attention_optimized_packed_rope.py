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

import math
from typing import Callable, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers.utils import logging

from ..gptj.kv_caching import kv_page_update_do_input_select_with_past_kv_indices
from ..gptj.paged_attention_optimized_packed_rope import (
    get_decode_attn_weights,
    make_attention_mask,
)
from .huggingface import BaseModelOutputWithPast, LlamaModel, repeat_kv
from .paged_attention_rope import NewLlamaAttention as FastLlamaAttention
from .utils import renew_attention_module

logger = logging.get_logger(__name__)


def make_causal_mask(
    mask: torch.Tensor,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    assert mask.dim() == 3, f"Only 3D mask is supported. Got {mask.dim()}D mask."
    batch_size = mask.size(0)
    if batch_size <= 0:
        raise ValueError("batch_size has to be defined and > 0")
    mask = mask[:, None, :, :].to(dtype=dtype)  # fp16 compatibility

    # Since attention_mask is 1.0 for positions we want to attend and 0.0 for
    # masked positions, this operation will create a tensor which is 0.0 for
    # positions we want to attend and the dtype's smallest value for masked positions.
    # Since we are adding it to the raw scores before the softmax, this is
    # effectively the same as removing these entirely.
    inverted_mask = 1.0 - mask
    # Mask unattentive tokens' position with the least negative value to exclude them from
    # attention calculations.
    return inverted_mask.masked_fill(inverted_mask.to(torch.bool), torch.finfo(dtype).min).to(
        device
    )


def get_prefill_attn_weigths(
    attn_weights: torch.Tensor, causal_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    return attn_weights + causal_mask.to(
        attn_weights.dtype
    )  # in prefill, causal_mask is used as a mask


# LlamaForCausalLM.forward returns Tuple[torch.Tensor]
class NewLlamaAttention(FastLlamaAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        past_valid_key_indices: torch.IntTensor,
        past_valid_value_indices: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        past_key_value: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        causal_mask: Optional[torch.Tensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update_do_input_select_with_past_kv_indices,
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

        key_states, value_states = kv_update_method(
            present_key=key_states,
            present_value=value_states,
            past_key_value=past_key_value,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_indices=past_valid_key_indices,
            past_valid_value_indices=past_valid_value_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            head_first=False,
        )

        present_key_value = None

        attn_output = self.compute_attn(
            query_states,
            key_states,
            value_states,
            attention_mask,
            causal_mask,
            is_prefill,
            bsz=bsz,
            q_len=q_len,
        )

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, present_key_value

    def compute_attn(
        self,
        query_states: torch.Tensor,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        is_prefill: bool = True,
        **kwargs,
    ) -> torch.Tensor:
        bsz = kwargs.get("bsz")
        q_len = kwargs.get("q_len")
        # repeat k/v heads if n_kv_heads < n_heads
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)

        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(
            self.head_dim
        )

        if is_prefill:
            attn_weights = get_prefill_attn_weigths(attn_weights, causal_mask)
        else:
            attn_weights = get_decode_attn_weights(attn_weights, attention_mask)

        # upcast attention to fp32
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32).to(
            query_states.dtype
        )
        attn_output = torch.matmul(attn_weights, value_states)

        attn_output = attn_output.transpose(1, 2).contiguous()
        attn_output = attn_output.reshape(bsz, q_len, self.hidden_size)

        if self.pretraining_tp > 1:
            attn_output = attn_output.split(self.hidden_size // self.pretraining_tp, dim=2)
            o_proj_slices = self.o_proj.weight.split(self.hidden_size // self.pretraining_tp, dim=1)
            attn_output = sum(
                [F.linear(attn_output[i], o_proj_slices[i]) for i in range(self.pretraining_tp)]
            )
        else:
            attn_output = self.o_proj(attn_output)

        return attn_output


class NewLlamaModel(LlamaModel):
    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
        is_paged_attention_prefill: Optional[bool] = None,
        **kwargs,
    ) -> Union[Tuple, BaseModelOutputWithPast]:
        output_attentions = (
            output_attentions if output_attentions is not None else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        use_cache = use_cache if use_cache is not None else self.config.use_cache

        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        # retrieve input_ids and inputs_embeds
        if input_ids is not None and inputs_embeds is not None:
            raise ValueError(
                "You cannot specify both decoder_input_ids and "
                "decoder_inputs_embeds at the same time"
            )
        elif input_ids is not None:
            batch_size, seq_length = input_ids.shape
        elif inputs_embeds is not None:
            batch_size, seq_length, _ = inputs_embeds.shape
        else:
            raise ValueError(
                "You have to specify either decoder_input_ids or decoder_inputs_embeds"
            )

        seq_length_with_past = seq_length
        past_key_values_length = 0

        if past_key_values is not None:
            past_key_values_length = past_key_values[0][0].shape[2]
            seq_length_with_past = seq_length_with_past + past_key_values_length

        # NOTE: In PagedAttention, past_key_values is always not None. So, we should check both
        # whether it's prefill or not, as well as the condition mentioned earlier.
        if is_paged_attention_prefill:
            seq_length_with_past = seq_length
            past_key_values_length = 0

        if position_ids is None:
            device = input_ids.device if input_ids is not None else inputs_embeds.device
            position_ids = torch.arange(
                past_key_values_length,
                seq_length + past_key_values_length,
                dtype=torch.long,
                device=device,
            )
            position_ids = position_ids.unsqueeze(0).view(-1, seq_length)
        else:
            position_ids = position_ids.view(-1, seq_length).long()

        if inputs_embeds is None:
            inputs_embeds = self.embed_tokens(input_ids)

        if causal_mask is not None:
            causal_mask = make_causal_mask(causal_mask, inputs_embeds.dtype, inputs_embeds.device)
        if attention_mask is not None:
            attention_mask = make_attention_mask(
                attention_mask, inputs_embeds.dtype, inputs_embeds.device
            )

        hidden_states = inputs_embeds

        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once(
                    "`use_cache=True` is incompatible with gradient checkpointing. "
                    "Setting `use_cache=False`..."
                )
                use_cache = False

        # decoder layers
        all_hidden_states = () if output_hidden_states else None
        all_self_attns = () if output_attentions else None
        next_decoder_cache = () if use_cache else None

        for idx, decoder_layer in enumerate(self.layers):
            if output_hidden_states:
                all_hidden_states += (hidden_states,)

            past_key_value = past_key_values[idx] if past_key_values is not None else None

            if self.gradient_checkpointing and self.training:

                def create_custom_forward(module):
                    def custom_forward(*inputs):
                        # None for past_key_value
                        return module(*inputs, output_attentions, None)

                    return custom_forward

                layer_outputs = torch.utils.checkpoint.checkpoint(
                    create_custom_forward(decoder_layer),
                    hidden_states,
                    attention_mask,
                    position_ids,
                    None,
                )
            else:
                layer_outputs = decoder_layer(
                    hidden_states,
                    attention_mask=attention_mask,
                    causal_mask=causal_mask,
                    position_ids=position_ids,
                    past_key_value=past_key_value,
                    output_attentions=output_attentions,
                    use_cache=use_cache,
                    **kwargs,
                )

            hidden_states = layer_outputs[0]

            if use_cache:
                next_decoder_cache += (layer_outputs[2 if output_attentions else 1],)

            if output_attentions:
                all_self_attns += (layer_outputs[1],)

        hidden_states = self.norm(hidden_states)

        # add hidden states from the last decoder layer
        if output_hidden_states:
            all_hidden_states += (hidden_states,)

        next_cache = next_decoder_cache if use_cache else None
        if not return_dict:
            return tuple(
                v
                for v in [hidden_states, next_cache, all_hidden_states, all_self_attns]
                if v is not None
            )
        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=next_cache,
            hidden_states=all_hidden_states,
            attentions=all_self_attns,
        )


LlamaForCausalLM = renew_attention_module(new_attn=NewLlamaAttention, new_model=NewLlamaModel)
