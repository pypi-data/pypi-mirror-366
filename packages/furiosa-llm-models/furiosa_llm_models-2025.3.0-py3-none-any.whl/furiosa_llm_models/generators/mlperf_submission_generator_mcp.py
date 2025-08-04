# TODO(A separate beam search module exists since PR103 requires a different
# mechanisom for generation phase, specifically inputs)
import copy
from typing import Dict, List, Optional, Tuple, Union

import torch
from torch._dynamo.eval_frame import OptimizedModule
from torch.fx import GraphModule
from transformers import (
    GPTJConfig,
    LlamaConfig,
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
    PreTrainedTokenizerFast,
)

# from typing import List, Optional, Tuple, Union
# import torch
# from torch.fx import GraphModule
from transformers.generation import (
    BeamScorer,
    BeamSearchScorer,
    MinNewTokensLengthLogitsProcessor,
)

# from furiosa_llm_models.generators.paged_attention_optimized_generator import (
#     USE_CACHE,
#     handle_outputs,
#     move_kv_cache_block_in_place,
#     prepare_decode_inputs,
#     prepare_prefill_inputs,
# )
from furiosa_llm_models.generators.paged_attention_optimized_generator_beam_search import (
    adjust_kv_cache_block,
    find_next_tokens,
)
from furiosa_llm_models.generators.v2.generator import (
    OUTPUT_ATTENTIONS,
    OUTPUT_HIDDEN_STATES,
    RETURN_DICT,
    SUPPORTED_GENERATION_RETURN_DICT_TYPES,
)
from furiosa_llm_models.generators.v2.tokenizer import get_tokenizer

from .generator import BaseGenerator
from .packing import greedy_attention_packing

# FIXME: Rename this. Since PagedAttentionGenerator "uses" caches,
# yet it does not yield 'past_key_values' as its output.
USE_CACHE = False

# Below values are for gptj, thus for llama, default argument value should not be used
BLOCK_SIZE = 1
BUCKET_SIZE = 2048
MAX_BATCH_SIZE = 4
NUM_BEAMS = 4
MAX_NEW_TOKENS = 128


def get_generation_output_kwargs(
    output_attentions: bool,
    output_hidden_states: bool,
    return_dict: bool,
    use_cache: bool,
) -> Dict:
    if output_attentions:
        raise ValueError(
            f"model.forward with output_attentions={output_attentions} is not supported."
        )
    if output_hidden_states:
        raise ValueError(
            f"model.forward with output_hidden_states={output_hidden_states} is not supported."
        )
    if use_cache:
        raise ValueError(f"model.forward with use_cache={use_cache} is not supported.")

    return {
        "output_attentions": output_attentions,
        "output_hidden_states": output_hidden_states,
        "return_dict": return_dict,
        "use_cache": use_cache,
    }


def get_model_dim(config: PretrainedConfig) -> Tuple[int, int, int]:
    if isinstance(config, GPTJConfig):
        n_head = config.n_head
        n_embd = config.n_embd
        n_layer = config.n_layer
        head_size = int(n_embd / n_head)
    elif isinstance(config, LlamaConfig):
        n_head = config.num_attention_heads
        n_embd = config.hidden_size
        # We need to calculate head_size here because it might be different if attention is GQA.
        head_size = int(n_embd / n_head)
        # If attention is GQA.
        if n_head > config.num_key_value_heads:
            n_head = config.num_key_value_heads
        n_layer = config.num_hidden_layers
    else:
        raise ValueError(f"Unsupported config type: {type(config)}")
    return n_layer, n_head, head_size


def get_total_block_space(
    n_layer: int,
    n_head: int,
    head_size: int,
    num_blocks: int,
    block_size: int = BLOCK_SIZE,
    kv_dtype: torch.dtype = torch.float32,
    device: torch.device = torch.device("cpu"),
) -> List[Tuple[torch.Tensor, torch.Tensor]]:
    # TODO: Generalize this function to support other models
    # Arbitrary set to accommodate input prompt and generated summary
    example_block_per_layer_shape = (
        num_blocks,
        block_size,
        n_head,
        head_size,
    )

    total_block_space = []
    for _ in range(0, n_layer):
        total_block_space.append(
            (
                torch.zeros(example_block_per_layer_shape, dtype=kv_dtype).to(device),  # key
                torch.zeros(example_block_per_layer_shape, dtype=kv_dtype).to(device),  # value
            )
        )
    return total_block_space


class PagedAttentionGenerator(BaseGenerator):
    output_attentions = OUTPUT_ATTENTIONS
    output_hidden_states = OUTPUT_HIDDEN_STATES
    return_dict = RETURN_DICT
    use_cache = USE_CACHE

    def __init__(
        self,
        model: Union[PreTrainedModel, Dict[str, GraphModule]] = None,
        tokenizer: Optional[Union[PreTrainedTokenizer, PreTrainedTokenizerFast]] = None,
        bucket_size: int = BUCKET_SIZE,
        kv_dtype: torch.dtype = torch.float32,
        return_tensors: bool = False,
        total_block_space: Optional[List[Tuple[torch.Tensor, torch.Tensor]]] = None,
        prefill: Optional[GraphModule] = None,
        decode: Optional[GraphModule] = None,
        num_beams: int = NUM_BEAMS,
        max_batch: int = MAX_BATCH_SIZE,
        batch_size: int = None,
        max_new_tokens: int = MAX_NEW_TOKENS,
    ) -> None:
        assert num_beams == prefill.concrete_args["num_beam"] == decode.concrete_args["num_beam"]

        # ------------- validation -------------
        self.model = self.decode = None
        if isinstance(model, PreTrainedModel):
            self.model = model
        # OptimizedModule cannot be checked by isinstance
        # TypeError: Subscripted generics cannot be used with class and instance checks
        if type(model) == OptimizedModule:  # noqa: E721
            self.model = model
        if (
            isinstance(model, Dict)
            and isinstance(model["prefill"], GraphModule)
            and isinstance(model["decode"], GraphModule)
        ):
            self.model = self.prefill = model["prefill"]
            self.decode = model["decode"]
        if prefill is not None and decode is not None:
            self.model = self.prefill = prefill
            self.decode = decode

        if self.model is None:
            raise ValueError("model is not provided or valid.")
        self.config = self.model.config
        # NOTE: This type of usage is not recommended in Generators.
        # It's more suitable for handlers like HuggingFace's pipeline API.
        self.tokenizer = (
            tokenizer if tokenizer is not None else get_tokenizer(self.config._name_or_path)
        )
        self.num_beams = num_beams
        self.max_new_tokens = max_new_tokens
        self.max_batch = max_batch

        n_layer, n_head, head_size = get_model_dim(self.config)
        if total_block_space is None:
            # num_blocks = dummy pad token(=1) + bucket_size(=max_length)
            #               * effective batch_size * 2(for each key and value)
            num_blocks = 1 + 2 * bucket_size * (
                max_batch if batch_size is None else min(batch_size, max_batch)
            )
            total_block_space = get_total_block_space(
                n_layer,
                n_head,
                head_size,
                block_size=BLOCK_SIZE,
                kv_dtype=kv_dtype,
                device=self.model.device,
                num_blocks=num_blocks,
            )

        assert len(total_block_space) == n_layer, "KV cache initialization failed"

        block_indices, block_size, _, _ = total_block_space[0][0].shape

        assert bucket_size % block_size == 0
        assert block_size == 1

        self.past_key_values = total_block_space

        self.block_size = block_size

        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []

        # Below fields keep track of prompt block indices which are shared across beam candidates
        self.prompt_key_block_indices: List[List[int]] = []
        self.prompt_value_block_indices: List[List[int]] = []

        self.available_block_indices = list(range(1, block_indices))
        self.zero_block_index = 0  # this is a special zero block
        self.total_block_count = block_indices
        # TODO: this should be different for prefill and decode
        self.bucket_size = bucket_size
        self.num_max_block = int(bucket_size / block_size)
        self.return_tensors = return_tensors
        # This is an attribute that is used to determine whether the model has scores for decode output. # noqa
        # It is only True for gptj.symbolic.paged_attention_optimized_packed_rope_erf_gelu.GPTJForCausalLM. # noqa
        # FIXME: This is a hacky way to handle this.
        try:
            getattr(self.model, "has_scores_for_decode_output")
        except AttributeError:
            self.model.has_scores_for_decode_output = False

    def reset(self):
        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []
        self.available_block_indices = list(range(1, self.total_block_count))

    def prepare_prefill_input_metadata(
        self, attention_mask: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for single_attention_mask in attention_mask:
            # for each attention_mask add zero block for padding
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            self.active_key_block_indices.append(block_indices[:])
            self.active_value_block_indices.append(block_indices)

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        valid_key_indices = []  # shape = (batch*(bucket_size -1))
        valid_value_indices = []  #
        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            valid_key_indices.extend(key_batch[:-1])
            valid_value_indices.extend(value_batch[:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)
        valid_key_indices = torch.IntTensor(valid_key_indices)
        valid_value_indices = torch.IntTensor(valid_value_indices)

        return (
            new_key_location,
            new_value_location,
            valid_key_indices,
            valid_value_indices,
        )

    # this will handle a single sequence without scheduling
    @torch.no_grad()
    def generate(
        self, input_ids: torch.Tensor, attention_mask: torch.Tensor, max_length: int, **kwargs
    ) -> Union[List[str], torch.Tensor]:
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """
        # FIXME: This is a hacky way to handle the device.
        # This should be handled in a better way.
        with torch.device(input_ids.device):
            # ----------- initial_settings -----------------
            starting_input_ids = input_ids
            starting_attention_mask = attention_mask
            batch_size, prompt_len = starting_input_ids.shape

            # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
            # In vllm, generate is async and inner scheduler decides which batch to use based on
            # memory allocation
            assert batch_size <= self.max_batch

            starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
            starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

            # ----------- adjust to bucket settings --------
            pad_token_id = self.model.config.eos_token_id

            attention_mask = torch.zeros((batch_size, self.bucket_size), dtype=torch.int)
            attention_mask[:, :prompt_len] = starting_attention_mask

            input_ids = torch.full(
                (batch_size, self.bucket_size), fill_value=pad_token_id, dtype=torch.int
            )
            input_ids[:, :prompt_len] = starting_input_ids

            position_ids = torch.zeros((batch_size, self.bucket_size), dtype=torch.long)
            position_ids[:, :prompt_len] = starting_position_ids

            sequence_idx = prompt_len - 1
            is_prefill = True

            batch_size = input_ids.shape[0]
            unfinished_sequences = torch.ones(batch_size, dtype=torch.long, device=input_ids.device)
            eos_token_id = self.model.config.eos_token_id
            eos_token_id_tensor = torch.tensor([eos_token_id]).to(input_ids.device)
            next_tokens = None

            # FIXME: This is a temporary solution to handle out-of-bound positional embedding access. # noqa
            # This issue occurs when the maximum length of the generated sequence exceeds the
            # maximum number of embeddings in the model.
            if max_length > self.config.max_position_embeddings:
                max_length = self.config.max_position_embeddings

            # start generating new tokens
            for i in range(max_length - prompt_len):
                if is_prefill:
                    (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                        attention_mask
                    )

                    (
                        packed_input_ids,
                        _packed_attention_mask,  # this attention mask if for debugging purpose
                        causal_mask,
                        packed_position_ids,
                        logit_target_locations,
                        new_key_location,
                        new_value_location,
                    ) = prepare_prefill_inputs(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        new_key_location=new_key_location,
                        new_value_location=new_value_location,
                        pad_token_id=pad_token_id,
                    )  # original attention mask, original position ids

                    forward_kwargs = {
                        "input_ids": packed_input_ids,
                        "attention_mask": None,
                        "causal_mask": causal_mask,
                        "position_ids": packed_position_ids,
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": None,
                        "past_valid_value_indices": None,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                    }

                    # If the model is a GraphModule, we need to switch the model to prefill.
                    if isinstance(self.model, GraphModule) and self.model != self.prefill:
                        self.model = self.prefill

                else:
                    (input_ids, attention_mask, position_ids) = prepare_decode_inputs(
                        next_input_ids=next_tokens,
                        prev_attention_mask=attention_mask,
                        is_first_decode=(True if i == 1 else False),  # FIXME: hacky
                        seq_idx=sequence_idx,
                    )

                    logit_target_locations = None  # for decode, not needed

                    (
                        new_key_location,
                        new_value_location,
                        valid_key_indices,
                        valid_value_indices,
                    ) = self.prepare_decode_input_metadata()

                    forward_kwargs = {
                        "input_ids": input_ids,
                        "attention_mask": attention_mask,
                        "causal_mask": None,
                        "position_ids": position_ids,
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_indices": valid_key_indices,
                        "past_valid_value_indices": valid_value_indices,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                    }

                    # If the model is a GraphModule, we need to switch the model to decode.
                    if isinstance(self.model, GraphModule) and self.model != self.decode:
                        self.model = self.decode

                # remove all concrete args from forward_kwargs for they will not be used in the
                # forward pass.
                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs:
                            del forward_kwargs[arg]

                outputs = self.model(**forward_kwargs)

                if not is_prefill:
                    # now copy the new_key location back to original place for decode_phase
                    move_kv_cache_block_in_place(
                        seq_idx=sequence_idx,
                        new_location=new_key_location,
                        existing_block_indices=self.active_key_block_indices,
                    )
                    move_kv_cache_block_in_place(
                        seq_idx=sequence_idx,
                        new_location=new_value_location,
                        existing_block_indices=self.active_value_block_indices,
                    )

                # done
                outputs = handle_outputs(outputs)

                # done
                next_tokens = find_next_tokens(
                    outputs,
                    logit_target_locations,
                    unfinished_sequences,
                    pad_token_id,
                    is_prefill,
                )

                starting_input_ids = torch.cat([starting_input_ids, next_tokens[:, None]], dim=-1)

                unfinished_sequences = unfinished_sequences.mul(
                    next_tokens.tile(eos_token_id_tensor.shape[0], 1)
                    .ne(eos_token_id_tensor.unsqueeze(1))
                    .prod(dim=0)
                )

                sequence_idx += 1

                # prepare for next phase
                is_prefill = False

            # reset must be called
            self.reset()

            # return entire sample
            outputs = (
                [
                    [self.tokenizer.decode(output, skip_special_tokens=True)]
                    for output in starting_input_ids
                ]
                if not self.return_tensors
                else starting_input_ids
            )
            return outputs


def move_kv_cache_block_in_place(
    seq_idx: int,
    new_location: torch.Tensor,
    existing_block_indices: List[List[int]],
    beam_idx,
) -> None:
    # new key location should always be shape [batch, 1]
    for single_batch_block_indices, cur_beam_idx in zip(existing_block_indices, beam_idx):
        single_batch_block_indices[seq_idx] = new_location[cur_beam_idx].item()


def prepare_decode_inputs(
    next_input_ids: torch.Tensor,
    prev_attention_mask: torch.Tensor,
    is_first_decode: bool,
    seq_idx: int,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    return (input_ids, attention_mask, position_ids)
    """
    next_attention_mask = prev_attention_mask.clone()

    if is_first_decode:
        # Before: [[1, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0]]
        # After : [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
        next_attention_mask[:, -1] = 1
    else:
        # Before: [[1, 1, 1, 0, 0, 0, 0, 1], [0, 1, 1, 0, 0, 0, 0, 1]]
        # After : [[1, 1, 1, 1, 0, 0, 0, 1], [0, 1, 1, 1, 0, 0, 0, 1]]
        next_attention_mask[:, seq_idx - 1] = 1

    next_position_ids = next_attention_mask.long().cumsum(-1) - 1
    next_position_ids = next_position_ids[:, -1:]

    return (next_input_ids[:, None], next_attention_mask, next_position_ids)


def prepare_prefill_inputs(
    input_ids: torch.Tensor,
    attention_mask: torch.Tensor,
    new_key_location: torch.Tensor,
    new_value_location: torch.Tensor,
    pad_token_id: int,
) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, List[List[int]]]:
    """
    return (packed_input_ids, causal_mask, packed_position_ids, logit_target_locations, packed_new_key_locatoin, packed_new_value_location)
    """  # noqa: E501
    (
        packed_attention_mask,
        packed_input_ids,
        causal_mask,
        logit_target_locations,
        packed_position_ids,
        packed_new_key_location,
        packed_new_value_location,
    ) = greedy_attention_packing(
        input_ids,
        attention_mask,
        new_key_location,
        new_value_location,
        pad_token_id=pad_token_id,
    )
    return (
        packed_input_ids,
        packed_attention_mask,
        causal_mask,
        packed_position_ids,
        logit_target_locations,
        packed_new_key_location,
        packed_new_value_location,
    )


def handle_outputs(
    outputs: Tuple[torch.Tensor, List[Tuple[torch.Tensor, torch.Tensor]]],
) -> torch.Tensor:
    # handle outputs differently based on prefill vs decode

    # SUPPORTED_GENERATION_RETURN_DICT_TYPES[1],
    # i.e., CausalLMOutputWithCrossAttentions is not yet checked.
    if isinstance(outputs, SUPPORTED_GENERATION_RETURN_DICT_TYPES[0]):
        logits = outputs.to_tuple()[0]
    elif isinstance(outputs, Tuple):
        logits = outputs[0]
    elif isinstance(outputs, Dict):
        logits = outputs["logits"]
    else:
        raise ValueError(f"Unsupported generation output type: {type(outputs)}")
    return logits


class PagedAttentionGeneratorBeamSearch(PagedAttentionGenerator):
    def prepare_prefill_input_metadata(
        self,
        attention_mask: torch.Tensor,
        batch_size: int,
        max_prompt_len: int,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        for prefill, valid_key_indices and valid_value_indices are none
        return (new_key_location, new_value_location)
        """
        # beams belonging to same prompts should share blocks

        new_key_location = []  # shape = (batch, bucket_size)
        new_value_location = []  # shape = (batch, bucket_size)
        for count in range(batch_size):
            idx = count * self.num_beams
            single_attention_mask = attention_mask[idx]
            block_indices = []
            for val in single_attention_mask:
                if val == 0:
                    # padding
                    block_indices.append(self.zero_block_index)
                else:
                    block_indices.append(self.available_block_indices.pop())

            # at this point block has been created
            # MAX_PROMPT_LEN is required to remove dynamic characteristc to decode phase
            self.prompt_key_block_indices.append(copy.deepcopy(block_indices[:max_prompt_len]))
            self.prompt_value_block_indices.append(copy.deepcopy(block_indices[:max_prompt_len]))

            for _ in range(self.num_beams):
                self.active_key_block_indices.append(copy.deepcopy(block_indices))
                self.active_value_block_indices.append(copy.deepcopy(block_indices))

        new_key_location = torch.IntTensor(self.active_key_block_indices)
        new_value_location = torch.IntTensor(self.active_value_block_indices)

        return (
            new_key_location,
            new_value_location,
        )

    def prepare_decode_input_metadata(
        self, max_prompt_len: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        return (new_key_location, new_value_location, valid_key_indices, valid_valie_indices)
        """
        new_key_location = []  # shape = (batch, 1)
        new_value_location = []  # shape = (batch, 1)
        past_valid_key_decode_indices = []
        past_valid_value_decode_indices = []

        for key_batch, value_batch in zip(
            self.active_key_block_indices, self.active_value_block_indices
        ):
            past_valid_key_decode_indices.extend(key_batch[max_prompt_len:-1])
            past_valid_value_decode_indices.extend(value_batch[max_prompt_len:-1])

            # we use same block idx for key and value here
            new_block_idx = self.available_block_indices.pop()

            key_batch[-1] = new_block_idx
            value_batch[-1] = new_block_idx

            new_key_location.append([new_block_idx])
            new_value_location.append([new_block_idx])

        new_key_location = torch.IntTensor(new_key_location)
        new_value_location = torch.IntTensor(new_value_location)

        past_valid_key_prompt_indices = torch.IntTensor(self.prompt_key_block_indices)
        past_valid_value_prompt_indices = torch.IntTensor(self.prompt_value_block_indices)
        past_valid_key_decode_indices = torch.IntTensor(past_valid_key_decode_indices)
        past_valid_value_decode_indices = torch.IntTensor(past_valid_value_decode_indices)

        return (
            new_key_location,
            new_value_location,
            past_valid_key_prompt_indices,
            past_valid_key_decode_indices,
            past_valid_value_prompt_indices,
            past_valid_value_decode_indices,
        )

    def reset(self):
        self.active_key_block_indices: List[List[int]] = []
        self.active_value_block_indices: List[List[int]] = []
        self.available_block_indices = list(range(1, self.total_block_count))

        # Below fields keep track of prompt block indices which are shared across beam candidates
        self.prompt_key_block_indices: List[List[int]] = []
        self.prompt_value_block_indices: List[List[int]] = []

        for first_idx in range(len(self.past_key_values)):
            for second_idx in range(len(self.past_key_values[first_idx])):
                self.past_key_values[first_idx] = list(self.past_key_values[first_idx])
                kv_dtype = self.past_key_values[first_idx][second_idx].dtype
                device = self.past_key_values[first_idx][second_idx].device
                self.past_key_values[first_idx][second_idx] = torch.zeros(
                    self.past_key_values[first_idx][second_idx].shape, dtype=kv_dtype
                ).to(device)

    # this will handle a single sequence without scheduling
    @torch.no_grad()
    def generate(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        min_new_tokens: Optional[int] = None,
        max_length=None,
        **kwargs,
    ) -> Union[List[str], torch.Tensor]:
        """
        Generate N number of new tokens for each sequence
        where N = max_length - len(starting_input_ids[0])
        """
        # FIXME: This is a hacky way to handle the device.
        # This should be handled in a better way.
        with torch.device(input_ids.device):
            # ----------- initial_settings -----------------
            starting_input_ids = input_ids
            starting_attention_mask = attention_mask
            batch_size, prompt_len = starting_input_ids.shape

            # TODO(MAX BATCH CHECK ONLY EXISTS FOR THIS PYTHON GENERATOR)
            # In vllm, generate is async and inner scheduler decides which batch to use based on
            # memory allocation
            assert batch_size <= self.max_batch

            starting_position_ids = starting_attention_mask.long().cumsum(-1) - 1
            starting_position_ids.masked_fill_(starting_attention_mask == 0, 1)

            # ----------- adjust to bucket settings --------
            pad_token_id = self.model.config.eos_token_id

            attention_mask = torch.zeros((batch_size, self.bucket_size), dtype=torch.int)
            attention_mask[:, :prompt_len] = starting_attention_mask

            input_ids = torch.full(
                (batch_size, self.bucket_size), fill_value=pad_token_id, dtype=torch.int
            )
            input_ids[:, :prompt_len] = starting_input_ids

            position_ids = torch.zeros((batch_size, self.bucket_size), dtype=torch.long)
            position_ids[:, :prompt_len] = starting_position_ids

            is_prefill = True

            batch_size = input_ids.shape[0]
            eos_token_id = self.model.config.eos_token_id
            next_tokens = None

            self.logit_processor = MinNewTokensLengthLogitsProcessor(
                prompt_length_to_skip=starting_input_ids.shape[-1],
                min_new_tokens=min_new_tokens,
                eos_token_id=eos_token_id,
                device=input_ids.device,
            )

            # The argument max_length should not be used in MLPerf scenario,
            # as the maximum condition is imposed on the number of newly generated tokens
            # and thus should remain indepdent of prompt length.

            if "max_new_tokens" in kwargs:
                _max_length = min(
                    prompt_len + kwargs["max_new_tokens"], self.config.max_position_embeddings
                )
                if max_length:
                    assert _max_length == max_length
            elif max_length:
                _max_length = min(max_length, self.config.max_position_embeddings)
            else:
                _max_length = self.config.max_position_embeddings

            # beam search stuff
            beam_scorer: BeamScorer = BeamSearchScorer(
                batch_size=input_ids.shape[0],
                num_beams=self.num_beams,
                device=input_ids.device,
                length_penalty=1.0,  # TODO: Generalize. Fix it as 1.0 for now.
                do_early_stopping=True,  # This should be always True.
                num_beam_hyps_to_keep=1,  # TODO: Generalize. Fix it as 1 for now.
                max_length=_max_length,
            )

            input_ids = input_ids.repeat_interleave(
                self.num_beams, 0
            )  # [batch_size * num_beams, sequence_length]
            starting_input_ids = starting_input_ids.repeat_interleave(self.num_beams, 0)
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L727
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L718-L722
            attention_mask = attention_mask.repeat_interleave(
                self.num_beams, 0
            )  # [batch_size * num_beams, sequence_length]

            # beam search config
            batch_size = len(beam_scorer._beam_hyps)
            num_beams = beam_scorer.num_beams

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2889
            batch_beam_size, _ = input_ids.shape
            # TODO(this is because we use bucketization)
            cur_len = prompt_len
            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2891-L2894
            if num_beams * batch_size != batch_beam_size:
                raise ValueError(
                    f"Batch dimension of `input_ids` should be {num_beams * batch_size}, "
                    f"but is {batch_beam_size}."
                )

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2896-L2900
            # Assuming return_dict_in_generate and output_scores are not used in this function.
            # scores = None # not used
            beam_indices = None

            ####################>>>>>>>>>>>>>>>>>>>>
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2912-L2916
            beam_scores = torch.zeros(
                (batch_size, num_beams), dtype=torch.float, device=input_ids.device
            )
            beam_scores[:, 1:] = -1e9
            beam_scores = beam_scores.view((batch_size * num_beams,))
            is_first_decode = False
            next_tokens = None
            # start generating new tokens

            count = 0
            max_prompt_len = self.bucket_size - self.max_new_tokens
            while True:
                if is_prefill:
                    (new_key_location, new_value_location) = self.prepare_prefill_input_metadata(
                        attention_mask, batch_size, max_prompt_len
                    )
                    (
                        packed_input_ids,
                        _packed_attention_mask,  # this attention mask if for debugging purpose
                        causal_mask,
                        packed_position_ids,
                        logit_target_locations,
                        new_key_location,
                        new_value_location,
                    ) = prepare_prefill_inputs(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        new_key_location=new_key_location,
                        new_value_location=new_value_location,
                        pad_token_id=pad_token_id,
                    )  # original attention mask, original position ids
                    forward_kwargs = {
                        "input_ids": packed_input_ids,
                        "attention_mask": None,
                        "causal_mask": causal_mask,
                        "position_ids": packed_position_ids,
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_prompt_indices": None,
                        "past_valid_key_decode_indices": None,
                        "past_valid_value_prompt_indices": None,
                        "past_valid_value_decode_indices": None,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                        "num_beam": self.num_beams,
                        "max_new_tokens": self.max_new_tokens,
                        "num_real_batch": batch_size,
                    }

                    is_first_decode = True

                    # If the model is a GraphModule, we need to switch the model to prefill.
                    if isinstance(self.model, GraphModule) and self.model != self.prefill:
                        self.model = self.prefill
                else:
                    (next_tokens, attention_mask, position_ids) = prepare_decode_inputs(
                        next_input_ids=next_tokens,
                        prev_attention_mask=attention_mask,
                        is_first_decode=is_first_decode,
                        seq_idx=max_prompt_len + count - 1,
                    )

                    logit_target_locations = None  # for decode, not needed

                    (
                        new_key_location,
                        new_value_location,
                        past_valid_key_prompt_indices,
                        past_valid_key_decode_indices,
                        past_valid_value_prompt_indices,
                        past_valid_value_decode_indices,
                    ) = self.prepare_decode_input_metadata(max_prompt_len=max_prompt_len)

                    forward_kwargs = {
                        "input_ids": next_tokens,
                        "attention_mask": attention_mask,
                        "causal_mask": None,
                        "position_ids": position_ids,
                        "past_key_values": self.past_key_values,
                        "new_key_location": new_key_location,
                        "new_value_location": new_value_location,
                        "past_valid_key_prompt_indices": past_valid_key_prompt_indices,
                        "past_valid_key_decode_indices": past_valid_key_decode_indices,
                        "past_valid_value_prompt_indices": past_valid_value_prompt_indices,
                        "past_valid_value_decode_indices": past_valid_value_decode_indices,
                        "is_prefill": is_prefill,
                        "bucket_size": self.bucket_size,
                        "use_cache": USE_CACHE,
                        "num_beam": self.num_beams,
                        "max_new_tokens": self.max_new_tokens,
                        "num_real_batch": batch_size,
                    }

                    is_first_decode = False

                    # If the model is a GraphModule, we need to switch the model to decode.
                    if isinstance(self.model, GraphModule) and self.model != self.decode:
                        self.model = self.decode

                # remove all concrete args from forward_kwargs for they will not be used in the
                # forward pass.
                if isinstance(self.model, GraphModule):
                    for arg in self.model.concrete_args:
                        if arg in forward_kwargs:
                            del forward_kwargs[arg]

                outputs = self.model(**forward_kwargs)

                # done
                logits = handle_outputs(outputs)

                # logits has shape 4,8
                # because attention has been packe

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2943
                # this is for attention depacking
                # next_token_logits = logits[:, -1, :]
                # FIXME: This is copy from paged_attention_optimized-generator_beam_search,
                # since we do not support a common generator for now.
                # if is_prefill or not self.model.has_scores_for_decode_output:
                #     next_token_logits = find_next_tokens(logits, logit_target_locations, is_prefill)  # noqa: E501

                #     # TODO: Check if self.adjust_logits_during_generation is necessary in this
                #     # context
                #     # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2944-L2946
                #     # The following code adjusts the logits during generation. However, it seems to  # noqa: E501
                #     # have no effect on GPT-J and LLaMMA models, as they do not have this function
                #     # as an instance method. Additionally, the `adjust_logits_during_generation`
                #     # function in `transformers.generation.utils.GenerationMixin` does not modify
                #     # the logits, as can be seen in the following code:
                #     # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L564-L568
                #     ####################>>>>>>>>>>>>>>>>>>>>
                #     # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2947-L2949
                #     next_token_scores = torch.nn.functional.log_softmax(
                #         next_token_logits, dim=-1
                #     )  # [batch_size * num_beams, vocab_size]
                # else:
                #     # For decode, we will use the logits as scores as model outputs
                #     # torch.nn.functional.log_softmax(lm_logits[:, -1], dim=-1)
                #     next_token_scores = logits

                if is_prefill:
                    next_token_scores = find_next_tokens(logits, logit_target_locations, is_prefill)
                    # next_token_scores = torch.nn.functional.log_softmax(
                    #     next_token_logits, dim=-1
                    # )  # [batch_size * num_beams, vocab_size]
                else:
                    # For decode, we will use the logits as scores as model outputs
                    # torch.nn.functional.log_softmax(lm_logits[:, -1], dim=-1)
                    next_token_scores = logits[:, -1]

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2951-L2952
                next_token_scores_processed = self.logit_processor(input_ids, next_token_scores)

                next_token_scores = next_token_scores_processed + beam_scores[:, None].expand_as(
                    next_token_scores
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2972-L2974
                vocab_size = next_token_scores.shape[-1]
                next_token_scores = next_token_scores.view(batch_size, num_beams * vocab_size)

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2976-L2979
                next_token_scores, next_tokens = torch.topk(
                    next_token_scores, 2 * num_beams, dim=1, largest=True, sorted=True
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2981-L2982
                next_indices = torch.div(next_tokens, vocab_size, rounding_mode="floor")
                next_tokens = next_tokens % vocab_size

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2984-L2993
                beam_outputs = beam_scorer.process(
                    starting_input_ids,
                    next_token_scores,
                    next_tokens,
                    next_indices,
                    pad_token_id=pad_token_id,
                    eos_token_id=eos_token_id,
                    beam_indices=beam_indices,
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2995-L2997
                beam_scores = beam_outputs["next_beam_scores"]
                beam_next_tokens = beam_outputs["next_beam_tokens"]
                beam_idx = beam_outputs["next_beam_indices"]

                # TODO(DONGHUN) based on this idx adjust the block index
                # we know new beams are chosen at this point

                new_key_block_indices = adjust_kv_cache_block(
                    beam_idx, self.active_key_block_indices
                )
                self.active_key_block_indices = new_key_block_indices
                new_value_block_indices = adjust_kv_cache_block(
                    beam_idx, self.active_value_block_indices
                )
                self.active_value_block_indices = new_value_block_indices

                if not is_prefill:
                    # now copy the new_key location back to original place for decode_phase
                    move_kv_cache_block_in_place(
                        seq_idx=max_prompt_len + count - 1,
                        new_location=new_key_location,
                        existing_block_indices=self.active_key_block_indices,
                        beam_idx=beam_idx,
                    )
                    move_kv_cache_block_in_place(
                        seq_idx=max_prompt_len + count - 1,
                        new_location=new_value_location,
                        existing_block_indices=self.active_value_block_indices,
                        beam_idx=beam_idx,
                    )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L2999
                starting_input_ids = torch.cat(
                    [starting_input_ids[beam_idx, :], beam_next_tokens.unsqueeze(-1)], dim=-1
                )

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3010-L3011
                cur_len = cur_len + 1

                # TODO: remove count which is only for debuggin
                count += 1

                ####################>>>>>>>>>>>>>>>>>>>>
                # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3013-L3015
                # cur_len >= max_length is a short version of the stopping criteria in
                # https://github.com/huggingface/transformers/blob/main/src/transformers/generation/stopping_criteria.py#L75-L83
                # TODO: Implement get stopping criteria logic
                # TODO: Implement other stopping criteria
                if beam_scorer.is_done or starting_input_ids.shape[1] >= _max_length:
                    break

                # v2.Generator specific variables
                is_prefill = False
                next_tokens = beam_next_tokens

            sequence_outputs = beam_scorer.finalize(
                starting_input_ids,
                beam_scores,
                next_tokens,
                next_indices,
                pad_token_id=pad_token_id,
                eos_token_id=eos_token_id,
                max_length=_max_length,
                beam_indices=beam_indices,
            )

            # reset must be called for paged attention to call generate again
            self.reset()
            # https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/generation/utils.py#L3055-L3056

            outputs = (
                [
                    [self.tokenizer.decode(output, skip_special_tokens=True)]
                    for output in sequence_outputs["sequences"]
                ]
                if not self.return_tensors
                else sequence_outputs["sequences"]
            )

            return outputs
