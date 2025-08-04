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
"""PyTorch LLaMA model."""

from typing import Optional, Tuple

import torch
from transformers.utils import logging

from .huggingface import LlamaAttention, LlamaForCausalLM

logger = logging.get_logger(__name__)


class LlamaRotaryEmbedding(torch.nn.Module):
    def __init__(self, dim, max_position_embeddings=2048, base=10000, device=None):
        super().__init__()

        self.dim = dim
        self.max_position_embeddings = max_position_embeddings
        self.base = base
        inv_freq = 1.0 / (self.base ** (torch.arange(0, self.dim, 2).float().to(device) / self.dim))
        self.register_buffer("inv_freq", inv_freq)

        # Build here to make `torch.jit.trace` work.
        self._set_cos_sin_cache(
            seq_len=max_position_embeddings,
            device=self.inv_freq.device,
        )

    def _set_cos_sin_cache(self, seq_len, device):
        self.max_seq_len_cached = seq_len
        t = torch.arange(self.max_seq_len_cached, device=device, dtype=self.inv_freq.dtype)

        # Always use float32 for sincos
        freqs = torch.einsum("i,j->ij", t, self.inv_freq).float()
        # Different from paper, but it uses a different permutation
        # in order to obtain the same calculation
        self._set_cache_from_freqs(freqs)

    def _set_cache_from_freqs(self, freqs):
        max_pos, dim = freqs.shape
        sin = freqs.sin().unsqueeze(dim=1)  # [max_pos, 1, dim]
        cos = freqs.cos().unsqueeze(dim=1)  # [max_pos, 1, dim]
        sincos = torch.cat([cos, -sin, sin, cos], dim=1)  # [max_pos, 4, dim]
        sincos = sincos.permute(0, 2, 1)  # [max_pos, dim, 4]
        self.register_buffer("sincos_cached", sincos.reshape(max_pos, dim, 2, 2), persistent=False)

    def forward(self, x, seq_len=None):
        # x: [bs, num_attention_heads, seq_len, head_size]
        if seq_len > self.max_seq_len_cached:
            self._set_cos_sin_cache(seq_len=seq_len, device=x.device)

        return self.sincos_cached[:seq_len]


class LlamaLinearScalingRotaryEmbedding(LlamaRotaryEmbedding):
    """LlamaRotaryEmbedding extended with linear scaling.
    Credits to the Reddit user /u/kaiokendev"""

    def __init__(
        self, dim, max_position_embeddings=2048, base=10000, device=None, scaling_factor=1.0
    ):
        self.scaling_factor = scaling_factor
        super().__init__(dim, max_position_embeddings, base, device)

    def _set_cos_sin_cache(self, seq_len, device):
        self.max_seq_len_cached = seq_len
        t = torch.arange(self.max_seq_len_cached, device=device, dtype=self.inv_freq.dtype)
        t = t / self.scaling_factor

        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        # Different from paper, but it uses a different permutation
        # in order to obtain the same calculation
        self._set_cache_from_freqs(freqs)


class LlamaDynamicNTKScalingRotaryEmbedding(LlamaRotaryEmbedding):
    """LlamaRotaryEmbedding extended with Dynamic NTK scaling.
    Credits to the Reddit users /u/bloc97 and /u/emozilla"""

    def __init__(
        self, dim, max_position_embeddings=2048, base=10000, device=None, scaling_factor=1.0
    ):
        self.scaling_factor = scaling_factor
        super().__init__(dim, max_position_embeddings, base, device)

    def _set_cos_sin_cache(self, seq_len, device):
        self.max_seq_len_cached = seq_len

        if seq_len > self.max_position_embeddings:
            base = self.base * (
                (self.scaling_factor * seq_len / self.max_position_embeddings)
                - (self.scaling_factor - 1)
            ) ** (self.dim / (self.dim - 2))
            inv_freq = 1.0 / (base ** (torch.arange(0, self.dim, 2).float().to(device) / self.dim))
            self.register_buffer("inv_freq", inv_freq)

        t = torch.arange(self.max_seq_len_cached, device=device, dtype=self.inv_freq.dtype)

        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        # Different from paper, but it uses a different permutation
        # in order to obtain the same calculation
        self._set_cache_from_freqs(freqs)


def apply_rotary_pos_emb(q, k, sincos, position_ids):
    def apply(tensor, sincos):
        batch, num_head, seq_len, rotary_dim = tensor.shape
        # sincos always have dtype float32. We need to cast tensor to float32 to avoid accuracy
        # degradation.
        activation = tensor.reshape(batch, num_head, seq_len, 2, rotary_dim // 2).to(sincos.dtype)
        einsum = torch.einsum("bsfij,bhsjf->bhsif", sincos, activation)
        # get back to the original dtype
        return einsum.reshape(batch, num_head, seq_len, -1).to(tensor.dtype)

    sincos_proj = sincos[position_ids]  # [bs, seq_len, dim, 2, 2]
    return apply(q, sincos_proj), apply(k, sincos_proj)


class FastLlamaAttention(LlamaAttention):
    def _init_rope(self):
        if self.config.rope_scaling is None:
            self.rotary_emb = LlamaRotaryEmbedding(
                self.head_dim, max_position_embeddings=self.max_position_embeddings
            )
        else:
            scaling_type = self.config.rope_scaling["type"]
            scaling_factor = self.config.rope_scaling["factor"]
            if scaling_type == "linear":
                self.rotary_emb = LlamaLinearScalingRotaryEmbedding(
                    self.head_dim,
                    max_position_embeddings=self.max_position_embeddings,
                    scaling_factor=scaling_factor,
                )
            elif scaling_type == "dynamic":
                self.rotary_emb = LlamaDynamicNTKScalingRotaryEmbedding(
                    self.head_dim,
                    max_position_embeddings=self.max_position_embeddings,
                    scaling_factor=scaling_factor,
                )
            else:
                raise ValueError(f"Unknown RoPE scaling type {scaling_type}")

    def apply_rope(
        self,
        query_states: torch.Tensor,
        key_states: torch.Tensor,
        value_states: torch.Tensor,
        kv_seq_len: Optional[int] = None,
        position_ids: Optional[torch.LongTensor] = None,
        head_first: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        sincos = self.rotary_emb(value_states, seq_len=kv_seq_len)
        query_states, key_states = apply_rotary_pos_emb(
            query_states, key_states, sincos, position_ids
        )

        if not head_first:
            key_states = key_states.transpose(1, 2)

        return query_states, key_states


class MLPerfROPELlamaForCausalLM(LlamaForCausalLM):
    def __init__(self, config):
        super().__init__(config)
        for layer in self.model.layers:
            layer.self_attn = FastLlamaAttention(config)


LlamaForCausalLM = MLPerfROPELlamaForCausalLM
