import colorsys

import pygame

BUTTON_HEIGHT = 32
BUTTON_MARGIN = 4
CATEGORY_BUTTON_HEIGHT = 30
CATEGORY_COLUMNS = 2
CATEGORY_FONT_SIZE = 15
COLOR_SWATCH_HEIGHT = 90
UNDO_BUTTON_HEIGHT = 32
PANEL_WIDTH = 220
PANEL_BG_COLOR = (230, 230, 230)
BUTTON_IDLE_COLOR = (255, 255, 255)
BUTTON_ACTIVE_COLOR = (180, 180, 250)
BUTTON_BORDER_COLOR = (0, 0, 0)
BUTTON_TEXT_COLOR = (0, 0, 0)
CATEGORY_IDLE_COLOR = (200, 200, 200)
CATEGORY_ACTIVE_COLOR = (130, 130, 220)
UNDO_BUTTON_COLOR = (240, 200, 140)
STATUS_TEXT_COLOR = (60, 60, 60)

FILL_CATEGORY_NAME = "Preencher"
UNDO_CLICK_RESULT = "undo"


def gradient_pos_to_color(pos, rect):
    """Maps a click inside a color-gradient rect to an RGB color.

    Hue varies left-to-right (0 to 360 degrees); saturation varies
    top-to-bottom (0 at the top = white, 1 at the bottom = fully
    saturated); value (brightness) is fixed at 1.0.
    """
    x = min(max(pos[0] - rect.x, 0), rect.width - 1)
    y = min(max(pos[1] - rect.y, 0), rect.height - 1)
    hue = x / max(rect.width - 1, 1)
    saturation = y / max(rect.height - 1, 1)
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, 1.0)
    return (round(r * 255), round(g * 255), round(b * 255))


def _build_gradient_surface(width, height):
    surface = pygame.Surface((width, height))
    for px in range(width):
        hue = px / max(width - 1, 1)
        for py in range(height):
            saturation = py / max(height - 1, 1)
            r, g, b = colorsys.hsv_to_rgb(hue, saturation, 1.0)
            surface.set_at((px, py), (round(r * 255), round(g * 255), round(b * 255)))
    return surface


class Button:
    def __init__(self, label, tool_key, rect):
        self.label = label
        self.tool_key = tool_key
        self.rect = rect

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class CategoryButton:
    def __init__(self, label, rect):
        self.label = label
        self.rect = rect

    def contains(self, pos):
        return self.rect.collidepoint(pos)


class ToolPanel:
    def __init__(self, tool_definitions, categories, x=0, y=0):
        self._x = x
        self._y = y
        label_by_key = {key: label for label, key in tool_definitions}
        self._label_by_key = label_by_key
        self.categories = [
            (name, [(label_by_key[key], key) for key in keys])
            for name, keys in categories
        ]

        self.undo_button = CategoryButton(
            "Desfazer",
            pygame.Rect(x + BUTTON_MARGIN, y + BUTTON_MARGIN, PANEL_WIDTH - 2 * BUTTON_MARGIN, UNDO_BUTTON_HEIGHT),
        )
        category_top = y + BUTTON_MARGIN + UNDO_BUTTON_HEIGHT + BUTTON_MARGIN

        columns = min(CATEGORY_COLUMNS, len(self.categories))
        rows = -(-len(self.categories) // columns)  # ceiling division
        category_width = (PANEL_WIDTH - (columns + 1) * BUTTON_MARGIN) // columns
        self._category_rows = rows
        self._category_top = category_top
        self.category_buttons = []
        for i, (name, _) in enumerate(self.categories):
            col, row = i % columns, i // columns
            rect = pygame.Rect(
                x + BUTTON_MARGIN + col * (category_width + BUTTON_MARGIN),
                category_top + row * (CATEGORY_BUTTON_HEIGHT + BUTTON_MARGIN),
                category_width,
                CATEGORY_BUTTON_HEIGHT,
            )
            self.category_buttons.append(CategoryButton(name, rect))

        self._category_font = pygame.font.SysFont(None, CATEGORY_FONT_SIZE)
        self.active_category_index = 0
        first_category_tools = self.categories[0][1]
        self.active_tool_key = first_category_tools[0][1] if first_category_tools else None

        self.buttons = []
        self.color_swatch_rect = None
        self._gradient_surface = None
        self._rebuild_tool_buttons()

    def _rebuild_tool_buttons(self):
        category_grid_height = self._category_rows * (CATEGORY_BUTTON_HEIGHT + BUTTON_MARGIN)
        top = self._category_top + category_grid_height
        _, tool_list = self.categories[self.active_category_index]

        self.buttons = []
        for i, (label, tool_key) in enumerate(tool_list):
            rect = pygame.Rect(
                self._x + BUTTON_MARGIN,
                top + i * (BUTTON_HEIGHT + BUTTON_MARGIN),
                PANEL_WIDTH - 2 * BUTTON_MARGIN,
                BUTTON_HEIGHT,
            )
            self.buttons.append(Button(label, tool_key, rect))

        category_name, _ = self.categories[self.active_category_index]
        if category_name == FILL_CATEGORY_NAME:
            swatch_top = top + len(tool_list) * (BUTTON_HEIGHT + BUTTON_MARGIN) + BUTTON_MARGIN
            swatch_width = PANEL_WIDTH - 2 * BUTTON_MARGIN
            self.color_swatch_rect = pygame.Rect(
                self._x + BUTTON_MARGIN, swatch_top, swatch_width, COLOR_SWATCH_HEIGHT,
            )
            self._gradient_surface = _build_gradient_surface(swatch_width, COLOR_SWATCH_HEIGHT)
        else:
            self.color_swatch_rect = None
            self._gradient_surface = None

    def contains(self, pos):
        return pos[0] < PANEL_WIDTH

    def handle_click(self, pos):
        if self.undo_button.contains(pos):
            return UNDO_CLICK_RESULT
        for i, cat_button in enumerate(self.category_buttons):
            if cat_button.contains(pos):
                self.active_category_index = i
                self._rebuild_tool_buttons()
                return None
        for button in self.buttons:
            if button.contains(pos):
                self.active_tool_key = button.tool_key
                return button.tool_key
        return None

    def active_tool_label(self):
        return self._label_by_key.get(self.active_tool_key, "")

    def draw(self, surface, font):
        pygame.draw.rect(surface, PANEL_BG_COLOR, (self._x, self._y, PANEL_WIDTH, surface.get_height()))

        pygame.draw.rect(surface, UNDO_BUTTON_COLOR, self.undo_button.rect)
        pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.undo_button.rect, 1)
        undo_text = font.render(self.undo_button.label, True, BUTTON_TEXT_COLOR)
        surface.blit(undo_text, undo_text.get_rect(center=self.undo_button.rect.center))

        for i, cat_button in enumerate(self.category_buttons):
            color = CATEGORY_ACTIVE_COLOR if i == self.active_category_index else CATEGORY_IDLE_COLOR
            pygame.draw.rect(surface, color, cat_button.rect)
            pygame.draw.rect(surface, BUTTON_BORDER_COLOR, cat_button.rect, 1)
            text_surface = self._category_font.render(cat_button.label, True, BUTTON_TEXT_COLOR)
            text_rect = text_surface.get_rect(center=cat_button.rect.center)
            surface.blit(text_surface, text_rect)

        for button in self.buttons:
            color = BUTTON_ACTIVE_COLOR if button.tool_key == self.active_tool_key else BUTTON_IDLE_COLOR
            pygame.draw.rect(surface, color, button.rect)
            pygame.draw.rect(surface, BUTTON_BORDER_COLOR, button.rect, 1)
            text_surface = font.render(button.label, True, BUTTON_TEXT_COLOR)
            surface.blit(text_surface, (button.rect.x + 6, button.rect.y + 6))

        if self.color_swatch_rect is not None:
            surface.blit(self._gradient_surface, self.color_swatch_rect.topleft)
            pygame.draw.rect(surface, BUTTON_BORDER_COLOR, self.color_swatch_rect, 1)

        status_y = surface.get_height() - 26
        status_text = f"Ferramenta atual: {self.active_tool_label()}"
        status_surface = font.render(status_text, True, STATUS_TEXT_COLOR)
        surface.blit(status_surface, (self._x + BUTTON_MARGIN, status_y))
