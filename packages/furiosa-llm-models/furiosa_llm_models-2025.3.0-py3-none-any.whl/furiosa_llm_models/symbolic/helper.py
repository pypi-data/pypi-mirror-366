import abc
from typing import Dict, List, Tuple

import torch
from torch.fx import GraphModule
from transformers import PreTrainedModel
from transformers.utils.fx import HFTracer

# Below values are used for symbolic tracing and should be separated from generator values
BUCKET_SIZE = 2048
MAX_BATCH_SIZE = 4
NUM_BEAMS = 2
MAX_NEW_TOKENS = 128
NUM_REAL_BATCH = 1


class SymbolicTraceBase(abc.ABC):
    def trace(self, disable_check: bool = False, **kwargs) -> GraphModule:
        """
        Helper function to trace the model in symbolic mode.
        """
        model_to_trace = self
        input_names, concrete_args = self.get_input_names_and_concrete_args(
            model_to_trace, **kwargs
        )

        # if not disable_check:
        #     check_if_model_is_supported(model)

        # Tracing.
        tracer = CustomHFTracer()

        traced_graph = tracer.trace(model_to_trace, concrete_args=concrete_args)
        traced = torch.fx.GraphModule(model_to_trace, traced_graph)

        traced.config = model_to_trace.config
        traced.generation_config = model_to_trace.generation_config
        traced.input_names = input_names
        traced.concrete_args = concrete_args

        model_class = model_to_trace.__class__
        traced.module_name = model_class.__module__ + "." + model_class.__name__

        # The model class must be stored as an attribute to allow model deserialization,
        # which uses trace, and thus
        # _generate_dummy_input, where the model class is needed.
        traced.class_for_deserialization = model_class
        traced.device = model_to_trace.device
        # This is an attribute that is used to determine whether the model has scores for decode output. # noqa
        # It is only True for gptj.symbolic.paged_attention_optimized_packed_rope_erf_gelu.GPTJForCausalLM. # noqa
        # FIXME: This is a hacky way to handle this.
        try:
            traced.has_scores_for_decode_output = model_to_trace.has_scores_for_decode_output
        except AttributeError:
            traced.has_scores_for_decode_output = False
        traced.device_map = getattr(model_to_trace, "hf_device_map", None)
        return traced

    @abc.abstractmethod
    def get_input_names_and_concrete_args(
        self, model: PreTrainedModel, prefill_phase: bool = True
    ) -> Tuple[List[str], Dict]:
        pass


class CausalLMSymbolicTrace(SymbolicTraceBase):
    def trace_all(self, disable_check: bool = False) -> Dict[str, GraphModule]:
        """
        Helper function to trace both prefill and decode modes.
        """
        return {
            "prefill": self.trace_prefill(),
            "decode": self.trace_decode(),
        }

    def trace_prefill(self, disable_check: bool = False) -> GraphModule:
        """
        Helper function to trace prefill mode.
        """
        return self.trace(prefill_phase=True, disable_check=False)

    def trace_decode(self, disable_check: bool = False) -> GraphModule:
        """
        Helper function to trace decode mode.
        """
        return self.trace(prefill_phase=False, disable_check=False)


class QuestionAnsweringSymbolicTrace(SymbolicTraceBase):
    def trace_model(self, disable_check: bool = False) -> Dict[str, GraphModule]:
        """
        Helper function to trace all modes
        """

        return self.trace(disable_check=disable_check)


class CustomHFTracer(HFTracer):
    def _generate_dummy_input(
        self, model: "PreTrainedModel", input_name: str, shape: List[int], input_names: List[str]
    ) -> Dict[str, torch.Tensor]:
        """Generates dummy input for model inference recording."""

        device = model.device
        inputs_dict = {}

        kv_cache_length = 5

        if "mask" in input_name:
            if "past_key_values" in input_names:
                mask_shape = [shape[0], shape[1] + kv_cache_length]
            else:
                mask_shape = shape

            inputs_dict[input_name] = torch.zeros(mask_shape, dtype=torch.long, device=device)
        elif "ids" in input_name:
            inputs_dict[input_name] = torch.zeros(shape, dtype=torch.long, device=device)
        else:
            shape_with_hidden_size = shape + [model.config.hidden_size]
            inputs_dict[input_name] = torch.zeros(
                shape_with_hidden_size, dtype=torch.float, device=device
            )

        return inputs_dict
