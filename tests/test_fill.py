import pytest

from src.fill import boundary_fill, flood_fill

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class GridFramebuffer:
    """In-memory pixel grid, no pygame dependency, for fast fill tests."""

    def __init__(self, width, height, background=WHITE):
        self.width = width
        self.height = height
        self._pixels = {(x, y): background for x in range(width) for y in range(height)}

    def get_pixel(self, x, y):
        return self._pixels.get((x, y))

    def set_pixel(self, x, y, color):
        if (x, y) in self._pixels:
            self._pixels[x, y] = color

    def draw_rect_border(self, x0, y0, x1, y1, color):
        for x in range(x0, x1 + 1):
            self.set_pixel(x, y0, color)
            self.set_pixel(x, y1, color)
        for y in range(y0, y1 + 1):
            self.set_pixel(x0, y, color)
            self.set_pixel(x1, y, color)


def test_boundary_fill_stops_at_border_color():
    fb = GridFramebuffer(10, 10)
    fb.draw_rect_border(2, 2, 6, 6, BLACK)

    boundary_fill(fb, seed=(4, 4), border_color=BLACK, fill_color=RED, connectivity=4)

    assert fb.get_pixel(4, 4) == RED
    assert fb.get_pixel(3, 3) == RED
    assert fb.get_pixel(2, 2) == BLACK  # border untouched
    assert fb.get_pixel(0, 0) == WHITE  # outside region untouched


def test_boundary_fill_seed_outside_canvas_is_a_noop():
    fb = GridFramebuffer(10, 10)
    boundary_fill(fb, seed=(100, 100), border_color=BLACK, fill_color=RED, connectivity=4)
    # no exception raised, nothing changed
    assert all(color == WHITE for color in fb._pixels.values())


def test_boundary_fill_seed_on_border_is_a_noop():
    fb = GridFramebuffer(10, 10)
    fb.draw_rect_border(2, 2, 6, 6, BLACK)

    boundary_fill(fb, seed=(2, 2), border_color=BLACK, fill_color=RED, connectivity=4)

    assert fb.get_pixel(4, 4) == WHITE  # interior was never touched


def _draw_plus_pinch(fb):
    """A solid 5x5 border with cross-arms that wall off the four interior
    corners and the center from each other via 4-connectivity, while
    leaving them reachable diagonally (8-connectivity only)."""
    fb.draw_rect_border(0, 0, 4, 4, BLACK)
    for x, y in [(2, 1), (2, 3), (1, 2), (3, 2)]:
        fb.set_pixel(x, y, BLACK)


def test_boundary_fill_4_connectivity_cannot_cross_a_diagonal_only_gap():
    fb = GridFramebuffer(10, 10)
    _draw_plus_pinch(fb)

    boundary_fill(fb, seed=(1, 1), border_color=BLACK, fill_color=RED, connectivity=4)

    assert fb.get_pixel(1, 1) == RED
    assert fb.get_pixel(2, 2) == WHITE  # only reachable diagonally from (1,1)


def test_boundary_fill_8_connectivity_crosses_a_diagonal_only_gap():
    fb = GridFramebuffer(10, 10)
    _draw_plus_pinch(fb)

    boundary_fill(fb, seed=(1, 1), border_color=BLACK, fill_color=RED, connectivity=8)

    assert fb.get_pixel(1, 1) == RED
    assert fb.get_pixel(2, 2) == RED  # reached diagonally
    assert fb.get_pixel(3, 3) == RED  # reached through a chain of diagonal steps


def test_flood_fill_replaces_contiguous_target_color():
    fb = GridFramebuffer(10, 10)
    GREEN = (0, 200, 0)
    for x in range(2, 7):
        for y in range(2, 7):
            fb.set_pixel(x, y, GREEN)

    flood_fill(fb, seed=(4, 4), target_color=GREEN, fill_color=RED, connectivity=4)

    assert fb.get_pixel(4, 4) == RED
    assert fb.get_pixel(2, 2) == RED  # whole green region replaced
    assert fb.get_pixel(0, 0) == WHITE  # background outside the region untouched


def test_flood_fill_does_not_cross_non_target_color_border():
    fb = GridFramebuffer(10, 10)
    fb.draw_rect_border(2, 2, 6, 6, BLACK)

    flood_fill(fb, seed=(4, 4), target_color=WHITE, fill_color=RED, connectivity=4)

    assert fb.get_pixel(4, 4) == RED
    assert fb.get_pixel(0, 0) == WHITE  # outside the border stays untouched


def test_flood_fill_seed_not_matching_target_color_is_a_noop():
    fb = GridFramebuffer(10, 10)
    fb.set_pixel(4, 4, BLACK)

    flood_fill(fb, seed=(4, 4), target_color=WHITE, fill_color=RED, connectivity=4)

    assert fb.get_pixel(4, 4) == BLACK


def test_flood_fill_invalid_connectivity_raises_value_error():
    fb = GridFramebuffer(10, 10)
    with pytest.raises(ValueError):
        flood_fill(fb, seed=(0, 0), target_color=WHITE, fill_color=RED, connectivity=5)
