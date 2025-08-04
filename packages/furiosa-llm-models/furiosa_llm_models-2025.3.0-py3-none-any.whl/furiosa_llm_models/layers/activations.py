import math

import torch
import torch.nn as nn
from transformers.activations import (
    AccurateGELUActivation,
    ClassInstantier,
    ClippedGELUActivation,
    FastGELUActivation,
    GELUActivation,
    LaplaceActivation,
    LinearActivation,
    MishActivation,
    NewGELUActivation,
    PytorchGELUTanh,
    QuickGELUActivation,
    ReLUSquaredActivation,
)


class RNGDGelu(nn.Module):
    """
    This activation function is an optimized version of GeLU that can run in a single execution on RNGD.
    The RNGD architecture natively supports the Gauss error function (erf). https://en.wikipedia.org/wiki/Error_function

    The original Gelu implementation can be found in the Huggingface Transformers library:
    https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/activations.py#L59-L78

    For more details on the optimization and its benefits, please refer to the following documentation:
    https://www.notion.so/furiosa/GPT-J-6e6ff841bcbc402dbecc03069b8c60b3?pvs=4
    """  # noqa

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x1 = x * 1 / math.sqrt(2)  # Float cluster MUL0
        x2 = torch.erf(x1)  # Float cluster FPU erf
        x3 = 1 / math.sqrt(2) + 1 / math.sqrt(2) * x2  # Float cluster FMA
        x4 = x1 * x3  # Float cluster MUL1
        return x4


# https://github.com/huggingface/transformers/blob/v4.31.0/src/transformers/activations.py#L140-L150
class SiLUActivation(nn.Module):
    """
    See Gaussian Error Linear Units (Hendrycks et al., https://arxiv.org/abs/1606.08415) where the SiLU (Sigmoid Linear
    Unit) was originally introduced and coined, and see Sigmoid-Weighted Linear Units for Neural Network Function
    Approximation in Reinforcement Learning (Elfwing et al., https://arxiv.org/abs/1702.03118) and Swish: a Self-Gated
    Activation Function (Ramachandran et al., https://arxiv.org/abs/1710.05941v1) where the SiLU was experimented with
    later.
    """  # noqa

    def forward(self, input: torch.Tensor) -> torch.Tensor:
        return nn.functional.silu(input)


ACT2CLS = {
    "gelu": GELUActivation,
    "gelu_10": (ClippedGELUActivation, {"min": -10, "max": 10}),
    "gelu_fast": FastGELUActivation,
    "gelu_new": NewGELUActivation,
    "gelu_python": (GELUActivation, {"use_gelu_python": True}),
    "gelu_pytorch_tanh": PytorchGELUTanh,
    "gelu_accurate": AccurateGELUActivation,
    "laplace": LaplaceActivation,
    "leaky_relu": nn.LeakyReLU,
    "linear": LinearActivation,
    "mish": MishActivation,
    "quick_gelu": QuickGELUActivation,
    "relu": nn.ReLU,
    "relu2": ReLUSquaredActivation,
    "relu6": nn.ReLU6,
    "sigmoid": nn.Sigmoid,
    "silu": SiLUActivation,
    "swish": SiLUActivation,
    "tanh": nn.Tanh,
    "rngd_gelu": RNGDGelu,
}
ACT2FN = ClassInstantier(ACT2CLS)


def get_activation(activation_string):
    if activation_string in ACT2FN:
        return ACT2FN[activation_string]
    else:
        raise KeyError(
            f"function {activation_string} not found in ACT2FN mapping {list(ACT2FN.keys())}"
        )


# For backwards compatibility with: from activations import gelu_python
gelu_python = get_activation("gelu_python")
gelu_new = get_activation("gelu_new")
gelu = get_activation("gelu")
gelu_fast = get_activation("gelu_fast")
quick_gelu = get_activation("quick_gelu")
silu = get_activation("silu")
mish = get_activation("mish")
linear_act = get_activation("linear")
rngd_gelu = get_activation("rngd_gelu")
