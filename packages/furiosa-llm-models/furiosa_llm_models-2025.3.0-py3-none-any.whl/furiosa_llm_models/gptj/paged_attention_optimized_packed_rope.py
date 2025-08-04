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

from typing import Callable, Optional, Tuple, Union

import torch
from transformers.utils import logging

from .huggingface import BaseModelOutputWithPast, GPTJModel
from .huggingface_rope import FastGPTJAttention
from .kv_caching import kv_page_update_do_input_select_with_past_kv_indices
from .utils import renew_attention_module

logger = logging.get_logger(__name__)


def make_attention_mask(
    mask: torch.Tensor, dtype: torch.dtype, device: torch.device
) -> torch.Tensor:
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


def make_causal_mask(
    mask: torch.Tensor,
) -> torch.Tensor:
    assert mask.dim() == 3, f"Only 3D mask is supported. Got {mask.dim()}D mask."
    batch_size = mask.size(0)
    if batch_size <= 0:
        raise ValueError("batch_size has to be defined and > 0")
    return mask[:, None, :, :]  # fp16 compatibility


def get_prefill_attn_weigths(
    attn_weights: torch.Tensor, causal_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    # Because this typecasting will cause accuracy degradation, we want this typecasting to
    # occur in MCM_matmul module that performs matmul.
    # query = query.to(torch.float32)
    # key = key.to(torch.float32)
    mask_value = torch.finfo(attn_weights.dtype).min
    # Need to be a tensor, otherwise we get error: `RuntimeError: expected scalar type float but
    # found double`.
    # Need to be on the same device, otherwise
    #   `RuntimeError: ..., x and y to be on the same device`
    mask_value = torch.tensor(mask_value, dtype=attn_weights.dtype).to(attn_weights.device)
    return torch.where(
        causal_mask, attn_weights, mask_value
    )  # in prefill, causal_mask is used as a mask


def get_decode_attn_weights(
    attn_weights: torch.Tensor, attention_mask: Optional[torch.Tensor] = None
) -> torch.Tensor:
    # Because this typecasting will cause accuracy degradation, we want this typecasting to
    # occur in MCM_matmul module that performs matmul.
    # query = query.to(torch.float32)
    # key = key.to(torch.float32)
    return attn_weights + attention_mask.to(
        attn_weights.dtype
    )  # in decode, attention_mask is used as a mask


# GPTJCausalForLM.forward returns Tuple[torch.Tensor]
class NewGPTJAttention(FastGPTJAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        past_valid_key_indices: torch.IntTensor,
        past_valid_value_indices: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        layer_past: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        attention_mask: Optional[torch.FloatTensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        output_attentions: bool = False,
        kv_update_method: Callable = kv_page_update_do_input_select_with_past_kv_indices,
        **kwargs,
    ) -> Tuple[torch.Tensor]:
        query, key, value = self.proj_qkv(hidden_states)

        query, key = self.apply_rope(query, key, position_ids)

        key, value = kv_update_method(
            present_key=key,
            present_value=value,
            past_key_value=layer_past,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_indices=past_valid_key_indices,
            past_valid_value_indices=past_valid_value_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            head_first=False,
        )

        present_key_value = None

        attn_output, attn_weights = self.compute_attn(
            query,
            key,
            value,
            attention_mask,
            head_mask,
            causal_mask=causal_mask,
            is_prefill=is_prefill,
        )

        outputs = (attn_output, present_key_value)
        if output_attentions:
            outputs += (attn_weights,)

        return outputs

    def _attn(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        head_mask: Optional[torch.Tensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        is_prefill: bool = True,
    ):
        attn_weights = torch.matmul(query, key.transpose(-1, -2))

        if is_prefill:
            attn_weights = get_prefill_attn_weigths(attn_weights, causal_mask)
        else:
            attn_weights = get_decode_attn_weights(attn_weights, attention_mask)

        attn_weights /= self.scale_attn

        attn_weights = torch.nn.functional.softmax(attn_weights, dim=-1)
        # we restrict the softmax output to be in bfloat16 in quantized model, i.e., in W8A8KV8
        # model where value.dtype == int8 is true, the code below will typecast score to int8 and
        # thus cause significant accuracy degradation.
        # attn_weights = attn_weights.to(value.dtype)
        attn_weights = self.attn_dropout(attn_weights)

        # Mask heads if we want to
        if head_mask is not None:
            attn_weights = attn_weights * head_mask

        attn_output = torch.matmul(attn_weights, value)

        return attn_output, attn_weights


class NewGPTJModel(GPTJModel):
    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        causal_mask: Optional[torch.Tensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
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

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
        else:
            raise ValueError("You have to specify either input_ids or inputs_embeds")

        device = input_ids.device if input_ids is not None else inputs_embeds.device

        if token_type_ids is not None:
            token_type_ids = token_type_ids.view(-1, input_shape[-1])

        # if position_ids is not None:
        #     position_ids = position_ids.view(-1, input_shape[-1]).long()

        if past_key_values is None:
            past_length = 0
            past_key_values = tuple([None] * len(self.h))
        else:
            past_length = past_key_values[0][0].size(-2)

        if position_ids is None:
            position_ids = torch.arange(
                past_length, input_shape[-1] + past_length, dtype=torch.long, device=device
            )
            position_ids = position_ids.unsqueeze(0).view(-1, input_shape[-1])

        if causal_mask is not None:
            causal_mask = make_causal_mask(causal_mask)
        if attention_mask is not None:
            attention_mask = make_attention_mask(attention_mask, self.dtype, self.device)

        # Prepare head mask if needed
        # 1.0 in head_mask indicate we keep the head
        # attention_probs has shape bsz x num_attention_heads x N x N
        # head_mask has shape n_layer x batch x num_attention_heads x N x N
        head_mask = self.get_head_mask(head_mask, self.config.n_layer)

        if inputs_embeds is None:
            inputs_embeds = self.wte(input_ids)

        hidden_states = inputs_embeds

        if token_type_ids is not None:
            token_type_embeds = self.wte(token_type_ids)
            hidden_states = hidden_states + token_type_embeds

        hidden_states = self.drop(hidden_states)

        output_shape = input_shape + (hidden_states.size(-1),)

        if self.gradient_checkpointing and self.training:
            if use_cache:
                logger.warning_once(
                    "`use_cache=True` is incompatible with gradient checkpointing. "
                    "Setting `use_cache=False`..."
                )
                use_cache = False

        presents = () if use_cache else None
        all_self_attentions = () if output_attentions else None
        all_hidden_states = () if output_hidden_states else None
        for i, block in enumerate(self.h):
            layer_past = past_key_values[i]

            if output_hidden_states:
                all_hidden_states = all_hidden_states + (hidden_states,)

            if self.gradient_checkpointing and self.training:

                def create_custom_forward(module):
                    def custom_forward(*inputs):
                        # None for past_key_value
                        return module(*inputs, use_cache, output_attentions)

                    return custom_forward

                outputs = torch.utils.checkpoint.checkpoint(
                    create_custom_forward(block),
                    hidden_states,
                    None,
                    attention_mask,
                    position_ids,
                    head_mask[i],
                )
            else:
                outputs = block(
                    hidden_states=hidden_states,
                    layer_past=layer_past,
                    attention_mask=attention_mask,
                    causal_mask=causal_mask,
                    position_ids=position_ids,
                    head_mask=head_mask[i],
                    use_cache=use_cache,
                    output_attentions=output_attentions,
                    **kwargs,
                )

            hidden_states = outputs[0]
            if use_cache is True:
                presents = presents + (outputs[1],)

            if output_attentions:
                all_self_attentions = all_self_attentions + (outputs[2 if use_cache else 1],)

        hidden_states = self.ln_f(hidden_states)

        hidden_states = hidden_states.view(output_shape)
        # Add last hidden state
        if output_hidden_states:
            all_hidden_states = all_hidden_states + (hidden_states,)

        if not return_dict:
            return tuple(
                v
                for v in [hidden_states, presents, all_hidden_states, all_self_attentions]
                if v is not None
            )

        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=presents,
            hidden_states=all_hidden_states,
            attentions=all_self_attentions,
        )


GPTJForCausalLM = renew_attention_module(new_attn=NewGPTJAttention, new_model=NewGPTJModel)
