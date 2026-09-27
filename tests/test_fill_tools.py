from src.constants import FILL_COLOR, STROKE_COLOR
from src.models import Scene
from src.tools.fill_tools import (
    BoundaryFillTool4,
    BoundaryFillTool8,
    FloodFillTool4,
    FloodFillTool8,
)


def test_boundary_fill_tool_4_appends_correct_fill_request():
    scene = Scene()
    BoundaryFillTool4(scene).on_mouse_down((12.4, 8.6))
    assert scene.fills == [{
        "algorithm": "boundary",
        "seed": (12, 9),
        "border_color": STROKE_COLOR,
        "fill_color": FILL_COLOR,
        "connectivity": 4,
    }]


def test_boundary_fill_tool_8_uses_connectivity_8():
    scene = Scene()
    BoundaryFillTool8(scene).on_mouse_down((0, 0))
    assert scene.fills[0]["connectivity"] == 8


def test_flood_fill_tool_4_appends_correct_fill_request():
    scene = Scene()
    FloodFillTool4(scene).on_mouse_down((5, 5))
    assert scene.fills == [{
        "algorithm": "flood",
        "seed": (5, 5),
        "fill_color": FILL_COLOR,
        "connectivity": 4,
    }]


def test_flood_fill_tool_8_uses_connectivity_8():
    scene = Scene()
    FloodFillTool8(scene).on_mouse_down((0, 0))
    assert scene.fills[0]["connectivity"] == 8
