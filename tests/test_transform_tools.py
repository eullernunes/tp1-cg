import math

from src.models import Line, Point, Polygon, Scene
from src.tools._geometry import normalize_rect
from src.tools.transform_tools import (
    ReflectXTool,
    ReflectXYTool,
    ReflectYTool,
    RotateTool,
    ScaleTool,
    SelectTool,
    TranslateTool,
)


def test_normalize_rect_orders_min_and_max_regardless_of_drag_direction():
    assert normalize_rect((10, 10), (0, 0)) == (0, 0, 10, 10)
    assert normalize_rect((0, 0), (10, 10)) == (0, 0, 10, 10)


def test_select_tool_selects_objects_on_mouse_up():
    scene = Scene()
    inside = Line((5, 5), (8, 8))
    outside = Line((100, 100), (110, 110))
    scene.lines = [inside, outside]
    tool = SelectTool(scene)

    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((20, 20))
    assert scene.preview_rect == (0, 0, 20, 20)  # visible while dragging

    tool.on_mouse_up((20, 20))

    assert scene.selected_lines == [inside]
    assert tool.current_rect is None  # preview cleared after release
    assert scene.preview_rect is None  # preview cleared after release


def test_select_tool_ignores_zero_area_rectangle():
    scene = Scene()
    scene.lines = [Line((5, 5), (8, 8))]
    tool = SelectTool(scene)

    tool.on_mouse_down((5, 5))
    tool.on_mouse_up((5, 5))

    assert scene.selected_lines == []


def test_translate_tool_moves_selected_line_by_drag_delta():
    scene = Scene()
    line = Line((0, 0), (10, 0))
    scene.selected_lines = [line]
    tool = TranslateTool(scene)

    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((5, 3))

    assert line.start == (5, 3)
    assert line.end == (15, 3)


def test_translate_tool_with_nothing_selected_is_a_noop():
    scene = Scene()
    tool = TranslateTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((5, 3))  # must not raise


def test_rotate_tool_rotates_selected_polygon_around_its_centroid():
    scene = Scene()
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])  # centroid (1, 1)
    scene.selected_polygons = [polygon]
    tool = RotateTool(scene)

    tool.on_mouse_down((3, 1))  # angle 0 degrees from centroid
    tool.on_mouse_drag((1, 3))  # angle 90 degrees from centroid

    x, y = polygon.vertices[0]
    assert math.isclose(x, 2, abs_tol=1e-6)
    assert math.isclose(y, 0, abs_tol=1e-6)


def test_rotate_tool_with_nothing_selected_is_a_noop():
    scene = Scene()
    tool = RotateTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((5, 3))  # must not raise


def test_scale_tool_scales_selected_line_around_centroid():
    scene = Scene()
    line = Line((0, 0), (4, 0))  # centroid (2, 0)
    scene.selected_lines = [line]
    tool = ScaleTool(scene)

    tool.on_mouse_down((4, 0))  # distance 2 from centroid
    tool.on_mouse_drag((6, 0))  # distance 4 from centroid -> factor 2

    assert line.start == (-2, 0)
    assert line.end == (6, 0)


def test_scale_tool_with_nothing_selected_is_a_noop():
    scene = Scene()
    tool = ScaleTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((5, 3))  # must not raise


def test_reflect_x_tool_reflects_selected_line_around_centroid():
    scene = Scene()
    line = Line((0, -2), (0, 2))  # centroid (0, 0)
    scene.selected_lines = [line]
    ReflectXTool(scene).on_mouse_down((0, 0))
    assert line.start == (0, 2)
    assert line.end == (0, -2)


def test_reflect_y_tool_reflects_selected_line_around_centroid():
    scene = Scene()
    line = Line((-2, 0), (2, 0))  # centroid (0, 0)
    scene.selected_lines = [line]
    ReflectYTool(scene).on_mouse_down((0, 0))
    assert line.start == (2, 0)
    assert line.end == (-2, 0)


def test_reflect_xy_tool_reflects_selected_line_around_centroid():
    scene = Scene()
    line = Line((1, 1), (3, 3))  # centroid (2, 2)
    scene.selected_lines = [line]
    ReflectXYTool(scene).on_mouse_down((0, 0))
    assert line.start == (3, 3)
    assert line.end == (1, 1)


def test_reflect_tool_with_nothing_selected_is_a_noop():
    scene = Scene()
    ReflectXTool(scene).on_mouse_down((0, 0))  # must not raise


def test_select_tool_zero_area_click_preserves_existing_selection():
    scene = Scene()
    existing_line = Line((5, 5), (8, 8))
    scene.lines = [existing_line]
    scene.selected_lines = [existing_line]
    tool = SelectTool(scene)

    tool.on_mouse_down((10, 10))
    tool.on_mouse_up((10, 10))  # zero-area click

    assert scene.selected_lines == [existing_line]  # selection unchanged


def test_translate_tool_moves_selected_point_by_drag_delta():
    scene = Scene()
    point = Point(0, 0)
    scene.points = [point]
    scene.selected_points = [point]
    tool = TranslateTool(scene)

    tool.on_mouse_down((0, 0))
    tool.on_mouse_drag((5, 3))

    assert point.x == 5
    assert point.y == 3


def test_rotate_tool_cumulative_rotations_across_multiple_drags():
    scene = Scene()
    polygon = Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])  # centroid (1, 1)
    scene.selected_polygons = [polygon]
    tool = RotateTool(scene)

    # First drag: angle 0 to angle 90 (90 degree rotation)
    tool.on_mouse_down((3, 1))  # angle 0 degrees from centroid (1, 1)
    tool.on_mouse_drag((1, 3))  # angle 90 degrees from centroid

    # Second drag: angle 90 to angle 180 (another 90 degree rotation)
    tool.on_mouse_drag((-1, 1))  # angle 180 degrees from centroid

    # Total rotation should be 180 degrees, so vertex[0] should be at (2, 2)
    x, y = polygon.vertices[0]
    assert math.isclose(x, 2, abs_tol=1e-6)
    assert math.isclose(y, 2, abs_tol=1e-6)
