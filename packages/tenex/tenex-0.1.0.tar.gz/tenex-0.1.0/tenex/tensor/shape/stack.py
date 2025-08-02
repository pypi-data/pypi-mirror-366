from __future__ import annotations
import tenex


def stack(shape1: tenex.Shape, shape2: tenex.Shape):
    if shape1 == shape2:
        return 2 * shape1
    if len(shape1) != len(shape2):
        raise TypeError("")
    index = -1
    for i, (dim1, dim2) in enumerate(zip(shape1, shape2)):
        if dim1 != dim2:
            if index < 0:
                index = i
            else:
                raise ValueError("")
    dim = shape1[index] + shape2[index]
    return shape1[:index] * dim * shape2[index + 1 :]
