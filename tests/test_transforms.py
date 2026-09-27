import math

import pytest

from src.transforms import reflect, rotate, scale, translate


def test_translate_shifts_all_vertices_by_dx_dy():
    result = translate([(0, 0), (1, 2)], dx=5, dy=-3)
    assert result == [(5, -3), (6, -1)]


def test_rotate_90_degrees_around_origin():
    result = rotate([(1, 0)], angle_degrees=90, pivot=(0, 0))
    x, y = result[0]
    assert math.isclose(x, 0, abs_tol=1e-9)
    assert math.isclose(y, 1, abs_tol=1e-9)


def test_rotate_around_non_origin_pivot():
    result = rotate([(2, 1)], angle_degrees=180, pivot=(1, 1))
    x, y = result[0]
    assert math.isclose(x, 0, abs_tol=1e-9)
    assert math.isclose(y, 1, abs_tol=1e-9)


def test_scale_by_factor_around_pivot():
    result = scale([(2, 2)], sx=2, sy=2, pivot=(0, 0))
    assert result == [(4, 4)]


def test_scale_around_non_origin_pivot():
    result = scale([(2, 0)], sx=3, sy=1, pivot=(1, 0))
    assert result == [(4, 0)]


def test_reflect_x_flips_y_around_pivot():
    result = reflect([(1, 2)], axis="x", pivot=(0, 0))
    assert result == [(1, -2)]


def test_reflect_y_flips_x_around_pivot():
    result = reflect([(1, 2)], axis="y", pivot=(0, 0))
    assert result == [(-1, 2)]


def test_reflect_xy_flips_both_around_pivot():
    result = reflect([(1, 2)], axis="xy", pivot=(0, 0))
    assert result == [(-1, -2)]


def test_reflect_unknown_axis_raises_value_error():
    with pytest.raises(ValueError):
        reflect([(1, 2)], axis="z", pivot=(0, 0))
