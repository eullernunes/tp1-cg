import pygame

from . import rasterization
from .constants import PREVIEW_RECT_COLOR, STROKE_COLOR
from .fill import boundary_fill, flood_fill
from .framebuffer import Framebuffer
from .models import Scene
from .tools.clip_tools import ClipCohenSutherlandTool, ClipLiangBarskyTool
from .tools.drawing_tools import CircleTool, LineBresenhamTool, LineDdaTool, PointTool, PolygonTool
from .tools.fill_tools import (
    BoundaryFillTool4,
    BoundaryFillTool8,
    FloodFillTool4,
    FloodFillTool8,
)
from .tools.transform_tools import (
    ReflectXTool,
    ReflectXYTool,
    ReflectYTool,
    RotateTool,
    ScaleTool,
    SelectTool,
    TranslateTool,
)
from .ui import PANEL_WIDTH, UNDO_CLICK_RESULT, ToolPanel, gradient_pos_to_color

CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600

TOOL_DEFINITIONS = [
    ("Ponto", "point"),
    ("Reta (DDA)", "line_dda"),
    ("Reta (Bresenham)", "line_bresenham"),
    ("Circulo (Bresenham)", "circle"),
    ("Poligono", "polygon"),
    ("Fechar poligono", "polygon_close"),
    ("Selecionar", "select"),
    ("Transladar", "translate"),
    ("Rotacionar", "rotate"),
    ("Escalar", "scale"),
    ("Refletir X", "reflect_x"),
    ("Refletir Y", "reflect_y"),
    ("Refletir XY", "reflect_xy"),
    ("Recortar (Cohen-Sutherland)", "clip_cs"),
    ("Recortar (Liang-Barsky)", "clip_lb"),
    ("Boundary-Fill (4)", "boundary_fill_4"),
    ("Boundary-Fill (8)", "boundary_fill_8"),
    ("Flood-Fill (4)", "flood_fill_4"),
    ("Flood-Fill (8)", "flood_fill_8"),
]

TOOL_CATEGORIES = [
    ("Desenhar", ["point", "line_dda", "line_bresenham", "circle", "polygon", "polygon_close"]),
    ("Transformar", ["select", "translate", "rotate", "scale", "reflect_x", "reflect_y", "reflect_xy"]),
    ("Recortar", ["clip_cs", "clip_lb"]),
    ("Preencher", ["boundary_fill_4", "boundary_fill_8", "flood_fill_4", "flood_fill_8"]),
]


def build_tools(scene):
    return {
        "point": PointTool(scene),
        "line_dda": LineDdaTool(scene),
        "line_bresenham": LineBresenhamTool(scene),
        "circle": CircleTool(scene),
        "polygon": PolygonTool(scene),
        "select": SelectTool(scene),
        "translate": TranslateTool(scene),
        "rotate": RotateTool(scene),
        "scale": ScaleTool(scene),
        "reflect_x": ReflectXTool(scene),
        "reflect_y": ReflectYTool(scene),
        "reflect_xy": ReflectXYTool(scene),
        "clip_cs": ClipCohenSutherlandTool(scene),
        "clip_lb": ClipLiangBarskyTool(scene),
        "boundary_fill_4": BoundaryFillTool4(scene),
        "boundary_fill_8": BoundaryFillTool8(scene),
        "flood_fill_4": FloodFillTool4(scene),
        "flood_fill_8": FloodFillTool8(scene),
    }


def to_canvas_pos(pos):
    return (pos[0] - PANEL_WIDTH, pos[1])


def handle_event(scene, panel, tools, active_tool_key, event):
    """Routes one Pygame event; kept separate from run()'s blocking loop so
    it can be unit tested with synthetic events, without opening a window."""
    if event.type == pygame.MOUSEBUTTONDOWN:
        if panel.contains(event.pos):
            if panel.color_swatch_rect is not None and panel.color_swatch_rect.collidepoint(event.pos):
                scene.fill_color = gradient_pos_to_color(event.pos, panel.color_swatch_rect)
            else:
                clicked = panel.handle_click(event.pos)
                if clicked == "polygon_close":
                    tools["polygon"].close()
                    panel.active_tool_key = active_tool_key
                elif clicked == UNDO_CLICK_RESULT:
                    scene.undo()
                    panel.active_tool_key = active_tool_key
                elif clicked is not None:
                    active_tool_key = clicked
        else:
            tools[active_tool_key].on_mouse_down(to_canvas_pos(event.pos))
    elif event.type == pygame.MOUSEMOTION:
        if event.buttons[0] and not panel.contains(event.pos):
            tools[active_tool_key].on_mouse_drag(to_canvas_pos(event.pos))
    elif event.type == pygame.MOUSEBUTTONUP:
        if not panel.contains(event.pos):
            tools[active_tool_key].on_mouse_up(to_canvas_pos(event.pos))
    return active_tool_key


class _FillRecorder:
    """Wraps a Framebuffer so a fill algorithm's writes are applied to it and
    also recorded, so a fill only needs to run its flood-fill/boundary-fill
    algorithm once; every later frame just replays the recorded pixels."""

    def __init__(self, fb):
        self._fb = fb
        self.pixels = {}

    def get_pixel(self, x, y):
        return self._fb.get_pixel(x, y)

    def set_pixel(self, x, y, color):
        self._fb.set_pixel(x, y, color)
        self.pixels[(x, y)] = color


def _build_fill_surface(width, height, pixels):
    """Bakes a recorded fill into its own transparent surface, once, so every
    later frame can replay it with a single native blit instead of writing
    each pixel through Python again."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))
    for (x, y), color in pixels.items():
        surface.set_at((x, y), (*color, 255))
    return surface


def _draw_rect_outline(fb, rect, color):
    xmin, ymin, xmax, ymax = rect
    corners = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
    for i in range(4):
        rasterization.line_bresenham(fb, corners[i], corners[(i + 1) % 4], color)


def render(scene, fb):
    fb.clear()
    for circle in scene.circles:
        rasterization.circle_bresenham(fb, circle.center, circle.radius, STROKE_COLOR)
    for line in scene.lines:
        if line.algorithm == "dda":
            rasterization.line_dda(fb, line.start, line.end, STROKE_COLOR)
        else:
            rasterization.line_bresenham(fb, line.start, line.end, STROKE_COLOR)
    for polygon in scene.polygons:
        verts = polygon.vertices
        for i in range(len(verts)):
            rasterization.line_bresenham(fb, verts[i], verts[(i + 1) % len(verts)], STROKE_COLOR)
    for point in scene.points:
        fb.set_pixel(round(point.x), round(point.y), STROKE_COLOR)
    in_progress = scene.in_progress_polygon_vertices
    for i in range(len(in_progress) - 1):
        rasterization.line_bresenham(fb, in_progress[i], in_progress[i + 1], STROKE_COLOR)
    for vertex in in_progress:
        rasterization.circle_bresenham(fb, vertex, 3, STROKE_COLOR)
    for request in scene.fills:
        if "surface" not in request:
            recorder = _FillRecorder(fb)
            if request["algorithm"] == "boundary":
                boundary_fill(
                    recorder, request["seed"], request["border_color"],
                    request["fill_color"], request["connectivity"],
                )
            else:
                target_color = fb.get_pixel(*request["seed"])
                if target_color is None:
                    continue
                flood_fill(
                    recorder, request["seed"], target_color,
                    request["fill_color"], request["connectivity"],
                )
            request["surface"] = _build_fill_surface(fb.width, fb.height, recorder.pixels)
        # Already computed (this frame or an earlier one): a single native
        # blit replays it, instead of writing each pixel through Python again.
        fb.to_surface().blit(request["surface"], (0, 0))
    if scene.preview_rect is not None:
        _draw_rect_outline(fb, scene.preview_rect, PREVIEW_RECT_COLOR)


def run():
    pygame.init()
    screen = pygame.display.set_mode((PANEL_WIDTH + CANVAS_WIDTH, CANVAS_HEIGHT))
    pygame.display.set_caption("TP1 Algoritmos CG")
    font = pygame.font.SysFont(None, 20)
    clock = pygame.time.Clock()

    scene = Scene()
    fb = Framebuffer(CANVAS_WIDTH, CANVAS_HEIGHT)
    panel = ToolPanel(TOOL_DEFINITIONS, TOOL_CATEGORIES)
    tools = build_tools(scene)
    active_tool_key = panel.active_tool_key

    canvas_rect = pygame.Rect(PANEL_WIDTH, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                active_tool_key = handle_event(scene, panel, tools, active_tool_key, event)

        render(scene, fb)
        screen.blit(fb.to_surface(), (PANEL_WIDTH, 0))
        pygame.draw.rect(screen, (80, 80, 80), canvas_rect, 2)
        label_surface = font.render("Area de Desenho", True, (80, 80, 80))
        screen.blit(label_surface, (canvas_rect.x + 8, canvas_rect.y + 6))
        panel.draw(screen, font)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    run()
