from typing import Tuple

from torch import Tensor
from torch.nn.functional import pad

from ..generator import BaseGenerator


class BertGenerator(BaseGenerator):
    def __init__(self, model) -> None:
        self.model = model

    def generate(self, padded_sequences, bucket_size) -> Tuple[Tensor, Tensor]:
        def bucket_pad(tensor):
            if bucket_size is None:
                return tensor

            padding_size = bucket_size - tensor.shape[-1]
            return pad(tensor, (0, padding_size))

        original_seq = padded_sequences["input_ids"].shape[-1]
        outputs = self.model(
            input_ids=bucket_pad(padded_sequences["input_ids"]),
            token_type_ids=bucket_pad(padded_sequences["token_type_ids"]),
            attention_mask=bucket_pad(padded_sequences["attention_mask"]),
        )
        start = outputs.start_logits[:, :original_seq].argmax(-1)
        end = outputs.end_logits[:, :original_seq].argmax(-1)
        return (start, end)


class BertUnsplitGenerator(BaseGenerator):
    def __init__(self, model) -> None:
        self.model = model

    def generate(self, padded_sequences, bucket_size) -> Tensor:
        def bucket_pad(tensor):
            if bucket_size is None:
                return tensor

            padding_size = bucket_size - tensor.shape[-1]
            return pad(tensor, (0, padding_size))

        original_seq = padded_sequences["input_ids"].shape[-1]
        logits = self.model(
            input_ids=bucket_pad(padded_sequences["input_ids"]),
            token_type_ids=bucket_pad(padded_sequences["token_type_ids"]),
            attention_mask=bucket_pad(padded_sequences["attention_mask"]),
        )
        pos = logits[:, :original_seq].argmax(1)
        return pos
