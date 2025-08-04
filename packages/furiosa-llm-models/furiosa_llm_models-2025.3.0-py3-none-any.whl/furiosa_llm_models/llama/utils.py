from typing import Optional

from .huggingface import LlamaAttention, LlamaForCausalLM, LlamaModel


def renew_attention_module(
    new_attn: LlamaAttention,
    new_model: Optional[LlamaModel] = None,
    parent_class: LlamaForCausalLM = LlamaForCausalLM,
) -> LlamaForCausalLM:
    class NewLlamaForCausalLM(parent_class):
        def __init__(self, config):
            super().__init__(config)
            if new_model is not None:
                self.model = new_model(config)
            for layer in self.model.layers:
                layer.self_attn = new_attn(config)

    return NewLlamaForCausalLM
