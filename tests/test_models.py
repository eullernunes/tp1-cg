from src.constants import FILL_COLOR
from src.models import Circle, Line, Point, Polygon, Scene


def test_select_in_rect_selects_only_overlapping_objects():
    scene = Scene()
    inside_line = Line((10, 10), (20, 20))
    outside_line = Line((100, 100), (110, 110))
    inside_point = Point(15, 15)
    outside_point = Point(200, 200)
    inside_polygon = Polygon([(5, 5), (25, 5), (15, 25)])
    outside_polygon = Polygon([(300, 300), (320, 300), (310, 320)])
    scene.lines = [inside_line, outside_line]
    scene.points = [inside_point, outside_point]
    scene.polygons = [inside_polygon, outside_polygon]

    scene.select_in_rect((0, 0, 30, 30))

    assert scene.selected_lines == [inside_line]
    assert scene.selected_points == [inside_point]
    assert scene.selected_polygons == [inside_polygon]


def test_select_in_rect_with_no_overlap_selects_nothing():
    scene = Scene()
    scene.lines = [Line((100, 100), (110, 110))]

    scene.select_in_rect((0, 0, 10, 10))

    assert scene.selected_lines == []


def test_clear_selection_empties_all_selection_lists():
    scene = Scene()
    scene.selected_lines = [Line((0, 0), (1, 1))]
    scene.selected_points = [Point(0, 0)]
    scene.selected_polygons = [Polygon([(0, 0), (1, 0), (0, 1)])]

    scene.clear_selection()

    assert scene.selected_lines == []
    assert scene.selected_points == []
    assert scene.selected_polygons == []


def test_circle_is_not_a_scene_selection_field():
    scene = Scene()
    assert not hasattr(scene, "selected_circles")
    assert isinstance(scene.circles, list)


def test_scene_defaults_fill_color_to_the_fill_color_constant():
    scene = Scene()
    assert scene.fill_color == FILL_COLOR


def test_scene_starts_with_no_in_progress_polygon_vertices():
    scene = Scene()
    assert scene.in_progress_polygon_vertices == []


def test_scene_starts_with_no_preview_rect():
    scene = Scene()
    assert scene.preview_rect is None


def test_undo_restores_the_most_recently_saved_snapshot():
    scene = Scene()
    scene.lines = [Line((0, 0), (1, 1))]
    scene.save_undo_snapshot()
    scene.lines.append(Line((2, 2), (3, 3)))

    scene.undo()

    assert scene.lines == [Line((0, 0), (1, 1))]


def test_undo_with_no_history_is_a_noop():
    scene = Scene()
    scene.lines = [Line((0, 0), (1, 1))]

    scene.undo()

    assert scene.lines == [Line((0, 0), (1, 1))]


def test_undo_pops_snapshots_in_last_in_first_out_order():
    scene = Scene()
    scene.save_undo_snapshot()  # snapshot A: lines == []
    scene.lines.append(Line((0, 0), (1, 1)))
    scene.save_undo_snapshot()  # snapshot B: lines == [line1]
    scene.lines.append(Line((2, 2), (3, 3)))

    scene.undo()
    assert scene.lines == [Line((0, 0), (1, 1))]

    scene.undo()
    assert scene.lines == []


def test_undo_clears_selection_and_in_progress_polygon():
    scene = Scene()
    line = Line((0, 0), (1, 1))
    scene.lines = [line]
    scene.save_undo_snapshot()
    scene.selected_lines = [line]
    scene.in_progress_polygon_vertices = [(5, 5)]

    scene.undo()

    assert scene.selected_lines == []
    assert scene.in_progress_polygon_vertices == []


def test_undo_history_is_capped_and_drops_the_oldest_snapshot():
    from src.models import MAX_UNDO_HISTORY

    scene = Scene()
    for i in range(MAX_UNDO_HISTORY + 5):
        scene.save_undo_snapshot()
        scene.lines.append(Line((i, i), (i + 1, i + 1)))

    for _ in range(MAX_UNDO_HISTORY):
        scene.undo()

    # The oldest 5 snapshots were dropped, so undo can't get back past
    # the 5th line ever added.
    assert len(scene.lines) == 5


def test_save_undo_snapshot_excludes_the_cached_fill_surface():
    scene = Scene()
    scene.fills = [{"algorithm": "flood", "seed": (1, 1), "surface": object()}]

    scene.save_undo_snapshot()

    assert "surface" not in scene._undo_history[-1]["fills"][0]
    assert scene._undo_history[-1]["fills"][0]["seed"] == (1, 1)
