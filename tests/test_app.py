from unittest.mock import patch

import pygame

from src.app import (
    TOOL_CATEGORIES,
    TOOL_DEFINITIONS,
    build_tools,
    handle_event,
    render,
    to_canvas_pos,
)
from src.constants import STROKE_COLOR
from src.framebuffer import Framebuffer
from src.models import Scene
from src.ui import PANEL_WIDTH, UNDO_CLICK_RESULT, ToolPanel


def test_to_canvas_pos_subtracts_panel_width_offset():
    assert to_canvas_pos((PANEL_WIDTH + 5, 20)) == (5, 20)


def test_clicking_a_panel_button_switches_active_tool():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    target_label, target_key = next(
        (label, key) for label, key in TOOL_DEFINITIONS if key == "circle"
    )
    button = next(b for b in panel.buttons if b.tool_key == target_key)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=button.rect.center)

    new_active = handle_event(scene, panel, tools, panel.active_tool_key, event)

    assert new_active == target_key


def test_drag_on_canvas_creates_a_line_at_canvas_relative_coordinates():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    active = "line_dda"

    down_pos = (PANEL_WIDTH + 10, 20)
    up_pos = (PANEL_WIDTH + 60, 20)
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=down_pos))
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONUP, pos=up_pos))

    assert len(scene.lines) == 1
    assert scene.lines[0].start == (10, 20)
    assert scene.lines[0].end == (60, 20)


def test_render_draws_a_line_into_the_framebuffer():
    scene = Scene()
    tools = build_tools(scene)
    tools["line_bresenham"].on_mouse_down((0, 0))
    tools["line_bresenham"].on_mouse_up((5, 0))
    fb = Framebuffer(20, 20)

    render(scene, fb)

    assert fb.get_pixel(0, 0) == STROKE_COLOR
    assert fb.get_pixel(5, 0) == STROKE_COLOR


def test_point_tool_click_creates_a_point_that_render_draws():
    scene = Scene()
    tools = build_tools(scene)
    tools["point"].on_mouse_down((4, 4))
    fb = Framebuffer(20, 20)

    render(scene, fb)

    assert fb.get_pixel(4, 4) == STROKE_COLOR


def test_polygon_close_click_does_not_change_active_tool_or_panel_highlight():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)

    circle_button = next(b for b in panel.buttons if b.tool_key == "circle")
    active = handle_event(
        scene, panel, tools, panel.active_tool_key,
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=circle_button.rect.center),
    )
    assert active == "circle"
    assert panel.active_tool_key == "circle"

    close_button = next(b for b in panel.buttons if b.tool_key == "polygon_close")
    active = handle_event(
        scene, panel, tools, active,
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=close_button.rect.center),
    )

    assert active == "circle"
    assert panel.active_tool_key == "circle"


def test_mousemotion_with_button_held_drags_the_active_tool():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    active = "select"

    down_pos = (PANEL_WIDTH + 5, 5)
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=down_pos))

    drag_pos = (PANEL_WIDTH + 30, 30)
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEMOTION, pos=drag_pos, buttons=(1, 0, 0)))

    assert tools["select"].current_rect == (5, 5, 30, 30)

    up_pos = (PANEL_WIDTH + 30, 30)
    handle_event(scene, panel, tools, active,
                 pygame.event.Event(pygame.MOUSEBUTTONUP, pos=up_pos))


def test_mousemotion_without_button_held_does_not_drag():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    active = "select"

    down_pos = (PANEL_WIDTH + 5, 5)
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=down_pos))

    move_pos = (PANEL_WIDTH + 30, 30)
    handle_event(scene, panel, tools, active,
                 pygame.event.Event(pygame.MOUSEMOTION, pos=move_pos, buttons=(0, 0, 0)))

    assert tools["select"].current_rect is None


def test_clicking_a_category_tab_switches_visible_tools_via_handle_event():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    fill_tab = panel.category_buttons[3]  # "Preencher"

    active = handle_event(
        scene, panel, tools, panel.active_tool_key,
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=fill_tab.rect.center),
    )

    assert active == panel.active_tool_key  # unchanged, only the visible category switched
    assert panel.active_category_index == 3
    assert {b.tool_key for b in panel.buttons} == {
        "boundary_fill_4", "boundary_fill_8", "flood_fill_4", "flood_fill_8",
    }


def test_clicking_the_color_swatch_sets_scene_fill_color():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    fill_tab = panel.category_buttons[3]  # "Preencher"
    handle_event(scene, panel, tools, panel.active_tool_key,
                 pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=fill_tab.rect.center))
    assert panel.color_swatch_rect is not None

    swatch_click_pos = panel.color_swatch_rect.topleft  # white corner (hue=0, sat=0)
    handle_event(scene, panel, tools, panel.active_tool_key,
                 pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=swatch_click_pos))

    assert scene.fill_color == (255, 255, 255)


def test_clicking_the_undo_button_via_handle_event_reverts_the_last_action():
    scene = Scene()
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)

    # Draw a line -- this pushes an undo snapshot before appending it.
    active = "line_dda"
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(PANEL_WIDTH + 5, 5)))
    active = handle_event(scene, panel, tools, active,
                           pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(PANEL_WIDTH + 50, 5)))
    assert len(scene.lines) == 1

    result_active = handle_event(scene, panel, tools, active,
                                  pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=panel.undo_button.rect.center))

    assert len(scene.lines) == 0
    assert result_active == active  # undo doesn't change the active tool


def test_render_draws_in_progress_polygon_vertices_before_closing():
    scene = Scene()
    tools = build_tools(scene)
    tools["polygon"].on_mouse_down((5, 5))
    tools["polygon"].on_mouse_down((15, 5))
    fb = Framebuffer(20, 20)

    render(scene, fb)

    assert fb.get_pixel(5, 5) == STROKE_COLOR
    assert fb.get_pixel(15, 5) == STROKE_COLOR
    assert len(scene.polygons) == 0  # not closed yet


def test_render_draws_the_preview_rect_while_selecting():
    from src.constants import PREVIEW_RECT_COLOR

    scene = Scene()
    tools = build_tools(scene)
    tools["select"].on_mouse_down((2, 2))
    tools["select"].on_mouse_drag((10, 2))  # drag along the top edge only
    fb = Framebuffer(20, 20)

    render(scene, fb)

    assert fb.get_pixel(2, 2) == PREVIEW_RECT_COLOR
    assert fb.get_pixel(10, 2) == PREVIEW_RECT_COLOR


def test_render_draws_nothing_extra_once_the_drag_ends():
    from src.constants import PREVIEW_RECT_COLOR

    scene = Scene()
    tools = build_tools(scene)
    tools["select"].on_mouse_down((2, 2))
    tools["select"].on_mouse_drag((10, 10))
    tools["select"].on_mouse_up((10, 10))
    fb = Framebuffer(20, 20)

    render(scene, fb)

    assert fb.get_pixel(2, 2) != PREVIEW_RECT_COLOR


def test_render_only_runs_flood_fill_once_across_multiple_frames():
    scene = Scene()
    tools = build_tools(scene)
    tools["polygon"].on_mouse_down((2, 2))
    tools["polygon"].on_mouse_down((12, 2))
    tools["polygon"].on_mouse_down((12, 12))
    tools["polygon"].on_mouse_down((2, 12))
    tools["polygon"].close()
    tools["flood_fill_4"].on_mouse_down((7, 7))
    fb = Framebuffer(20, 20)

    with patch("src.app.flood_fill") as mock_flood_fill:
        render(scene, fb)
        render(scene, fb)
        render(scene, fb)

    assert mock_flood_fill.call_count == 1
    assert "surface" in scene.fills[0]


def test_render_replays_cached_fill_pixels_on_later_frames_without_the_seed():
    scene = Scene()
    tools = build_tools(scene)
    tools["polygon"].on_mouse_down((2, 2))
    tools["polygon"].on_mouse_down((12, 2))
    tools["polygon"].on_mouse_down((12, 12))
    tools["polygon"].on_mouse_down((2, 12))
    tools["polygon"].close()
    tools["flood_fill_4"].on_mouse_down((7, 7))
    fb = Framebuffer(20, 20)

    render(scene, fb)  # computes and caches the fill
    fb.clear()  # simulate the next frame's fb.clear() before vectors are redrawn
    render(scene, fb)  # should replay from the cache, not re-run flood_fill

    from src.constants import FILL_COLOR
    assert fb.get_pixel(7, 7) == FILL_COLOR


def test_render_applies_flood_fill_requests_after_drawing_objects():
    scene = Scene()
    tools = build_tools(scene)
    # A closed 10x10 square polygon to flood-fill the interior of.
    tools["polygon"].on_mouse_down((2, 2))
    tools["polygon"].on_mouse_down((12, 2))
    tools["polygon"].on_mouse_down((12, 12))
    tools["polygon"].on_mouse_down((2, 12))
    tools["polygon"].close()
    tools["flood_fill_4"].on_mouse_down((7, 7))
    fb = Framebuffer(20, 20)

    render(scene, fb)

    from src.constants import FILL_COLOR
    assert fb.get_pixel(7, 7) == FILL_COLOR
