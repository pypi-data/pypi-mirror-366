from __future__ import annotations
from .shape import Shape, InputShape
from .dtype import DType

from .arange import arange

__all__ = [
    # tensor related core classes and types
    "Tensor",
    "Shape",
    "DType",
    "InputShape",
    # tensor creation routines
    "arange",
]


def resolve_args(*args, **kwargs):
    if len(args) == len(kwargs):
        return args
    items = list(kwargs.items())

    for arg, (key, val) in zip(args, kwargs.items()):
        pass


class Tensor:
    def __init__(self, data, shape: InputShape = None, /, *, dtype=None):
        pass
