import torch

from ..gptj.paged_attention_utils import InputMetadata


def reshape_and_cache(
    target: torch.Tensor,
    total: torch.Tensor,
    new_target_location: torch.Tensor,
):
    indices = torch.squeeze(new_target_location.reshape(1, -1), dim=0)
    batch, seq, num_head, head_dim = target.shape
    total[indices] = target.reshape(batch * seq, 1, num_head, head_dim)


# FIXME: move this function to .generators.paged_attention_generator
def prepare_inputs_for_paged_attention_generation(
    self,
    input_ids: torch.Tensor,
    input_metadata: InputMetadata,
    attention_mask: torch.Tensor,
    **kwargs,
):
    # we allow inputs with different sequence_length
    updated_input_ids = input_ids
    if not input_metadata.is_prefill:
        updated_input_ids = input_ids[:, -1:]

    # attention mask should exist at this point
    assert attention_mask is not None

    model_inputs = {"input_ids": updated_input_ids}

    model_inputs.update(
        {
            "use_cache": kwargs.get("use_cache"),
            "attention_mask": attention_mask,
            "is_paged_attention_prefill": input_metadata.is_prefill,
        }
    )

    return model_inputs
