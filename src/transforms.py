import math
from typing import List, Tuple

Vertex = Tuple[float, float]


def translate(vertices: List[Vertex], dx: float, dy: float) -> List[Vertex]:
    return [(x + dx, y + dy) for x, y in vertices]


def rotate(vertices: List[Vertex], angle_degrees: float, pivot: Vertex) -> List[Vertex]:
    angle = math.radians(angle_degrees)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    px, py = pivot
    result = []
    for x, y in vertices:
        tx, ty = x - px, y - py
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a
        result.append((rx + px, ry + py))
    return result


def scale(vertices: List[Vertex], sx: float, sy: float, pivot: Vertex) -> List[Vertex]:
    px, py = pivot
    return [((x - px) * sx + px, (y - py) * sy + py) for x, y in vertices]


def reflect(vertices: List[Vertex], axis: str, pivot: Vertex) -> List[Vertex]:
    px, py = pivot
    result = []
    for x, y in vertices:
        tx, ty = x - px, y - py
        if axis == "x":
            tx, ty = tx, -ty
        elif axis == "y":
            tx, ty = -tx, ty
        elif axis == "xy":
            tx, ty = -tx, -ty
        else:
            raise ValueError(f"unknown reflection axis: {axis!r}")
        result.append((tx + px, ty + py))
    return result
