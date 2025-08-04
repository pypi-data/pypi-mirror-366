# For transformer models, GenerationMixin does the job but for custom rewritten models,
# such generator may not be enough so it is upto the developer to write a custom generator that
# may be used for testing rewritten models through this generator

from abc import ABC, abstractmethod


class BaseGenerator(ABC):
    @abstractmethod
    def generate(
        self,
        padded_sequences,
        max_length: int,
    ): ...
