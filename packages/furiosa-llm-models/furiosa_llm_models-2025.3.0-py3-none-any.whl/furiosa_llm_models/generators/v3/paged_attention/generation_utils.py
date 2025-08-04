from typing import Dict, List, Optional, Tuple

import torch
from transformers import (
    GPTJConfig,
    LlamaConfig,
    MistralConfig,
    PretrainedConfig,
)


def get_model_dimensions(config: PretrainedConfig) -> Tuple[int, int, int]:
    if isinstance(config, GPTJConfig):
        num_heads = config.n_head
        embedding_dim = config.n_embd
        num_layers = config.n_layer
        head_size = int(embedding_dim / num_heads)
    elif isinstance(config, LlamaConfig):
        num_heads = config.num_attention_heads
        embedding_dim = config.hidden_size
        head_size = int(embedding_dim / num_heads)
        # Adjust num_heads if attention is grouped-query attention (GQA)
        if num_heads > config.num_key_value_heads:
            num_heads = config.num_key_value_heads
        num_layers = config.num_hidden_layers
    elif isinstance(config, MistralConfig):
        num_heads = config.num_attention_heads
        embedding_dim = config.hidden_size
        head_size = config.head_dim
        # Adjust num_heads if attention is grouped-query attention (GQA)
        if num_heads > config.num_key_value_heads:
            num_heads = config.num_key_value_heads
        num_layers = config.num_hidden_layers
    else:
        raise ValueError(f"Unsupported config type: {type(config)}")
    return num_layers, num_heads, head_size


def get_key_value_blocks(
    num_layers: int,
    num_heads: int,
    head_size: int,
    num_blocks: int,
    block_size: int,
    kv_dtype: torch.dtype = torch.float32,
    device: torch.device = torch.device("cpu"),
    device_map: Optional[Dict] = None,
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    # Example
    # num_layers = 2
    # num_heads = 8
    # head_size = 64
    # num_blocks = 129 (1 + 2 * 16 (bucket_size) * 4 (batch_size))
    # block_size = 16
    # block_shape = (129, 16, 8, 64)
    block_shape = (
        num_blocks,
        block_size,
        num_heads,
        head_size,
    )

    key_value_blocks = []
    for layer_idx in range(num_layers):
        if device_map is not None and len(device_map) > 0:
            device = device_map[str(layer_idx)]

        key_value_blocks.append(
            (
                # key shape: (num_blocks, block_size, num_heads, head_size) = (129, 16, 8, 64)
                torch.zeros(block_shape, dtype=kv_dtype).to(device),
                # value shape: (num_blocks, block_size, num_heads, head_size) = (129, 16, 8, 64)
                torch.zeros(block_shape, dtype=kv_dtype).to(device),
            )
        )
    return key_value_blocks


def create_key_value_blocks(
    model_config: PretrainedConfig,
    bucket_size: int,
    batch_size: int,
    kv_dtype: torch.dtype,
    block_size: int,
    device: torch.device,
    device_map: Optional[Dict] = None,
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    num_layers, num_heads, head_size = get_model_dimensions(model_config)

    # num_blocks = 1 (dummy pad token) + bucket_size (max_length) * batch_size * 2 (for each key and value) # noqa
    # Example
    # bucket_size = 16
    # batch_size = 4
    # num_blocks = 1 + 2 * 16 * 4 = 129
    num_blocks = 1 + 2 * bucket_size * batch_size

    key_value_blocks = get_key_value_blocks(
        num_layers,
        num_heads,
        head_size,
        num_blocks,
        block_size,
        kv_dtype=kv_dtype,
        device=device,
        device_map=device_map,
    )
    if len(key_value_blocks) != num_layers:
        raise ValueError(
            f"Key-value blocks should be created for all layers. Got len(key_value_blocks): \
                {len(key_value_blocks)} != num_layers: {num_layers}"
        )

    return key_value_blocks
