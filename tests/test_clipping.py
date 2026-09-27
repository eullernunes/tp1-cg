import math

from src.clipping import cohen_sutherland, liang_barsky
from src.models import Line

WINDOW = (10, 10, 90, 90)


def _assert_points_close(actual, expected):
    assert math.isclose(actual[0], expected[0], abs_tol=1e-6)
    assert math.isclose(actual[1], expected[1], abs_tol=1e-6)


def test_line_fully_inside_window_is_unchanged():
    line = Line((20, 20), (80, 80))
    for clip in (cohen_sutherland, liang_barsky):
        result = clip(line, WINDOW)
        assert result is not None
        _assert_points_close(result.start, (20, 20))
        _assert_points_close(result.end, (80, 80))


def test_line_fully_outside_window_returns_none():
    line = Line((-50, -50), (-10, -10))
    for clip in (cohen_sutherland, liang_barsky):
        assert clip(line, WINDOW) is None


def test_line_crossing_left_edge_is_clipped():
    line = Line((0, 50), (50, 50))
    for clip in (cohen_sutherland, liang_barsky):
        result = clip(line, WINDOW)
        assert result is not None
        _assert_points_close(result.start, (10, 50))
        _assert_points_close(result.end, (50, 50))


def test_line_crossing_right_edge_is_clipped():
    line = Line((50, 50), (150, 50))
    for clip in (cohen_sutherland, liang_barsky):
        result = clip(line, WINDOW)
        assert result is not None
        _assert_points_close(result.start, (50, 50))
        _assert_points_close(result.end, (90, 50))


def test_line_crossing_top_and_bottom_edges_is_clipped():
    line = Line((50, 0), (50, 150))
    for clip in (cohen_sutherland, liang_barsky):
        result = clip(line, WINDOW)
        assert result is not None
        _assert_points_close(result.start, (50, 10))
        _assert_points_close(result.end, (50, 90))


def test_diagonal_line_crossing_two_corners_matches_between_algorithms():
    line = Line((0, 0), (100, 100))
    cs = cohen_sutherland(line, WINDOW)
    lb = liang_barsky(line, WINDOW)
    assert cs is not None and lb is not None
    _assert_points_close(cs.start, lb.start)
    _assert_points_close(cs.end, lb.end)
