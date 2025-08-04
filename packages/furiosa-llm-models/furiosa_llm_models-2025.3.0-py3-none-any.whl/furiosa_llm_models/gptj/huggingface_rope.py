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
from transformers.utils import is_torch_fx_proxy, logging

from .huggingface import GPTJAttention, GPTJForCausalLM, get_embed_positions

logger = logging.get_logger(__name__)


def create_sinusoidal_positions(num_pos: int, dim: int) -> torch.Tensor:
    inv_freq = 1.0 / (10000 ** (torch.arange(0, dim, 2) / dim))
    sinusoid_inp = torch.einsum(
        "i , j -> i j", torch.arange(num_pos, dtype=torch.float), inv_freq
    ).float()
    # shape should be as [cos0, -sin0, sin0, cos0]
    cos_top = torch.cos(sinusoid_inp).unsqueeze(dim=1)
    minus_sin = -torch.sin(sinusoid_inp).unsqueeze(dim=1)
    sin = torch.sin(sinusoid_inp).unsqueeze(dim=1)
    cos_bot = torch.cos(sinusoid_inp).unsqueeze(dim=1)
    return (
        torch.cat([cos_top, minus_sin, sin, cos_bot], dim=1)
        .permute(0, 2, 1)
        .reshape(num_pos, cos_top.size(-1) * 4)
    )


def apply_rotary_pos_emb(tensor: torch.Tensor, sincos: torch.Tensor) -> torch.Tensor:
    batch, seq_len, num_head, rotary_dim = tensor.shape
    # sincos always have dtype float32. We need to cast tensor to float32 to avoid accuracy
    # degradation.
    activation = tensor.reshape(batch, seq_len, num_head, rotary_dim // 2, 2).to(sincos.dtype)
    einsum = torch.einsum(
        "bsfij,bshfj-> bshfi", sincos[:, sincos.shape[1] - seq_len :, :, :, :], activation
    )
    # get back to the original dtype
    return einsum.reshape(batch, seq_len, num_head, -1).to(tensor.dtype)


class FastGPTJAttention(GPTJAttention):
    def __init__(self, config):
        super().__init__(config)
        max_positions = config.max_position_embeddings
        pos_embd_dim = self.rotary_dim or self.embed_dim
        self.embed_positions = create_sinusoidal_positions(max_positions, pos_embd_dim)

    def apply_rope(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        position_ids: Optional[torch.LongTensor] = None,
        head_first: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        if is_torch_fx_proxy(position_ids) or torch.jit.is_tracing():
            # The logic to conditionally copy to GPU could not be traced, so we do this
            # every time in the torch.fx case
            embed_positions = get_embed_positions(self.embed_positions, position_ids)
        else:
            embed_positions = self._get_embed_positions(position_ids)

        repeated_position_ids = position_ids.unsqueeze(-1).repeat(1, 1, embed_positions.shape[-1])
        sincos = torch.gather(embed_positions, 1, repeated_position_ids)
        sincos = sincos.reshape(sincos.size(0), sincos.size(1), sincos.size(-1) // 4, 2, 2)

        if self.rotary_dim is not None:
            k_rot = key[:, :, :, : self.rotary_dim]
            k_pass = key[:, :, :, self.rotary_dim :]

            q_rot = query[:, :, :, : self.rotary_dim]
            q_pass = query[:, :, :, self.rotary_dim :]

            k_rot = apply_rotary_pos_emb(k_rot, sincos)
            q_rot = apply_rotary_pos_emb(q_rot, sincos)

            key = torch.cat([k_rot, k_pass], dim=-1)
            query = torch.cat([q_rot, q_pass], dim=-1)
        else:
            key = apply_rotary_pos_emb(key, sincos)
            query = apply_rotary_pos_emb(query, sincos)

        if head_first:
            # key is permuted to [batch, head, seq_len, head_dim]
            key = key.permute(0, 2, 1, 3)

        # query should always be head first
        # query is permuted to [batch, head, seq_len, head_dim]
        query = query.permute(0, 2, 1, 3)

        return query, key


class MLPerfROPEGPTJForCausalLM(GPTJForCausalLM):
    def __init__(self, config):
        super().__init__(config)
        for layer in self.transformer.h:
            layer.attn = FastGPTJAttention(config)


GPTJForCausalLM = MLPerfROPEGPTJForCausalLM
