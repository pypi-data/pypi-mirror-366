import abc

from torch import Tensor


class BaseEncoder(abc.ABC):
    @abc.abstractmethod
    def encode(self, *args, **kwargs) -> Tensor:
        pass
