import math

from ..models import Circle, Line, Point, Polygon
from .base import Tool

CLOSE_THRESHOLD_PX = 8


class PointTool(Tool):
    def on_mouse_down(self, pos):
        self.scene.save_undo_snapshot()
        self.scene.points.append(Point(pos[0], pos[1]))


class LineDdaTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._start = None

    def on_mouse_down(self, pos):
        self._start = pos

    def on_mouse_up(self, pos):
        if self._start is not None and self._start != pos:
            self.scene.save_undo_snapshot()
            self.scene.lines.append(Line(self._start, pos, algorithm="dda"))
        self._start = None


class LineBresenhamTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._start = None

    def on_mouse_down(self, pos):
        self._start = pos

    def on_mouse_up(self, pos):
        if self._start is not None and self._start != pos:
            self.scene.save_undo_snapshot()
            self.scene.lines.append(Line(self._start, pos, algorithm="bresenham"))
        self._start = None


class CircleTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._center = None

    def on_mouse_down(self, pos):
        self._center = pos

    def on_mouse_up(self, pos):
        if self._center is None:
            return
        radius = math.hypot(pos[0] - self._center[0], pos[1] - self._center[1])
        if radius > 0:
            self.scene.save_undo_snapshot()
            self.scene.circles.append(Circle(self._center, radius))
        self._center = None


class PolygonTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._vertices = []

    def on_mouse_down(self, pos):
        if self._vertices:
            first = self._vertices[0]
            if math.hypot(pos[0] - first[0], pos[1] - first[1]) <= CLOSE_THRESHOLD_PX:
                self.close()
                return
        self._vertices.append(pos)
        self.scene.in_progress_polygon_vertices = list(self._vertices)

    def close(self):
        if len(self._vertices) >= 3:
            self.scene.save_undo_snapshot()
            self.scene.polygons.append(Polygon(list(self._vertices)))
        self._vertices = []
        self.scene.in_progress_polygon_vertices = []
