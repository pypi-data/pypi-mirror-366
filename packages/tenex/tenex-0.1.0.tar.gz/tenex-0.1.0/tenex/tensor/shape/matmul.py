from __future__ import annotations
import tenex


def matmul(shape1: tenex.Shape, shape2: tenex.Shape):
    assert shape1 and shape2, TypeError(f"{len(shape1)}-D and {len(shape2)}-D")
    if len(shape2) == 1:
        assert shape2[-1] == shape1[-1], TypeError()
        return shape1[:-1]
    assert shape2[-2] == shape1[-1], TypeError()
    return shape1[:-1] ** shape2[:-2] * shape2[-1]
