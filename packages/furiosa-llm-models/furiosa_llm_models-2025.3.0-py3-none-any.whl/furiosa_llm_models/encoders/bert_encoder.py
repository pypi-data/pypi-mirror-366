from typing import List, Optional, Tuple

import torch
from torch import Tensor
from torch.fx import GraphModule
from torch.nn.functional import pad
from transformers import PreTrainedModel
from transformers.modeling_outputs import QuestionAnsweringModelOutput

from ..generators.packing import greedy_attention_packing_bert
from .encoder import BaseEncoder


def bucket_pad(tensor: Tensor, bucket_size: Optional[int]) -> Tensor:
    if bucket_size is None:
        return tensor
    padding_size = bucket_size - tensor.shape[-1]
    return pad(tensor, (0, padding_size))


class BertEncoder(BaseEncoder):
    def __init__(self, model: PreTrainedModel, bucket_size: Optional[int] = None) -> None:
        self.model = model
        self.bucket_size = bucket_size

    def encode(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        token_type_ids: Tensor,
    ) -> Tuple[Tensor, Tensor]:
        original_seq_len = input_ids.shape[-1]
        outputs: QuestionAnsweringModelOutput = self.model(
            input_ids=bucket_pad(input_ids, bucket_size=self.bucket_size),
            token_type_ids=bucket_pad(token_type_ids, bucket_size=self.bucket_size),
            attention_mask=bucket_pad(attention_mask, bucket_size=self.bucket_size),
        )
        start_logits = outputs.start_logits[:, :original_seq_len]
        end_logits = outputs.end_logits[:, :original_seq_len]
        return start_logits, end_logits


class BertUnsplitEncoder(BertEncoder):
    def encode(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        token_type_ids: Tensor,
    ) -> Tensor:
        original_seq_len = input_ids.shape[-1]
        logits = self.model(
            input_ids=bucket_pad(input_ids, bucket_size=self.bucket_size),
            token_type_ids=bucket_pad(token_type_ids, bucket_size=self.bucket_size),
            attention_mask=bucket_pad(attention_mask, bucket_size=self.bucket_size),
        )
        return logits[:, :original_seq_len]


class BertUnsplitPackedEncoder(BertEncoder):
    def __init__(
        self,
        model: PreTrainedModel,
        bucket_size: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        compact_mask: bool = False,
        position_offset: int = 0,
    ) -> None:
        super().__init__(model, bucket_size=bucket_size)
        if pad_token_id is None:
            raise ValueError(f"pad_token_id must be provided for {self.__class__.__name__}")
        self.pad_token_id = pad_token_id
        self.compact_mask = compact_mask
        self.position_offset = position_offset

    def encode(
        self,
        input_ids: Tensor,
        attention_mask: Tensor,
        token_type_ids: Optional[Tensor] = None,
    ) -> List[Tensor]:
        # greedy attention packing bert will do left padding regardless of given input
        if token_type_ids is None:
            token_type_ids = torch.zeros(input_ids.shape).to(input_ids)

        (
            input_ids,
            token_type_ids,
            attention_mask,
            position_ids,
            packed_target_locations,
        ) = greedy_attention_packing_bert(
            input_ids=bucket_pad(input_ids, self.bucket_size),
            token_type_ids=bucket_pad(token_type_ids, self.bucket_size),
            bucketized_attention_mask=bucket_pad(attention_mask, self.bucket_size),
            pad_token_id=self.pad_token_id,
            compact_mask=self.compact_mask,
            position_offset=self.position_offset,
        )

        model_kwargs = dict(
            input_ids=input_ids,
            token_type_ids=token_type_ids,
            attention_mask=attention_mask,
            position_ids=position_ids,
        )

        # remove all concrete args from model_kwargs as they will not be used in the forward pass.
        if isinstance(self.model, GraphModule):
            for arg in self.model.concrete_args:
                if arg in model_kwargs:
                    del model_kwargs[arg]

        logits = self.model(**model_kwargs)

        outputs = []
        for batch_index, target_location in enumerate(packed_target_locations):
            for single_target_location in target_location:
                start, end = single_target_location
                single_logit = logits[batch_index][start:end]
                outputs.append(single_logit)

        return outputs
