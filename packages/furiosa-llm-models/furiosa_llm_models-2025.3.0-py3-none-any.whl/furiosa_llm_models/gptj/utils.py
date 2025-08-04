from typing import Optional

from .huggingface import GPTJAttention, GPTJForCausalLM, GPTJModel


def renew_attention_module(
    new_attn: GPTJAttention,
    new_model: Optional[GPTJModel] = None,
    parent_class: GPTJForCausalLM = GPTJForCausalLM,
) -> GPTJForCausalLM:
    class NewGPTJForCausalLM(parent_class):
        def __init__(self, config):
            super().__init__(config)
            if new_model is not None:
                self.transformer = new_model(config)
            for layer in self.transformer.h:
                layer.attn = new_attn(config)

    return NewGPTJForCausalLM
