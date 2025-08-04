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

"""
Llama-2 MLPerf-v4.1 submission candidate model.

This model includes the following optimizations:

- Model architecture:
    - Optimized Paged Attention: This optimization improves the performance of paged attention by reducing memory access in both the prefill and decode phases.
        Reference: [Optimized Paged Attention](https://www.notion.so/furiosa/GPT-J-b90c57dfcc744f5da4a9c2663370907c?pvs=4#019f77aca42a43a6b320bf9d220b2955)
    - Fast ROPE: This optimization rewrites the original ROPE implementation to run it faster on RNGD at the expense of a slight increase in memory usage.
        Reference: [Fast ROPE](https://www.notion.so/furiosa/RoPE-d9962d473bd746b9b2295a374aa93965)
    - Slicing: This optimization rewrites the last block to only account for last sequence since we do not use packing. This forces the generator to left padding for prefill

- Generator:
    - Causal mask-free decoding: This optimization separates the causal mask from the attention mask in attention layer to reduce the computation overhead in the decoding phase.
        Reference: [Causal mask-free decoding](https://www.notion.so/furiosa/GPT-J-b90c57dfcc744f5da4a9c2663370907c?pvs=4#cf0767d3d5d948668892f67efb4f8cf1)
"""  # noqa

import math
from typing import Callable, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers.utils import logging
from transformers.utils.fx import get_concrete_args

from ...gptj.kv_caching import kv_page_update_do_input_select_with_past_kv_indices
from ...gptj.paged_attention_optimized_packed_rope import (
    get_decode_attn_weights,
)
from ...symbolic.helper import CausalLMSymbolicTrace
from ..huggingface_rope import FastLlamaAttention
from ..paged_attention_optimized_packed_rope import get_prefill_attn_weigths
from .huggingface import (
    BaseModelOutputWithPast,
    CausalLMOutputWithPast,
    CrossEntropyLoss,
    LlamaConfig,
    LlamaDecoderLayer,
    LlamaModel,
    PreTrainedModel,
    repeat_kv,
)
from .huggingface_rope import apply_rotary_pos_emb

logger = logging.get_logger(__name__)


# https://github.com/mlcommons/inference_policies/blob/c9fbbddf778eadb39b33decb6fa66d2b465481e8/inference_rules.adoc?plain=1#L257C57-L257C73
BUCKET_SIZE = 2048
SKIP_KEYS_DEVICE_PLACEMENT = ["bucket_size", "past_key_values", "layer_past", "past_key_value"]


# from ..llama.paged_attention_optimized_packed_rope.make_causal_mask
def make_causal_mask(
    mask: torch.Tensor,
    dtype: torch.dtype,
    device: torch.device,
) -> torch.Tensor:
    #     assert mask.dim() == 3, f"Only 3D mask is supported. Got {mask.dim()}D mask."
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


# from ...gptj.paged_attention_optimized_packed_rope.make_attention_mask
def make_attention_mask(mask: torch.Tensor, dtype: torch.dtype, device: torch.device):
    assert mask.dim() == 2, f"Only 2D mask is supported. Got {mask.dim()}D mask."
    batch_size = mask.size(0)
    if batch_size <= 0:
        raise ValueError("batch_size has to be defined and > 0")
    # We create a 3D attention mask from a 2D tensor mask.
    # Sizes are [batch_size, 1, 1, to_seq_length]
    # So we can broadcast to [batch_size, num_heads, from_seq_length, to_seq_length]
    # this attention mask is more simple than the triangular masking of causal attention
    # used in OpenAI GPT, we just need to prepare the broadcast dimension here.
    mask = mask[:, None, None, :].to(dtype=dtype)  # fp16 compatibility

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
        attention_mask: Optional[torch.FloatTensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update_do_input_select_with_past_kv_indices,
    ) -> Tuple[torch.Tensor]:
        bsz, q_len, _ = hidden_states.size()

        # self.proj_qkv in ..paged_attention_optimized_packed_rope.LlamaAttention.proj_qkv
        if self.pretraining_tp > 1:
            key_value_slicing = (self.num_key_value_heads * self.head_dim) // self.pretraining_tp
            query_slices = self.q_proj.weight.split(
                (self.num_heads * self.head_dim) // self.pretraining_tp, dim=0
            )
            key_slices = self.k_proj.weight.split(key_value_slicing, dim=0)
            value_slices = self.v_proj.weight.split(key_value_slicing, dim=0)

            query_states = [
                F.linear(hidden_states, query_slices[i]) for i in range(self.pretraining_tp)
            ]
            query_states = torch.cat(query_states, dim=-1)

            key_states = [
                F.linear(hidden_states, key_slices[i]) for i in range(self.pretraining_tp)
            ]
            key_states = torch.cat(key_states, dim=-1)

            value_states = [
                F.linear(hidden_states, value_slices[i]) for i in range(self.pretraining_tp)
            ]
            value_states = torch.cat(value_states, dim=-1)

        else:
            query_states = self.q_proj(hidden_states)
            key_states = self.k_proj(hidden_states)
            value_states = self.v_proj(hidden_states)

        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)
        key_states = key_states.view(bsz, q_len, self.num_key_value_heads, self.head_dim).transpose(
            1, 2
        )
        value_states = value_states.view(
            bsz, q_len, self.num_key_value_heads, self.head_dim
        ).transpose(1, 2)

        # get sincos positional embeddings from self.rotary_emb without slicing
        sincos = self.rotary_emb.sincos_cached
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, sincos, position_ids
        )

        head_first = False
        if not head_first:
            key_states = key_states.transpose(1, 2)

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

        # self.compute_attn in ..paged_attention_optimized_packed_rope.LlamaAttention.compute_attn
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
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32)
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

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, present_key_value


class NewLlamaDecoderLayer(LlamaDecoderLayer):
    def __init__(self, config: LlamaConfig):
        super().__init__(config)
        self.hidden_size = config.hidden_size
        self.self_attn = NewLlamaAttention(config=config)
        self.self_attn._skip_keys = SKIP_KEYS_DEVICE_PLACEMENT

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor]] = None,
        new_key_location: Optional[torch.IntTensor] = None,
        new_value_location: Optional[torch.IntTensor] = None,
        past_valid_key_indices: Optional[torch.IntTensor] = None,
        past_valid_value_indices: Optional[torch.IntTensor] = None,
        is_prefill: bool = True,
        bucket_size: int = BUCKET_SIZE,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
    ) -> Tuple[torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]]:
        """
        Args:
            hidden_states (`torch.FloatTensor`): input to the layer of shape
                `(batch, seq_len, embed_dim)`
            attention_mask (`torch.FloatTensor`, *optional*): attention mask of size
                `(batch, 1, tgt_len, src_len)` where padding elements are indicated by very large
                negative values.
            output_attentions (`bool`, *optional*):
                Whether or not to return the attentions tensors of all attention layers
                See `attentions` under returned tensors for more detail.
            use_cache (`bool`, *optional*):
                If set to `True`, `past_key_values` key value states are returned and can be used
                to speed up decoding (see `past_key_values`).
            past_key_value (`Tuple(torch.FloatTensor)`, *optional*): cached past key and value
                projection states
        """

        residual = hidden_states

        hidden_states = self.input_layernorm(hidden_states)
        # Self Attention
        hidden_states, self_attn_weights, present_key_value = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            causal_mask=causal_mask,
            position_ids=position_ids,
            past_key_value=past_key_value,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_indices=past_valid_key_indices,
            past_valid_value_indices=past_valid_value_indices,
            is_prefill=is_prefill,
            bucket_size=bucket_size,
            output_attentions=output_attentions,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (self_attn_weights,)

        if use_cache:
            outputs += (present_key_value,)

        return outputs


class NewLlamaDecoderLayerLast(LlamaDecoderLayer):
    def __init__(self, config: LlamaConfig):
        super().__init__(config)
        self.hidden_size = config.hidden_size
        self.self_attn = NewLlamaAttentionLast(config=config)
        self.self_attn._skip_keys = SKIP_KEYS_DEVICE_PLACEMENT

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_value: Optional[Tuple[torch.Tensor]] = None,
        new_key_location: Optional[torch.IntTensor] = None,
        new_value_location: Optional[torch.IntTensor] = None,
        past_valid_key_indices: Optional[torch.IntTensor] = None,
        past_valid_value_indices: Optional[torch.IntTensor] = None,
        is_prefill: bool = True,
        bucket_size: int = BUCKET_SIZE,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
    ) -> Tuple[torch.FloatTensor, Optional[Tuple[torch.FloatTensor, torch.FloatTensor]]]:
        """
        Args:
            hidden_states (`torch.FloatTensor`): input to the layer of shape
                `(batch, seq_len, embed_dim)`
            attention_mask (`torch.FloatTensor`, *optional*): attention mask of size
                `(batch, 1, tgt_len, src_len)` where padding elements are indicated by very large
                negative values.
            output_attentions (`bool`, *optional*):
                Whether or not to return the attentions tensors of all attention layers
                See `attentions` under returned tensors for more detail.
            use_cache (`bool`, *optional*):
                If set to `True`, `past_key_values` key value states are returned and can be used
                to speed up decoding (see `past_key_values`).
            past_key_value (`Tuple(torch.FloatTensor)`, *optional*): cached past key and value
                projection states
        """

        residual = hidden_states[:, -1:, :]

        hidden_states = self.input_layernorm(hidden_states)
        # Self Attention
        hidden_states, self_attn_weights, present_key_value = self.self_attn(
            hidden_states=hidden_states,
            attention_mask=attention_mask,
            causal_mask=causal_mask,
            position_ids=position_ids,
            past_key_value=past_key_value,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_indices=past_valid_key_indices,
            past_valid_value_indices=past_valid_value_indices,
            is_prefill=is_prefill,
            bucket_size=bucket_size,
            output_attentions=output_attentions,
        )
        hidden_states = residual + hidden_states

        # Fully Connected
        residual = hidden_states
        hidden_states = self.post_attention_layernorm(hidden_states)
        hidden_states = self.mlp(hidden_states)
        hidden_states = residual + hidden_states

        outputs = (hidden_states,)

        if output_attentions:
            outputs += (self_attn_weights,)

        if use_cache:
            outputs += (present_key_value,)

        return outputs


class NewLlamaAttentionLast(FastLlamaAttention):
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
        attention_mask: Optional[torch.FloatTensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update_do_input_select_with_past_kv_indices,
    ) -> Tuple[torch.Tensor]:
        q_hidden_states = hidden_states[:, -1:, :]

        bsz, q_len, _ = q_hidden_states.size()
        bsz, kv_len, _ = hidden_states.size()
        query_states = self.q_proj(q_hidden_states)

        key_states = self.k_proj(hidden_states)
        value_states = self.v_proj(hidden_states)

        query_states = query_states.view(bsz, q_len, self.num_heads, self.head_dim).transpose(1, 2)

        key_states = key_states.view(
            bsz, kv_len, self.num_key_value_heads, self.head_dim
        ).transpose(  # noqa: E501
            1, 2
        )
        value_states = value_states.view(
            bsz, kv_len, self.num_key_value_heads, self.head_dim
        ).transpose(1, 2)

        # get sincos positional embeddings from self.rotary_emb without slicing
        sincos = self.rotary_emb.sincos_cached
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, sincos, position_ids
        )

        head_first = False
        if not head_first:
            key_states = key_states.transpose(1, 2)

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

        # self.compute_attn in ..paged_attention_optimized_packed_rope.LlamaAttention.compute_attn
        key_states = repeat_kv(key_states, self.num_key_value_groups)
        value_states = repeat_kv(value_states, self.num_key_value_groups)

        attn_weights = torch.matmul(query_states, key_states.transpose(2, 3)) / math.sqrt(
            self.head_dim
        )

        if is_prefill:
            attn_weights = get_prefill_attn_weigths(attn_weights, causal_mask[:, :, -1:, :])
        else:
            attn_weights = get_decode_attn_weights(attn_weights, attention_mask)

        # upcast attention to fp32
        attn_weights = nn.functional.softmax(attn_weights, dim=-1, dtype=torch.float32)
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

        if not output_attentions:
            attn_weights = None

        return attn_output, attn_weights, present_key_value


class NewLlamaModel(LlamaModel):
    def __init__(self, config: LlamaConfig):
        super().__init__(config)
        self.layers = nn.ModuleList(
            [NewLlamaDecoderLayer(config) for _ in range(config.num_hidden_layers - 1)]
            + [NewLlamaDecoderLayerLast(config)]
        )

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        new_key_location: Optional[torch.IntTensor] = None,
        new_value_location: Optional[torch.IntTensor] = None,
        past_valid_key_indices: Optional[torch.IntTensor] = None,
        past_valid_value_indices: Optional[torch.IntTensor] = None,
        is_prefill: bool = True,
        bucket_size: int = BUCKET_SIZE,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
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
        if is_prefill:
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
                    new_key_location=new_key_location,
                    new_value_location=new_value_location,
                    past_valid_key_indices=past_valid_key_indices,
                    past_valid_value_indices=past_valid_value_indices,
                    is_prefill=is_prefill,
                    bucket_size=bucket_size,
                    use_cache=use_cache,
                    output_attentions=output_attentions,
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


class LlamaPreTrainedModel(PreTrainedModel):
    config_class = LlamaConfig
    base_model_prefix = "model"
    supports_gradient_checkpointing = True
    _no_split_modules = ["NewLlamaDecoderLayer"]
    _skip_keys_device_placement = SKIP_KEYS_DEVICE_PLACEMENT

    def _init_weights(self, module):
        std = self.config.initializer_range
        if isinstance(module, nn.Linear):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=std)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()

    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, LlamaModel):
            module.gradient_checkpointing = value


class LlamaForCausalLM(LlamaPreTrainedModel, CausalLMSymbolicTrace):
    _tied_weights_keys = ["lm_head.weight"]

    def __init__(self, config):
        super().__init__(config)
        self.model = NewLlamaModel(config)
        self.pretraining_tp = config.pretraining_tp
        self.vocab_size = config.vocab_size
        self.lm_head = nn.Linear(config.hidden_size, config.vocab_size, bias=False)

        # Initialize weights and apply final processing
        self.post_init()

    def get_input_embeddings(self):
        return self.model.embed_tokens

    def set_input_embeddings(self, value):
        self.model.embed_tokens = value

    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings

    def set_decoder(self, decoder):
        self.model = decoder

    def get_decoder(self):
        return self.model

    def forward(
        self,
        input_ids: torch.LongTensor = None,
        attention_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        new_key_location: Optional[torch.IntTensor] = None,
        new_value_location: Optional[torch.IntTensor] = None,
        past_valid_key_indices: Optional[torch.IntTensor] = None,
        past_valid_value_indices: Optional[torch.IntTensor] = None,
        is_prefill: bool = True,
        bucket_size: int = BUCKET_SIZE,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, CausalLMOutputWithPast]:
        r"""
        Args:
            labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
                Labels for computing the masked language modeling loss. Indices should either be
                in `[0, ..., config.vocab_size]` or -100 (see `input_ids` docstring). Tokens with
                indices set to `-100` are ignored (masked), the loss is only computed for the
                tokens with labels in `[0, ..., config.vocab_size]`.

        Returns:

        Example:

        ```python
        >>> from transformers import AutoTokenizer, LlamaForCausalLM

        >>> model = LlamaForCausalLM.from_pretrained(PATH_TO_CONVERTED_WEIGHTS)
        >>> tokenizer = AutoTokenizer.from_pretrained(PATH_TO_CONVERTED_TOKENIZER)

        >>> prompt = "Hey, are you conscious? Can you talk to me?"
        >>> inputs = tokenizer(prompt, return_tensors="pt")

        >>> # Generate
        >>> generate_ids = model.generate(inputs.input_ids, max_length=30)
        >>> tokenizer.batch_decode(generate_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
        "Hey, are you conscious? Can you talk to me?\nI'm not conscious, but I can talk to you."
        ```"""  # noqa: E501

        output_attentions = (
            output_attentions if output_attentions is not None else self.config.output_attentions
        )
        output_hidden_states = (
            output_hidden_states
            if output_hidden_states is not None
            else self.config.output_hidden_states
        )
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        # decoder outputs consists of (dec_features, layer_state, dec_hidden, dec_attn)
        outputs = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            causal_mask=causal_mask,
            position_ids=position_ids,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_indices=past_valid_key_indices,
            past_valid_value_indices=past_valid_value_indices,
            is_prefill=is_prefill,
            bucket_size=bucket_size,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
        )

        hidden_states = outputs[0]
        if self.pretraining_tp > 1:
            lm_head_slices = self.lm_head.weight.split(
                self.vocab_size // self.pretraining_tp, dim=0
            )
            logits = [
                F.linear(hidden_states, lm_head_slices[i]) for i in range(self.pretraining_tp)
            ]
            logits = torch.cat(logits, dim=-1)
        else:
            logits = self.lm_head(hidden_states)
        logits = logits.float()

        loss = None
        if labels is not None:
            # Shift so that tokens < n predict n
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            # Flatten the tokens
            loss_fct = CrossEntropyLoss()
            shift_logits = shift_logits.view(-1, self.config.vocab_size)
            shift_labels = shift_labels.view(-1)
            # Enable model parallelism
            shift_labels = shift_labels.to(shift_logits.device)
            loss = loss_fct(shift_logits, shift_labels)

        if not return_dict:
            output = (logits,) + outputs[1:]
            return (loss,) + output if loss is not None else output

        return CausalLMOutputWithPast(
            loss=loss,
            logits=logits,
            past_key_values=outputs.past_key_values,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )

    def prepare_inputs_for_generation(
        self, input_ids, past_key_values=None, attention_mask=None, inputs_embeds=None, **kwargs
    ):
        if past_key_values:
            input_ids = input_ids[:, -1:]

        position_ids = kwargs.get("position_ids", None)
        if attention_mask is not None and position_ids is None:
            # create position_ids on the fly for batch generation
            position_ids = attention_mask.long().cumsum(-1) - 1
            position_ids.masked_fill_(attention_mask == 0, 1)
            if past_key_values:
                position_ids = position_ids[:, -1].unsqueeze(-1)

        # if `inputs_embeds` are passed, we only want to use them in the 1st generation step
        if inputs_embeds is not None and past_key_values is None:
            model_inputs = {"inputs_embeds": inputs_embeds}
        else:
            model_inputs = {"input_ids": input_ids}

        model_inputs.update(
            {
                "position_ids": position_ids,
                "past_key_values": past_key_values,
                "use_cache": kwargs.get("use_cache"),
                "attention_mask": attention_mask,
            }
        )
        return model_inputs

    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (
                tuple(
                    past_state.index_select(0, beam_idx.to(past_state.device))
                    for past_state in layer_past
                ),
            )
        return reordered_past

    def get_input_names_and_concrete_args(
        self, model, prefill_phase=True
    ) -> Tuple[List[str], Dict]:
        model = self

        if prefill_phase:
            input_names = [
                "input_ids",
                "causal_mask",
                "position_ids",
                "past_key_values",
                "new_key_location",
                "new_value_location",
                "bucket_size",
            ]
        else:
            input_names = [
                "input_ids",
                "position_ids",
                "past_key_values",
                "attention_mask",
                "new_key_location",
                "new_value_location",
                "past_valid_key_indices",
                "past_valid_value_indices",
                "bucket_size",
            ]

        concrete_args = get_concrete_args(model, input_names)

        if prefill_phase:
            custom_concrete_args = {
                "use_cache": False,
                "return_dict": True,
                "output_attentions": False,
                "output_hidden_states": False,
                "is_prefill": True,
            }
        else:
            custom_concrete_args = {
                "use_cache": False,
                "return_dict": True,
                "output_attentions": False,
                "output_hidden_states": False,
                "is_prefill": False,
            }

        for arg in custom_concrete_args:
            if arg in concrete_args:
                concrete_args[arg] = custom_concrete_args[arg]
                continue
            raise ValueError(f"{arg} is not defined in {concrete_args}")

        return input_names, concrete_args
