from src.models import Scene
from src.tools.drawing_tools import (
    CircleTool,
    LineBresenhamTool,
    LineDdaTool,
    PointTool,
    PolygonTool,
)


def test_point_tool_creates_a_point_on_click():
    scene = Scene()
    tool = PointTool(scene)
    tool.on_mouse_down((7, 9))
    assert len(scene.points) == 1
    assert scene.points[0].x == 7
    assert scene.points[0].y == 9


def test_line_dda_tool_creates_line_with_dda_algorithm_on_drag():
    scene = Scene()
    tool = LineDdaTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_up((10, 0))
    assert len(scene.lines) == 1
    assert scene.lines[0].algorithm == "dda"
    assert scene.lines[0].start == (0, 0)
    assert scene.lines[0].end == (10, 0)


def test_line_bresenham_tool_creates_line_with_bresenham_algorithm():
    scene = Scene()
    tool = LineBresenhamTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_up((10, 0))
    assert len(scene.lines) == 1
    assert scene.lines[0].algorithm == "bresenham"


def test_line_tool_ignores_zero_length_drag():
    scene = Scene()
    tool = LineDdaTool(scene)
    tool.on_mouse_down((5, 5))
    tool.on_mouse_up((5, 5))
    assert len(scene.lines) == 0


def test_circle_tool_creates_circle_with_computed_radius():
    scene = Scene()
    tool = CircleTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_up((3, 4))  # 3-4-5 triangle -> radius 5
    assert len(scene.circles) == 1
    assert scene.circles[0].center == (0, 0)
    assert scene.circles[0].radius == 5


def test_circle_tool_ignores_zero_radius_drag():
    scene = Scene()
    tool = CircleTool(scene)
    tool.on_mouse_down((5, 5))
    tool.on_mouse_up((5, 5))
    assert len(scene.circles) == 0


def test_polygon_tool_ignores_close_with_fewer_than_three_vertices():
    scene = Scene()
    tool = PolygonTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_down((10, 0))
    tool.close()
    assert len(scene.polygons) == 0


def test_polygon_tool_creates_polygon_on_close_with_three_or_more_vertices():
    scene = Scene()
    tool = PolygonTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_down((10, 0))
    tool.on_mouse_down((5, 10))
    tool.close()
    assert len(scene.polygons) == 1
    assert scene.polygons[0].vertices == [(0, 0), (10, 0), (5, 10)]


def test_polygon_tool_closes_on_click_near_first_vertex():
    scene = Scene()
    tool = PolygonTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_down((10, 0))
    tool.on_mouse_down((5, 10))
    tool.on_mouse_down((2, 2))  # within CLOSE_THRESHOLD_PX of (0, 0)
    assert len(scene.polygons) == 1
    assert scene.polygons[0].vertices == [(0, 0), (10, 0), (5, 10)]


def test_polygon_tool_exposes_in_progress_vertices_as_they_are_clicked():
    scene = Scene()
    tool = PolygonTool(scene)

    tool.on_mouse_down((0, 0))
    assert scene.in_progress_polygon_vertices == [(0, 0)]

    tool.on_mouse_down((10, 0))
    assert scene.in_progress_polygon_vertices == [(0, 0), (10, 0)]


def test_polygon_tool_clears_in_progress_vertices_on_close():
    scene = Scene()
    tool = PolygonTool(scene)
    tool.on_mouse_down((0, 0))
    tool.on_mouse_down((10, 0))
    tool.on_mouse_down((5, 10))

    tool.close()

    assert scene.in_progress_polygon_vertices == []
