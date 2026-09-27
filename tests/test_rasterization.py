from src.rasterization import circle_bresenham, line_bresenham, line_dda


class RecordingFramebuffer:
    def __init__(self):
        self.pixels = []

    def set_pixel(self, x, y, color):
        self.pixels.append((x, y))


def test_line_dda_horizontal():
    fb = RecordingFramebuffer()
    line_dda(fb, (0, 0), (5, 0), (0, 0, 0))
    assert fb.pixels == [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)]


def test_line_dda_vertical():
    fb = RecordingFramebuffer()
    line_dda(fb, (0, 0), (0, 5), (0, 0, 0))
    assert fb.pixels == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5)]


def test_line_bresenham_diagonal_45_degrees():
    fb = RecordingFramebuffer()
    line_bresenham(fb, (0, 0), (5, 5), (0, 0, 0))
    assert fb.pixels == [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]


def test_line_bresenham_generic_slope_has_no_gaps():
    fb = RecordingFramebuffer()
    line_bresenham(fb, (0, 0), (8, 3), (0, 0, 0))
    assert fb.pixels[0] == (0, 0)
    assert fb.pixels[-1] == (8, 3)
    assert len(fb.pixels) == 9  # one pixel per unit of the dominant axis (dx=8)
    for (x0, y0), (x1, y1) in zip(fb.pixels, fb.pixels[1:]):
        assert max(abs(x1 - x0), abs(y1 - y0)) == 1


def test_line_bresenham_matches_dda_endpoints():
    fb_dda = RecordingFramebuffer()
    fb_bres = RecordingFramebuffer()
    line_dda(fb_dda, (2, 3), (9, 7), (0, 0, 0))
    line_bresenham(fb_bres, (2, 3), (9, 7), (0, 0, 0))
    assert fb_dda.pixels[0] == fb_bres.pixels[0] == (2, 3)
    assert fb_dda.pixels[-1] == fb_bres.pixels[-1] == (9, 7)


def test_circle_bresenham_includes_the_four_cardinal_points():
    fb = RecordingFramebuffer()
    circle_bresenham(fb, center=(50, 50), radius=10, color=(0, 0, 0))
    assert (60, 50) in fb.pixels
    assert (40, 50) in fb.pixels
    assert (50, 60) in fb.pixels
    assert (50, 40) in fb.pixels


def test_circle_bresenham_is_symmetric_in_all_four_quadrants():
    fb = RecordingFramebuffer()
    circle_bresenham(fb, center=(0, 0), radius=6, color=(0, 0, 0))
    pixel_set = set(fb.pixels)
    for x, y in pixel_set:
        assert (-x, y) in pixel_set
        assert (x, -y) in pixel_set
        assert (-x, -y) in pixel_set
