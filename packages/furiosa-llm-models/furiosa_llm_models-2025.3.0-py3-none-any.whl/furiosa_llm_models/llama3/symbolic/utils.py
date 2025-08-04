import os
from collections import OrderedDict
from typing import Optional, Union

from transformers import PretrainedConfig

"""Returns exaone to llama mapping function"""


def get_exaone_mapping_func():
    return {
        "transformer": "model",
        ".h.": ".layers.",
        "ln_1": "input_layernorm",
        "ln_2": "post_attention_layernorm",
        "ln_f": "norm",
        "wte": "embed_tokens",
        "c_fc_0": "gate_proj",
        "c_fc_1": "up_proj",
        "c_proj": "down_proj",
        "rotary": "rotary_emb",
        ".attn.attention.": ".self_attn.",
        "out_proj": "o_proj",
    }


"""Retrieves exaone model information and converts ckpt using exaone_mapping_func"""


def get_exaone_infos(
    pretrained_model_name_or_path: Optional[Union[str, os.PathLike]],
    *model_args,
    config: Optional[Union[PretrainedConfig, str, os.PathLike]] = None,
    cache_dir: Optional[Union[str, os.PathLike]] = None,
    ignore_mismatched_sizes: bool = False,
    force_download: bool = False,
    local_files_only: bool = False,
    token: Optional[Union[str, bool]] = None,
    revision: str = "main",
    use_safetensors: bool = None,
    **kwargs,
):
    if pretrained_model_name_or_path not in [
        "LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct",
        "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
        "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
        "LGAI-EXAONE/EXAONE-3.5-32B-Instruct",
        "LGAI-EXAONE/EXAONE-Deep-2.4B",
        "LGAI-EXAONE/EXAONE-Deep-7.8B",
        "LGAI-EXAONE/EXAONE-Deep-32B",
    ]:
        return {
            "torch_dtype": None,
            "conversion_func": dict(),
            "original_config": None,
            "exaone_state_dict": OrderedDict(),
        }
    else:
        from transformers import AutoModelForCausalLM as HFAutoModelForCausalLM

        conversion_func = dict()
        hf_model = HFAutoModelForCausalLM.from_pretrained(
            pretrained_model_name_or_path=pretrained_model_name_or_path,
            *model_args,
            config=config,
            cache_dir=cache_dir,
            ignore_mismatched_sizes=ignore_mismatched_sizes,
            force_download=force_download,
            local_files_only=local_files_only,
            token=token,
            revision=revision,
            use_safetensors=use_safetensors,
            **kwargs,
        )

        state_dict = hf_model.state_dict()
        mapping_func = get_exaone_mapping_func()

        keys = list(state_dict.keys())
        for old_key in keys:
            new_key = old_key
            for key in mapping_func:
                new_key = new_key.replace(key, mapping_func[key])
            if new_key != old_key:
                state_dict[new_key] = state_dict.pop(old_key)
            conversion_func[old_key] = new_key
        return {
            "torch_dtype": hf_model.dtype,
            "conversion_func": conversion_func,
            "original_config": hf_model.config,
            "exaone_state_dict": state_dict,
        }


class LlamaBasedModelConverter:
    @classmethod
    def from_huggingface(
        cls,
        pretrained_model_name_or_path: Optional[Union[str, os.PathLike]],
        *model_args,
        config: Optional[Union[PretrainedConfig, str, os.PathLike]] = None,
        cache_dir: Optional[Union[str, os.PathLike]] = None,
        ignore_mismatched_sizes: bool = False,
        force_download: bool = False,
        local_files_only: bool = False,
        token: Optional[Union[str, bool]] = None,
        revision: str = "main",
        use_safetensors: bool = None,
        **kwargs,
    ):
        conversion_func = {}
        supported_models = {
            "exaone": [
                "LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct",
                "LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct",
                "LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct",
                "LGAI-EXAONE/EXAONE-3.5-32B-Instruct",
                "LGAI-EXAONE/EXAONE-Deep-2.4B",
                "LGAI-EXAONE/EXAONE-Deep-7.8B",
                "LGAI-EXAONE/EXAONE-Deep-32B",
            ]
        }
        supported_model_list = [model for models in supported_models.values() for model in models]

        # If this is not LGAI-EXAONE, proceed as usual
        if pretrained_model_name_or_path not in supported_model_list:
            raise ValueError(
                f"'from_huggingface' does not support '{pretrained_model_name_or_path}'."
                f"Please provide a valid model name from the list: {supported_model_list}."
            )
        else:
            # 1. get checkpoint & llamify it. (cpu)
            exaone_infos = get_exaone_infos(
                pretrained_model_name_or_path=pretrained_model_name_or_path,
                *model_args,
                config=config,
                cache_dir=cache_dir,
                ignore_mismatched_sizes=ignore_mismatched_sizes,
                force_download=force_download,
                local_files_only=local_files_only,
                token=token,
                revision=revision,
                use_safetensors=use_safetensors,
                **kwargs,
            )
            torch_dtype = exaone_infos["torch_dtype"]
            conversion_func = exaone_infos["conversion_func"]
            original_config = exaone_infos["original_config"]
            state_dict = exaone_infos["exaone_state_dict"]

            # 2. Change config
            from transformers import LlamaConfig

            new_exaone_config = LlamaConfig(
                vocab_size=original_config.vocab_size,
                hidden_size=original_config.hidden_size,
                intermediate_size=original_config.intermediate_size,
                num_hidden_layers=original_config.num_layers,
                num_attention_heads=original_config.num_attention_heads,
                max_position_embeddings=original_config.max_position_embeddings,
                rms_norm_eps=original_config.layer_norm_epsilon,
                num_key_value_heads=original_config.num_key_value_heads,
                rope_scaling=original_config.rope_scaling,
                rope_theta=original_config.rope_theta,
                bos_token_id=original_config.bos_token_id,
                eos_token_id=original_config.eos_token_id,
                pad_token_id=original_config.pad_token_id,
                attention_bias=False,
            )
            new_exaone_config.architectures = ["LlamaForCausalLM"]
            new_exaone_config.torch_dtype = torch_dtype

            # Furiosa specific: we currently utilize inv_freq_config for rope scaling
            if new_exaone_config.rope_scaling is not None:
                new_exaone_config.inv_freq_config = new_exaone_config.rope_scaling
                new_exaone_config.rope_scaling = None

            # 3. Load our model
            kwargs["state_dict"] = state_dict
            del kwargs["trust_remote_code"]
            model = cls.from_pretrained(
                pretrained_model_name_or_path=None,
                *model_args,
                config=new_exaone_config,
                cache_dir=cache_dir,
                ignore_mismatched_sizes=ignore_mismatched_sizes,
                force_download=force_download,
                local_files_only=local_files_only,
                token=token,
                revision=revision,
                use_safetensors=use_safetensors,
                **kwargs,
            )

        return model, conversion_func
