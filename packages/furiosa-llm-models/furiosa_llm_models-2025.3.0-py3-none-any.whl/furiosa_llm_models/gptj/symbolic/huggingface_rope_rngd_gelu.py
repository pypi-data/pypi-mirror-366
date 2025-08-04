from .huggingface_rope import GPTJForCausalLM


class GPTJForCausalLM(GPTJForCausalLM):
    _tied_weights_keys = ["lm_head.weight"]

    def __init__(self, config):
        # Call "rngd_gelu" activation function defined in furiosa_llm_models/gptj/activations.py
        config.activation_function = "rngd_gelu"
        super().__init__(config)
