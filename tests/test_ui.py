from src.ui import PANEL_WIDTH, UNDO_CLICK_RESULT, ToolPanel, gradient_pos_to_color

TOOLS = [
    ("Reta (DDA)", "line_dda"),
    ("Reta (Bresenham)", "line_bresenham"),
    ("Boundary-Fill (4)", "boundary_fill_4"),
]
CATEGORIES = [
    ("Desenhar", ["line_dda", "line_bresenham"]),
    ("Preencher", ["boundary_fill_4"]),
]


def test_panel_starts_with_first_tool_of_first_category_active():
    panel = ToolPanel(TOOLS, CATEGORIES)
    assert panel.active_tool_key == "line_dda"
    assert panel.active_category_index == 0


def test_contains_is_true_inside_panel_and_false_outside():
    assert ToolPanel(TOOLS, CATEGORIES).contains((10, 10)) is True
    assert ToolPanel(TOOLS, CATEGORIES).contains((PANEL_WIDTH + 10, 10)) is False


def test_handle_click_on_a_tool_button_switches_active_tool():
    panel = ToolPanel(TOOLS, CATEGORIES)
    second_button_center = panel.buttons[1].rect.center
    clicked_key = panel.handle_click(second_button_center)
    assert clicked_key == "line_bresenham"
    assert panel.active_tool_key == "line_bresenham"


def test_handle_click_outside_any_button_returns_none_and_keeps_state():
    panel = ToolPanel(TOOLS, CATEGORIES)
    result = panel.handle_click((PANEL_WIDTH - 5, 10_000))
    assert result is None
    assert panel.active_tool_key == "line_dda"


def test_handle_click_on_a_category_tab_switches_visible_tools_without_changing_active_tool():
    panel = ToolPanel(TOOLS, CATEGORIES)
    fill_tab_center = panel.category_buttons[1].rect.center

    result = panel.handle_click(fill_tab_center)

    assert result is None
    assert panel.active_category_index == 1
    assert [b.tool_key for b in panel.buttons] == ["boundary_fill_4"]
    assert panel.active_tool_key == "line_dda"  # unchanged by switching category


def test_color_swatch_only_present_on_the_fill_category():
    panel = ToolPanel(TOOLS, CATEGORIES)
    assert panel.color_swatch_rect is None  # starts on "Desenhar"

    panel.handle_click(panel.category_buttons[1].rect.center)

    assert panel.color_swatch_rect is not None


def test_clicking_the_undo_button_returns_the_undo_sentinel_without_changing_tool():
    panel = ToolPanel(TOOLS, CATEGORIES)

    result = panel.handle_click(panel.undo_button.rect.center)

    assert result == UNDO_CLICK_RESULT
    assert panel.active_tool_key == "line_dda"  # unchanged


def test_active_tool_label_returns_the_human_readable_label():
    panel = ToolPanel(TOOLS, CATEGORIES)
    assert panel.active_tool_label() == "Reta (DDA)"


def test_gradient_pos_to_color_left_edge_top_is_white():
    import pygame

    rect = pygame.Rect(0, 0, 100, 50)
    assert gradient_pos_to_color((0, 0), rect) == (255, 255, 255)


def test_gradient_pos_to_color_left_edge_bottom_is_fully_saturated_red():
    import pygame

    rect = pygame.Rect(0, 0, 100, 50)
    assert gradient_pos_to_color((0, 49), rect) == (255, 0, 0)


def test_gradient_pos_to_color_is_offset_by_the_rects_position():
    import pygame

    rect = pygame.Rect(20, 30, 100, 50)
    assert gradient_pos_to_color((20, 30), rect) == gradient_pos_to_color((0, 0), pygame.Rect(0, 0, 100, 50))
