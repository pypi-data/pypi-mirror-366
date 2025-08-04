"""The Reference Generator Implementation for FuriosaAI LLM Engine

This module provides the reference implementation of how to interact with our own models which are
usually modified for our LLM Engine. This module is used for testing and development purposes.
"""

from . import tokenizer as tokenizer
from .generator import (
    OriginalGenerator,
    PreAllocatedConcatGenerator,
    PreAllocatedGenerator,
)

__all__ = [
    "OriginalGenerator",
    "PreAllocatedGenerator",
    "PreAllocatedConcatGenerator",
]
