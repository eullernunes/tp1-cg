from src.models import Line, Scene
from src.tools.clip_tools import ClipCohenSutherlandTool, ClipLiangBarskyTool


def test_clip_tool_sets_clip_window_and_clips_lines_on_release():
    scene = Scene()
    scene.lines = [
        Line((0, 50), (100, 50)),   # crosses the window, gets shortened
        Line((-50, -50), (-10, -10)),  # fully outside, gets dropped
    ]
    tool = ClipCohenSutherlandTool(scene)

    tool.on_mouse_down((10, 10))
    tool.on_mouse_drag((90, 90))
    assert scene.preview_rect == (10, 10, 90, 90)  # visible while dragging

    tool.on_mouse_up((90, 90))

    assert scene.clip_window == (10, 10, 90, 90)
    assert len(scene.lines) == 1
    assert scene.lines[0].start == (10, 50)
    assert scene.lines[0].end == (90, 50)
    assert scene.preview_rect is None  # cleared after release


def test_liang_barsky_clip_tool_produces_same_result_as_cohen_sutherland():
    def make_scene():
        scene = Scene()
        scene.lines = [Line((0, 50), (100, 50))]
        return scene

    cs_scene = make_scene()
    lb_scene = make_scene()

    tool_cs = ClipCohenSutherlandTool(cs_scene)
    tool_cs.on_mouse_down((10, 10))
    tool_cs.on_mouse_up((90, 90))

    tool_lb = ClipLiangBarskyTool(lb_scene)
    tool_lb.on_mouse_down((10, 10))
    tool_lb.on_mouse_up((90, 90))

    assert cs_scene.lines[0].start == lb_scene.lines[0].start
    assert cs_scene.lines[0].end == lb_scene.lines[0].end


def test_clip_tool_ignores_zero_area_rectangle():
    """Verify that zero-area rectangles are a true no-op, not a reset.

    First perform a real clip to set state, then verify a zero-area click
    leaves that state unchanged (not reset to defaults).
    """
    scene = Scene()
    # Start with two lines
    line1 = Line((0, 50), (100, 50))
    line2 = Line((-50, -50), (-10, -10))
    scene.lines = [line1, line2]
    tool = ClipCohenSutherlandTool(scene)

    # First: perform a real clip operation
    tool.on_mouse_down((10, 10))
    tool.on_mouse_drag((90, 90))
    tool.on_mouse_up((90, 90))

    # State after first clip
    first_clip_window = scene.clip_window
    first_clipped_lines = scene.lines[:]
    assert first_clip_window == (10, 10, 90, 90)
    assert len(first_clipped_lines) == 1

    # Second: perform a zero-area click (at the same point)
    tool.on_mouse_down((50, 50))
    tool.on_mouse_up((50, 50))

    # Verify state is UNCHANGED (not reset)
    assert scene.clip_window == first_clip_window
    assert scene.lines == first_clipped_lines


def test_clip_tool_preserves_selected_lines_that_are_unaffected_by_clipping():
    """Verify that selected lines unaffected by clipping remain in selected_lines.

    Select a line that is fully inside the clip window (won't be modified by
    clipping), perform clipping, and verify the selection is preserved BY IDENTITY
    (not just by value equality).
    """
    scene = Scene()
    # Line fully inside the window (unaffected by clipping)
    selected_line = Line((20, 20), (80, 80))
    # Line that will be cropped
    cropped_line = Line((0, 50), (100, 50))
    scene.lines = [selected_line, cropped_line]
    scene.selected_lines = [selected_line]

    tool = ClipCohenSutherlandTool(scene)
    tool.on_mouse_down((10, 10))
    tool.on_mouse_up((90, 90))

    # The selected line is still in the scene's lines
    assert any(line.start == selected_line.start and line.end == selected_line.end
               for line in scene.lines)
    # The selection should still contain the unmodified line
    assert len(scene.selected_lines) == 1
    assert scene.selected_lines[0].start == selected_line.start
    assert scene.selected_lines[0].end == selected_line.end

    # CRITICAL: Verify OBJECT IDENTITY, not just value equality
    # The selected_lines entry must be the SAME OBJECT that's now in scene.lines
    matching_line = None
    for line in scene.lines:
        if line.start == selected_line.start and line.end == selected_line.end:
            matching_line = line
            break
    assert matching_line is not None, "No matching line found in scene.lines"
    assert scene.selected_lines[0] is matching_line, \
        "selected_lines contains stale object reference, not the new clipped object"


def test_clip_tool_removes_selected_lines_that_are_clipped_or_dropped():
    """Verify that selected lines that are clipped to None are removed from selected_lines.

    Select a line that is fully outside the clip window (will be dropped),
    perform clipping, and verify it's removed from the selection.
    """
    scene = Scene()
    # Line fully outside the window (will be dropped)
    outside_line = Line((-50, -50), (-10, -10))
    # Line inside the window (will survive)
    inside_line = Line((20, 20), (80, 80))
    scene.lines = [outside_line, inside_line]
    scene.selected_lines = [outside_line, inside_line]

    tool = ClipCohenSutherlandTool(scene)
    tool.on_mouse_down((10, 10))
    tool.on_mouse_up((90, 90))

    # Only the inside line survives
    assert len(scene.lines) == 1
    assert scene.lines[0].start == inside_line.start
    # Selection should only have the inside line
    assert len(scene.selected_lines) == 1
    assert scene.selected_lines[0].start == inside_line.start


def test_clip_tool_preserves_selected_line_identity_for_multiple_lines():
    """Behavioral test: verify object identity for selected lines among multiple lines.

    This test proves the identity fix actually matters: when multiple lines exist
    and one is selected, clipping should preserve that specific selection by
    remapping it to the new object that corresponds to the original selected line
    (by identity), not by value equality.
    """
    scene = Scene()
    # Multiple lines, one of which is selected
    line1 = Line((30, 30), (70, 70))  # Will be selected
    line2 = Line((20, 20), (40, 40))  # Not selected
    line3 = Line((60, 60), (80, 80))  # Not selected
    scene.lines = [line1, line2, line3]
    scene.selected_lines = [line1]

    # Clip with a window that contains all lines
    clip_tool = ClipCohenSutherlandTool(scene)
    clip_tool.on_mouse_down((10, 10))
    clip_tool.on_mouse_up((90, 90))

    # All lines survive the clip (all inside the window)
    assert len(scene.lines) == 3
    assert len(scene.selected_lines) == 1

    # The selected_lines entry must be one of the objects now in scene.lines
    # This verifies the fix: selected_lines holds NEW objects, not stale references
    selected_line = scene.selected_lines[0]
    assert any(line is selected_line for line in scene.lines), \
        "selected_lines contains object not found in scene.lines (stale reference bug)"

    # Verify it matches the geometry of the originally-selected line
    assert selected_line.start == line1.start
    assert selected_line.end == line1.end
