from __future__ import annotations
import tenex


def broadcast(shape1: tenex.Shape, shape2: tenex.Shape, /):
    dims = []
    for i in range(-1, -(max(len(shape1), len(shape2)) + 1), -1):
        d1 = 1 if i < -len(shape1) else shape1[i]
        d2 = 1 if i < -len(shape2) else shape2[i]
        if d1 == d2 or d2 == 1:
            dims.append(d1)
        elif d1 == 1:
            dims.append(d2)
        else:
            raise TypeError(
                f"{d1} and {d2} in index {i} is not compatible to broadcast"
            )
    return tenex.Shape(dims[::-1])
