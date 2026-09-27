from src.framebuffer import Framebuffer


def test_new_framebuffer_is_filled_with_background_color():
    fb = Framebuffer(10, 10, background=(255, 255, 255))
    assert fb.get_pixel(0, 0) == (255, 255, 255)
    assert fb.get_pixel(9, 9) == (255, 255, 255)


def test_set_pixel_then_get_pixel_returns_set_color():
    fb = Framebuffer(10, 10)
    fb.set_pixel(3, 4, (10, 20, 30))
    assert fb.get_pixel(3, 4) == (10, 20, 30)


def test_set_pixel_out_of_bounds_is_ignored():
    fb = Framebuffer(10, 10)
    fb.set_pixel(-1, 0, (1, 2, 3))
    fb.set_pixel(0, 100, (1, 2, 3))
    assert fb.get_pixel(-1, 0) is None
    assert fb.get_pixel(0, 100) is None


def test_clear_resets_to_background_color():
    fb = Framebuffer(5, 5, background=(0, 0, 0))
    fb.set_pixel(2, 2, (255, 255, 255))
    fb.clear()
    assert fb.get_pixel(2, 2) == (0, 0, 0)
