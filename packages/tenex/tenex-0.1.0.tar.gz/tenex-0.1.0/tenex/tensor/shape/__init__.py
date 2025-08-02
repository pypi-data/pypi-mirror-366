from __future__ import annotations
from typing import overload, override
from collections.abc import Sequence
from .broadcast import broadcast
from .matmul import matmul
from .stack import stack

__all__ = ["Shape", "InputShape"]

type InputShape = int | Sequence[int]


def from_input_shape(shape: InputShape):
    if isinstance(shape, int):
        return [int(shape)]
    if isinstance(shape, Sequence):
        return shape
    raise ValueError(f"the order of {type(shape)} is not stable")


def view(shape: Shape, *dims: int):
    if not dims:
        raise TypeError("`view` takes at least 1 positional arguments, but 0 given")
    size, indices, dims = 1, [], list(dims)
    for i, dim in enumerate(dims):
        if dim < 0:
            indices.append(i)
        else:
            size *= dim
    dim, mod = divmod(shape.size(), size)
    if mod != 0:
        raise ValueError(
            f"`view` requires modulo of `{shape} % {Shape.__repr__(dims)}` to be `0`, but got `{mod}`"
        )
    if dim == 1 or len(indices) == 1:
        for i in indices:
            dims[i] = dim
    elif len(indices):
        raise ValueError(
            f"`view` can not infer values for `?` in `{Shape.__repr__(dims)}`"
        )
    else:
        raise ValueError(
            f"`view` expects size of `{Shape.__repr__(dims)}` to be {shape.size()}, but got {size}"
        )
    return Shape(dims)


_scalar_shape = None


class Shape(tuple):

    def __new__(cls, *shapes: InputShape):
        if shapes == ():
            global _scalar_shape
            if _scalar_shape is None:
                _scalar_shape = super().__new__(cls)
            return _scalar_shape
        shape, *shapes = shapes
        if isinstance(shape, Shape):
            return shape
        shape = super().__new__(cls, from_input_shape(shape))
        for dim in shape:
            assert type(dim) is int and dim >= 0, TypeError(
                f"{dim} {type(dim)} is not int"
            )
        return shape * Shape(*shapes) if shapes else shape

    @overload
    def __getitem__(self, key: int) -> int:
        """retrieve dim in key position by int of key"""

    @overload
    def __getitem__(self, key: slice) -> Shape:
        """retrieve dim in key position by int of key"""

    @overload
    def __getitem__(self, key: Sequence[int, slice, Sequence[int]]) -> Shape:
        """retrieve dim in key position by int of key"""

    @override
    def __getitem__(self, key: int | slice | Sequence[int, slice, Sequence[int]]):
        """retrieve dim in key position by int of key"""
        if isinstance(key, Sequence):
            raise NotImplemented("TODO: reshape by permute dimensions")
        if isinstance(key, slice):
            return Shape(super().__getitem__(key))
        return super().__getitem__(key)

    def __add__(self, shape: InputShape):
        try:
            return stack(self, Shape(shape))
        except:
            return None

    def __radd__(self, shape: InputShape):
        return self + shape

    def __mul__(self, shape: InputShape):
        return Shape(super().__add__(Shape(shape)))

    def __rmul__(self, shape: InputShape):
        return Shape(shape) * self

    def __pow__(self, shape: InputShape):
        try:
            return broadcast(self, Shape(shape))
        except:
            return None

    def __rpow__(self, shape: InputShape):
        return self**shape

    def __matmul__(self, shape: InputShape):
        try:
            return matmul(self, Shape(shape))
        except:
            return None

    def __rmatmul__(self, shape: InputShape):
        return Shape(shape) @ self

    @overload
    def __eq__(self, value: int) -> bool:
        """作为size: int比较"""

    @overload
    def __eq__(self, shape: Sequence[int]) -> bool:
        """作为dims: tuple比较"""

    @override
    def __eq__(self, value: InputShape):
        if isinstance(value, int):
            return int(self) == value
        return super().__eq__(tuple(value))

    @overload
    def __lt__(self, value: int) -> bool:
        """作为size: int比较"""

    @overload
    def __lt__(self, shape: Sequence[int]) -> bool:
        """作为dims: tuple比较"""

    @override
    def __lt__(self, value: InputShape):
        if isinstance(value, int):
            return int(self) < value
        return super().__lt__(tuple(value))

    @overload
    def __le__(self, value: int) -> bool:
        """作为size: int比较"""

    @overload
    def __le__(self, shape: Sequence[int]) -> bool:
        """作为dims: tuple比较"""

    @override
    def __le__(self, value: InputShape):
        if isinstance(value, int):
            return int(self) <= value
        return super().__le__(tuple(value))

    @overload
    def __gt__(self, value: int) -> bool:
        """作为size: int比较"""

    @overload
    def __gt__(self, shape: Sequence[int]) -> bool:
        """作为dims: tuple比较"""

    @override
    def __gt__(self, value: InputShape):
        if isinstance(value, int):
            return int(self) > value
        return super().__gt__(tuple(value))

    @overload
    def __ge__(self, value: int) -> bool:
        """作为size: int比较"""

    @overload
    def __ge__(self, shape: Sequence[int]) -> bool:
        """作为dims: tuple比较"""

    @override
    def __ge__(self, value: InputShape):
        if isinstance(value, int):
            return int(self) >= value
        return super().__ge__(tuple(value))

    def __repr__(self):
        return f"({' * '.join(str(dim) for dim in self)})"

    def __int__(self):
        from math import prod

        return prod(self)


if __name__ == "__main__":
    # creating
    assert Shape((1, 2), 3, [4, 5]) == (1, 2, 3, 4, 5)
    # stack
    assert Shape(1, 2, 3) + Shape(1, 2, 3) == (2, 1, 2, 3)
    # concat
    assert Shape(1, 4, 3) + Shape(1, 2, 3) == (1, 6, 3)
    # multiply
    assert Shape(1, 2) * (4, 5) == (1, 2, 4, 5)
    assert (4, 5) * Shape(1, 2) == (4, 5, 1, 2)
    # broadcast
    assert Shape(1, 1, 3) ** (4, 1) == (1, 4, 3)
    assert (4, 1) ** Shape(1, 3) == (4, 3)
    assert (4, 3) ** Shape(3, 4) == None
    # matmul
    assert Shape(1, 3) @ (3, 4) == Shape(1, 4)
    assert Shape(1, 3) @ 3 == Shape(1)
    assert Shape(1, 3) @ (4, 4) == None
    assert Shape(1, 3) @ () == None
    # compare as size or dims
    assert Shape(2, 3, 4) == (2, 3, 4)
    assert Shape(2, 3, 4) == 2 * 3 * 4
    assert Shape(2, 3, 4) >= (2, 3, 4)
    assert Shape(2, 3, 4) >= 2 * 3 * 4
    assert Shape(2, 3, 4) <= (2, 3, 4)
    assert Shape(2, 3, 4) <= 2 * 3 * 4
    assert Shape(2, 3, 4) != (2, 3, 1)
    assert Shape(2, 3, 4) != 2 * 3 * 1
    assert Shape(2, 3, 4) > (2, 3, 1)
    assert Shape(2, 3, 4) > 2 * 3 * 1
    assert Shape(2, 3, 1) < (2, 3, 4)
    assert Shape(2, 3, 1) < 2 * 3 * 4

    # index and slice
    assert isinstance(Shape(range(4))[1:2], Shape)
    assert isinstance(Shape(range(4))[1], int)
    # view & size
    # assert Shape(2, 3, 4).view(2, 3, 4, -1, -2, -3) == (2, 3, 4, 1, 1, 1)
    assert int(Shape(3, 4, 5)) == 3 * 4 * 5
    # repr & str
    assert str(Shape()) == "()"
    assert str(Shape(3)) == "(3)"
    assert str(Shape(3, 4)) == "(3 * 4)"
    assert str(Shape(3, 4)) == repr(Shape(3, 4))
    # remain tuple like, singleton
    assert id(()) == id(()) and Shape() is Shape()
    a, b = (1, 2, 3), Shape(1, 2, 3)
    assert a is tuple(a) and b is Shape(b)
    print("all good")
