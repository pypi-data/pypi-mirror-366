from __future__ import annotations
from typing import overload
import tenex


@overload
def arange(shape: tenex.InputShape, /, *, dtype=None) -> tenex.Tensor: ...
@overload
def arange(
    start: int, shape: tenex.InputShape, step: int | float = 0, /, *, dtype=None
) -> tenex.Tensor: ...


def arange(*args, dtype=None):
    assert len(args) > 1 and len(args) <= 3
