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

"""
GPT-J MLPerf-v4.1 submission candidate model.

This model includes the following optimizations:

- Model architecture:
    - Optimized Paged Attention: This optimization improves the performance of paged attention by reducing memory access in both the prefill and decode phases.
        Reference: [Optimized Paged Attention](https://www.notion.so/furiosa/GPT-J-b90c57dfcc744f5da4a9c2663370907c?pvs=4#019f77aca42a43a6b320bf9d220b2955)
    - Fast ROPE: This optimization rewrites the original ROPE implementation to run it faster on RNGD at the expense of a slight increase in memory usage.
        Reference: [Fast ROPE](https://www.notion.so/furiosa/RoPE-d9962d473bd746b9b2295a374aa93965)
    - RNGD Gelu: This optimization rewrites the transformer's Gelu activation function to run in a single execution on RNGD.
        Reference: [RNGD Gelu](https://www.notion.so/furiosa/GPT-J-6e6ff841bcbc402dbecc03069b8c60b3?pvs=4#000c2dbb20184e488dc3f3e4fbbd48c9)

- Generator:
    - Input Packing: This optimization packs batches of input tokens into smaller ones.
        Reference: [Input Packing](https://www.notion.so/furiosa/packing-attention-3d432f4eea914345b06668b0fafce640)
    - Causal mask-free decoding: This optimization separates the causal mask from the attention mask in attention layer to reduce the computation overhead in the decoding phase.
        Reference: [Causal mask-free decoding](https://www.notion.so/furiosa/GPT-J-b90c57dfcc744f5da4a9c2663370907c?pvs=4#cf0767d3d5d948668892f67efb4f8cf1)
    - KV cache sharing across beams: This optimization shares logits of the prefill phase across all beams in Beam Search decoding, reducing redundant computation.
        Reference: [Logit sharing across beams](https://linear.app/furiosa-ai/issue/LLM-387/gptj-paged-attention-%EB%A1%9C%EC%A7%81%EC%97%90-beam-search-%EC%97%90%EC%84%9C-prompt%EB%A5%BC-%EA%B3%B5%EC%9C%A0%ED%95%98%EB%8A%94-batch%EB%93%A4%EC%97%90-%EB%8C%80%ED%95%B4#comment-e91385a2)
    - Beamsearch Softmax inbounding: This optimization inbounds the softmax operation into the model during the decoding phase, allowing it to be compiled and executed on the RNGD accelerator.
        Reference: [Softmax inbounding](https://furiosa-ai.slack.com/archives/D05BKAJH9C2/p1718331193534609)
"""  # noqa

from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.fx
import torch.utils.checkpoint
from torch import nn
from transformers import GPTJConfig
from transformers.modeling_outputs import (
    BaseModelOutputWithPast,
    CausalLMOutputWithPast,
)
from transformers.modeling_utils import PreTrainedModel
from transformers.utils import logging
from transformers.utils.fx import get_concrete_args

from ...symbolic.helper import CausalLMSymbolicTrace
from ..huggingface import GPTJMLP as HfGPTJMLP
from ..huggingface import GPTJModel as HfGPTJModel
from ..huggingface_rope import FastGPTJAttention
from ..kv_caching import kv_paged_update_beam

logger = logging.get_logger(__name__)

GPTJ_PRETRAINED_MODEL_ARCHIVE_LIST = [
    "EleutherAI/gpt-j-6B",
    # See all GPT-J models at https://huggingface.co/models?filter=gptj
]
BUCKET_SIZE = 2048
NUM_BEAMS = 4
MAX_NEW_TOKENS = 128
NUM_REAL_BATCH = 1


# GPTJCausalForLM.forward returns Tuple[torch.Tensor]
class NewGPTJAttention(FastGPTJAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        layer_past: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        output_attentions: bool = False,
    ) -> Tuple[torch.Tensor]:
        query, key, value = self.proj_qkv(hidden_states)

        query, key = self.apply_rope(query, key, position_ids)

        key, value = kv_paged_update_beam(
            present_key=key,
            present_value=value,
            past_key_value=layer_past,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_prompt_indices=past_valid_key_prompt_indices,
            past_valid_value_prompt_indices=past_valid_value_prompt_indices,
            past_valid_key_decode_indices=past_valid_key_decode_indices,
            past_valid_value_decode_indices=past_valid_value_decode_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            num_beam=num_beam,
            max_new_tokens=max_new_tokens,
            head_first=False,
            num_real_batch=num_real_batch,
        )

        present_key_value = None

        # for this optimized version, attn computation differs from original attn
        # so we use a custom attn method
        attn_dropout = self.attn_dropout
        # in the long term, causal_mask should be passed as input argument not keyword argument
        # self.bias should not be initialized as it is not used
        scale_attn = self.scale_attn

        attn_weights = torch.matmul(query, key.transpose(-1, -2))
        if is_prefill:
            # prefill, no attention mask
            assert attention_mask is None
            # Because this typecasting will cause accuracy degradation, we want this typecasting to
            # occur in MCM_matmul module that performs matmul.
            # query = query.to(torch.float32)
            # key = key.to(torch.float32)
            mask_value = torch.finfo(attn_weights.dtype).min
            # Need to be a tensor, otherwise we get error: `RuntimeError: expected scalar type float
            # but found double`.
            # Need to be on the same device, otherwise
            #   `RuntimeError: ..., x and y to be on the same device`
            mask_value = torch.tensor(mask_value, dtype=attn_weights.dtype).to(attn_weights.device)
            # at this point, causal_mask should be expanded to [batch, head, seq_len, seq_len]
            causal_mask = causal_mask[:, None, :, :]
            attn_weights = torch.where(causal_mask, attn_weights, mask_value)
            attn_weights = attn_weights / scale_attn
        else:
            # decode, no need for causal mask
            assert causal_mask is None
            # Because this typecasting will cause accuracy degradation, we want this typecasting to
            # occur in MCM_matmul module that performs matmul.
            # query = query.to(torch.float32)
            # key = key.to(torch.float32)
            attn_weights = attn_weights / scale_attn
            attn_weights = attn_weights + attention_mask

        attn_weights = torch.nn.functional.softmax(attn_weights, dim=-1)
        # we restrict the softmax output to be in bfloat16 in quantized model, i.e., in W8A8KV8
        # model where value.dtype == int8 is true, the code below will typecast score to int8 and
        # thus cause significant accuracy degradation.
        # attn_weights = attn_weights.to(value.dtype)
        attn_weights = attn_dropout(attn_weights)
        # Mask heads if we want to
        if head_mask is not None:
            attn_weights = attn_weights * head_mask
        attn_output = torch.matmul(attn_weights, value)

        attn_output = self._merge_heads(attn_output, self.num_attention_heads, self.head_dim)
        attn_output = self.out_proj(attn_output)
        attn_output = self.resid_dropout(attn_output)

        outputs = (attn_output, present_key_value)
        if output_attentions:
            outputs += (attn_weights,)

        return outputs


class GPTJBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        inner_dim = config.n_inner if config.n_inner is not None else 4 * config.n_embd
        self.ln_1 = nn.LayerNorm(config.n_embd, eps=config.layer_norm_epsilon)
        self.attn = NewGPTJAttention(config)
        self.mlp = HfGPTJMLP(inner_dim, config)

    def forward(
        self,
        hidden_states: Optional[torch.FloatTensor],
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        layer_past: Optional[Tuple[torch.Tensor]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = False,
        output_attentions: Optional[bool] = False,
    ) -> Union[
        Tuple[torch.Tensor],
        Optional[Tuple[torch.Tensor, Tuple[torch.FloatTensor, ...]]],
    ]:
        residual = hidden_states
        hidden_states = self.ln_1(hidden_states)
        attn_outputs = self.attn(
            hidden_states=hidden_states,
            layer_past=layer_past,
            attention_mask=attention_mask,
            position_ids=position_ids,
            head_mask=head_mask,
            output_attentions=output_attentions,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_prompt_indices=past_valid_key_prompt_indices,
            past_valid_value_prompt_indices=past_valid_value_prompt_indices,
            past_valid_key_decode_indices=past_valid_key_decode_indices,
            past_valid_value_decode_indices=past_valid_value_decode_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            causal_mask=causal_mask,
            num_beam=num_beam,
            max_new_tokens=max_new_tokens,
            num_real_batch=num_real_batch,
        )
        attn_output = attn_outputs[0]  # output_attn: a, present, (attentions)
        outputs = attn_outputs[1:]

        feed_forward_hidden_states = self.mlp(hidden_states)
        hidden_states = attn_output + feed_forward_hidden_states + residual

        if use_cache:
            outputs = (hidden_states,) + outputs
        else:
            outputs = (hidden_states,) + outputs[1:]

        return outputs  # hidden_states, present, (attentions)


class GPTJPreTrainedModel(PreTrainedModel):
    """
    An abstract class to handle weights initialization and a simple interface for downloading and
    loading pretrained models.
    """

    config_class = GPTJConfig
    base_model_prefix = "transformer"
    supports_gradient_checkpointing = True
    _no_split_modules = ["GPTJBlock"]
    _skip_keys_device_placement = "past_key_values"  # TODO: input_ids 중 skip 해야할 항목 추가필요

    def __init__(self, *inputs, **kwargs):
        super().__init__(*inputs, **kwargs)

    def _init_weights(self, module):
        """Initialize the weights."""
        if isinstance(module, (nn.Linear,)):
            # Slightly different from Mesh Transformer JAX which uses truncated_normal for
            # initialization. cf https://github.com/pytorch/pytorch/pull/5617
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.Embedding):
            module.weight.data.normal_(mean=0.0, std=self.config.initializer_range)
            if module.padding_idx is not None:
                module.weight.data[module.padding_idx].zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)

    def _set_gradient_checkpointing(self, module, value=False):
        if isinstance(module, GPTJModel):
            module.gradient_checkpointing = value


class GPTJModel(HfGPTJModel):
    def __init__(self, config):
        super().__init__(config)

        self.embed_dim = config.n_embd
        self.vocab_size = config.vocab_size
        self.wte = nn.Embedding(config.vocab_size, self.embed_dim)
        self.drop = nn.Dropout(config.embd_pdrop)
        self.h = nn.ModuleList(
            [GPTJBlock(config) for _ in range(config.n_layer - 1)] + [GPTJBlockLast(config)]
        )
        self.ln_f = nn.LayerNorm(self.embed_dim, eps=config.layer_norm_epsilon)

        self.gradient_checkpointing = False

        # Initialize weights and apply final processing
        self.post_init()

    def forward(
        self,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        input_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
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

        if input_ids is not None and inputs_embeds is not None:
            raise ValueError("You cannot specify both input_ids and inputs_embeds at the same time")
        elif input_ids is not None:
            input_shape = input_ids.size()
            input_ids = input_ids.view(-1, input_shape[-1])
            batch_size = input_ids.shape[0]
        elif inputs_embeds is not None:
            input_shape = inputs_embeds.size()[:-1]
            batch_size = inputs_embeds.shape[0]
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
                past_length,
                input_shape[-1] + past_length,
                dtype=torch.long,
                device=device,
            )
            position_ids = position_ids.unsqueeze(0).view(-1, input_shape[-1])

        # Attention mask.
        if attention_mask is not None:
            if batch_size <= 0:
                raise ValueError("batch_size has to be defined and > 0")
            attention_mask = attention_mask.view(batch_size, -1)
            # We create a 3D attention mask from a 2D tensor mask.
            # Sizes are [batch_size, 1, 1, to_seq_length]
            # So we can broadcast to [batch_size, num_heads, from_seq_length, to_seq_length]
            # this attention mask is more simple than the triangular masking of causal attention
            # used in OpenAI GPT, we just need to prepare the broadcast dimension here.
            attention_mask = attention_mask[:, None, None, :]

            # Since attention_mask is 1.0 for positions we want to attend and 0.0 for
            # masked positions, this operation will create a tensor which is 0.0 for
            # positions we want to attend and the dtype's smallest value for masked positions.
            # Since we are adding it to the raw scores before the softmax, this is
            # effectively the same as removing these entirely.
            attention_mask = attention_mask.to(dtype=self.dtype)  # fp16 compatibility
            attention_mask = (1.0 - attention_mask) * torch.finfo(self.dtype).min

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

        if not is_prefill:
            output_shape = input_shape + (hidden_states.size(-1),)
        else:
            # for now, prefill last block slice is not supporting packing
            output_shape = input_shape[:-1] + (
                1,
                hidden_states.size(-1),
            )

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
                    position_ids=position_ids,
                    head_mask=head_mask[i],
                    use_cache=use_cache,
                    output_attentions=output_attentions,
                    new_key_location=new_key_location,
                    new_value_location=new_value_location,
                    past_valid_key_prompt_indices=past_valid_key_prompt_indices,
                    past_valid_value_prompt_indices=past_valid_value_prompt_indices,
                    past_valid_key_decode_indices=past_valid_key_decode_indices,
                    past_valid_value_decode_indices=past_valid_value_decode_indices,
                    bucket_size=bucket_size,
                    is_prefill=is_prefill,
                    causal_mask=causal_mask,
                    num_beam=num_beam,
                    max_new_tokens=max_new_tokens,
                    num_real_batch=num_real_batch,
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
                for v in [
                    hidden_states,
                    presents,
                    all_hidden_states,
                    all_self_attentions,
                ]
                if v is not None
            )

        return BaseModelOutputWithPast(
            last_hidden_state=hidden_states,
            past_key_values=presents,
            hidden_states=all_hidden_states,
            attentions=all_self_attentions,
        )


# cannot reuse huggingface.py since symbolic trace requries root to be gptpretrainedmodel
class GPTJForCausalLM(GPTJPreTrainedModel, CausalLMSymbolicTrace):
    _tied_weights_keys = ["lm_head.weight"]
    has_scores_for_decode_output = True

    def __init__(self, config):
        config.activation_function = "rngd_gelu"
        super().__init__(config)
        self.transformer = GPTJModel(config)
        self.lm_head = nn.Linear(config.n_embd, config.vocab_size)

        # Initialize weights and apply final processing
        self.post_init()

    def get_output_embeddings(self):
        return self.lm_head

    def set_output_embeddings(self, new_embeddings):
        self.lm_head = new_embeddings

    def forward(
        self,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        input_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[Tuple[Tuple[torch.Tensor]]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        token_type_ids: Optional[torch.LongTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        labels: Optional[torch.LongTensor] = None,
        use_cache: Optional[bool] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        return_dict: Optional[bool] = None,
    ) -> Union[Tuple, CausalLMOutputWithPast]:
        r"""
        labels (`torch.LongTensor` of shape `(batch_size, sequence_length)`, *optional*):
            Labels for language modeling. Note that the labels **are shifted** inside the model,
            i.e. you can set `labels = input_ids` Indices are selected in
            `[-100, 0, ..., config.vocab_size]` All labels set to `-100` are ignored (masked),
            the loss is only computed for labels in `[0, ..., config.vocab_size]`
        """
        return_dict = return_dict if return_dict is not None else self.config.use_return_dict

        transformer_outputs = self.transformer(
            input_ids=input_ids,
            past_key_values=past_key_values,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
            position_ids=position_ids,
            head_mask=head_mask,
            inputs_embeds=inputs_embeds,
            use_cache=use_cache,
            output_attentions=output_attentions,
            output_hidden_states=output_hidden_states,
            return_dict=return_dict,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_prompt_indices=past_valid_key_prompt_indices,
            past_valid_value_prompt_indices=past_valid_value_prompt_indices,
            past_valid_key_decode_indices=past_valid_key_decode_indices,
            past_valid_value_decode_indices=past_valid_value_decode_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            causal_mask=causal_mask,
            num_beam=num_beam,
            max_new_tokens=max_new_tokens,
            num_real_batch=num_real_batch,
        )
        hidden_states = transformer_outputs[0]

        # make sure sampling in fp16 works correctly and
        # compute loss in fp32 to match with mesh-tf version
        # https://github.com/EleutherAI/gpt-neo/blob/89ce74164da2fb16179106f54e2269b5da8db333/models/gpt2/gpt2.py#L179
        lm_logits = self.lm_head(hidden_states).to(torch.float32)

        # with prefill last block slice log_softmax is computed in npu
        # need to implement related generator in the future
        next_token_scores = torch.nn.functional.log_softmax(lm_logits, dim=-1)
        return (next_token_scores,)

        # if not is_prefill:
        #     # This works with has_logits_in_model_output=False in
        #     # ..generators.paged_attention_optimized_generator_beam_search.PagedAttentionGeneratorBeamSearch # noqa
        #     # For detailed explanation, see the following link:
        #     # https://linear.app/furiosa-ai/issue/LLM-368/mlperf-gptj-beam-search의-softmax-를-logits-전체를-host에서-하는것이-아닌-npu에서
        #     next_token_scores = torch.nn.functional.log_softmax(lm_logits[:, -1], dim=-1)
        #     return (next_token_scores,)

        # return (lm_logits,)

    def get_input_names_and_concrete_args(
        self, model, prefill_phase=True
    ) -> Tuple[List[str], Dict]:
        model = self

        if prefill_phase:
            input_names = [
                "input_ids",
                "position_ids",
                "past_key_values",
                "causal_mask",
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
                "past_valid_key_prompt_indices",
                "past_valid_key_decode_indices",
                "past_valid_value_prompt_indices",
                "past_valid_value_decode_indices",
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
                "num_beam": NUM_BEAMS,
                "max_new_tokens": MAX_NEW_TOKENS,
                "num_real_batch": NUM_REAL_BATCH,
            }
        else:
            custom_concrete_args = {
                "use_cache": False,
                "return_dict": True,
                "output_attentions": False,
                "output_hidden_states": False,
                "is_prefill": False,
                "num_beam": NUM_BEAMS,
                "max_new_tokens": MAX_NEW_TOKENS,
                "num_real_batch": NUM_REAL_BATCH,
            }

        for arg in custom_concrete_args:
            if arg in concrete_args:
                concrete_args[arg] = custom_concrete_args[arg]
                continue
            raise ValueError(f"{arg} is not defined in {concrete_args}")

        return input_names, concrete_args


class GPTJBlockLast(nn.Module):
    def __init__(self, config):
        super().__init__()
        inner_dim = config.n_inner if config.n_inner is not None else 4 * config.n_embd
        self.ln_1 = nn.LayerNorm(config.n_embd, eps=config.layer_norm_epsilon)
        self.attn = NewGPTJAttentionLast(config)
        self.mlp = HfGPTJMLP(inner_dim, config)

    def forward(
        self,
        hidden_states: Optional[torch.FloatTensor],
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        layer_past: Optional[Tuple[torch.Tensor]] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        use_cache: Optional[bool] = False,
        output_attentions: Optional[bool] = False,
    ) -> Union[
        Tuple[torch.Tensor],
        Optional[Tuple[torch.Tensor, Tuple[torch.FloatTensor, ...]]],
    ]:
        # for now, prefill last block slice is not supporting packing
        residual = hidden_states[:, -1:, :]
        hidden_states = self.ln_1(hidden_states)
        attn_outputs = self.attn(
            hidden_states=hidden_states,
            layer_past=layer_past,
            attention_mask=attention_mask,
            position_ids=position_ids,
            head_mask=head_mask,
            output_attentions=output_attentions,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_prompt_indices=past_valid_key_prompt_indices,
            past_valid_value_prompt_indices=past_valid_value_prompt_indices,
            past_valid_key_decode_indices=past_valid_key_decode_indices,
            past_valid_value_decode_indices=past_valid_value_decode_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            causal_mask=causal_mask,
            num_beam=num_beam,
            max_new_tokens=max_new_tokens,
            num_real_batch=num_real_batch,
        )
        attn_output = attn_outputs[0]  # output_attn: a, present, (attentions)
        outputs = attn_outputs[1:]

        # for now, prefill last block slice is not supporting packing
        feed_forward_hidden_states = self.mlp(hidden_states[:, -1:, :])
        hidden_states = attn_output + feed_forward_hidden_states + residual

        if use_cache:
            outputs = (hidden_states,) + outputs
        else:
            outputs = (hidden_states,) + outputs[1:]

        return outputs  # hidden_states, present, (attentions)


class NewGPTJAttentionLast(FastGPTJAttention):
    def forward(
        self,
        hidden_states: torch.FloatTensor,
        new_key_location: torch.IntTensor,
        new_value_location: torch.IntTensor,
        bucket_size: int,
        is_prefill: bool,
        num_beam: int,
        num_real_batch: int,
        max_new_tokens: int,
        layer_past: Tuple[Tuple[torch.Tensor, torch.Tensor], ...],
        past_valid_key_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_key_decode_indices: Optional[torch.IntTensor] = None,
        past_valid_value_prompt_indices: Optional[torch.IntTensor] = None,
        past_valid_value_decode_indices: Optional[torch.IntTensor] = None,
        causal_mask: Optional[torch.BoolTensor] = None,
        attention_mask: Optional[torch.FloatTensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_mask: Optional[torch.FloatTensor] = None,
        output_attentions: bool = False,
    ) -> Tuple[torch.Tensor]:
        # for now, prefill last block slice is not supporting packing
        q_hidden_states = hidden_states[:, -1:, :]
        query = self.q_proj(q_hidden_states)
        key = self.k_proj(hidden_states)
        value = self.v_proj(hidden_states)

        query = self._split_heads(query, self.num_attention_heads, self.head_dim, True)
        key = self._split_heads(key, self.num_attention_heads, self.head_dim, True)
        value = self._split_heads(value, self.num_attention_heads, self.head_dim, False)

        query, key = self.apply_rope(query, key, position_ids)

        key, value = kv_paged_update_beam(
            present_key=key,
            present_value=value,
            past_key_value=layer_past,
            new_key_location=new_key_location,
            new_value_location=new_value_location,
            past_valid_key_prompt_indices=past_valid_key_prompt_indices,
            past_valid_value_prompt_indices=past_valid_value_prompt_indices,
            past_valid_key_decode_indices=past_valid_key_decode_indices,
            past_valid_value_decode_indices=past_valid_value_decode_indices,
            bucket_size=bucket_size,
            is_prefill=is_prefill,
            num_beam=num_beam,
            max_new_tokens=max_new_tokens,
            head_first=False,
            num_real_batch=num_real_batch,
        )

        present_key_value = None

        # for this optimized version, attn computation differs from original attn
        # so we use a custom attn method
        attn_dropout = self.attn_dropout
        # in the long term, causal_mask should be passed as input argument not keyword argument
        # self.bias should not be initialized as it is not used
        scale_attn = self.scale_attn

        attn_weights = torch.matmul(query, key.transpose(-1, -2))
        if is_prefill:
            # prefill, no attention mask
            assert attention_mask is None
            # Because this typecasting will cause accuracy degradation, we want this typecasting to
            # occur in MCM_matmul module that performs matmul.
            # query = query.to(torch.float32)
            # key = key.to(torch.float32)
            mask_value = torch.finfo(attn_weights.dtype).min
            # Need to be a tensor, otherwise we get error: `RuntimeError: expected scalar type float
            # but found double`.
            # Need to be on the same device, otherwise
            #   `RuntimeError: ..., x and y to be on the same device`
            mask_value = torch.tensor(mask_value, dtype=attn_weights.dtype).to(attn_weights.device)
            # at this point, causal_mask should be expanded to [batch, head, seq_len, seq_len]
            # for now, prefill last block slice is not supporting packing
            causal_mask = causal_mask[:, None, causal_mask.shape[1] - query.shape[2] :, :]
            causal_mask = (1 - causal_mask.to(attn_weights.dtype)) * mask_value
            # attn_weights = torch.where(causal_mask, attn_weights, mask_value)
            attn_weights = attn_weights / scale_attn
            attn_weights = attn_weights + causal_mask
        else:
            # decode, no need for causal mask
            assert causal_mask is None
            # Because this typecasting will cause accuracy degradation, we want this typecasting to
            # occur in MCM_matmul module that performs matmul.
            # query = query.to(torch.float32)
            # key = key.to(torch.float32)
            attn_weights = attn_weights / scale_attn
            attn_weights = attn_weights + attention_mask

        attn_weights = torch.nn.functional.softmax(attn_weights, dim=-1)
        # we restrict the softmax output to be in bfloat16 in quantized model, i.e., in W8A8KV8
        # model where value.dtype == int8 is true, the code below will typecast score to int8 and
        # thus cause significant accuracy degradation.
        # attn_weights = attn_weights.to(value.dtype)
        attn_weights = attn_dropout(attn_weights)
        # Mask heads if we want to
        if head_mask is not None:
            attn_weights = attn_weights * head_mask
        attn_output = torch.matmul(attn_weights, value)

        attn_output = self._merge_heads(attn_output, self.num_attention_heads, self.head_dim)
        attn_output = self.out_proj(attn_output)
        attn_output = self.resid_dropout(attn_output)

        outputs = (attn_output, present_key_value)
        if output_attentions:
            outputs += (attn_weights,)

        return outputs
