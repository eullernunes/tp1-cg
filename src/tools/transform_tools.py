import math

from .. import transforms
from ._geometry import normalize_rect
from .base import Tool


def _selection_centroid(scene):
    xs, ys = [], []
    for line in scene.selected_lines:
        xs += [line.start[0], line.end[0]]
        ys += [line.start[1], line.end[1]]
    for polygon in scene.selected_polygons:
        xs += [v[0] for v in polygon.vertices]
        ys += [v[1] for v in polygon.vertices]
    for point in scene.selected_points:
        xs.append(point.x)
        ys.append(point.y)
    if not xs:
        return None
    return (sum(xs) / len(xs), sum(ys) / len(ys))


def _has_selection(scene):
    return bool(scene.selected_lines or scene.selected_polygons or scene.selected_points)


def _apply_to_selection(scene, transform_fn):
    for line in scene.selected_lines:
        line.start, line.end = transform_fn([line.start, line.end])
    for polygon in scene.selected_polygons:
        polygon.vertices = transform_fn(polygon.vertices)
    for point in scene.selected_points:
        (point.x, point.y), = transform_fn([(point.x, point.y)])


class SelectTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._anchor = None
        self.current_rect = None

    def on_mouse_down(self, pos):
        self._anchor = pos
        self.current_rect = None
        self.scene.preview_rect = None

    def on_mouse_drag(self, pos):
        if self._anchor is not None:
            self.current_rect = normalize_rect(self._anchor, pos)
            self.scene.preview_rect = self.current_rect

    def on_mouse_up(self, pos):
        if self._anchor is None:
            return
        rect = normalize_rect(self._anchor, pos)
        self._anchor = None
        self.current_rect = None
        self.scene.preview_rect = None
        xmin, ymin, xmax, ymax = rect
        if xmax - xmin <= 0 or ymax - ymin <= 0:
            return
        self.scene.select_in_rect(rect)


class TranslateTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._last = None

    def on_mouse_down(self, pos):
        self._last = pos
        if _has_selection(self.scene):
            self.scene.save_undo_snapshot()

    def on_mouse_drag(self, pos):
        if self._last is None:
            return
        dx = pos[0] - self._last[0]
        dy = pos[1] - self._last[1]
        _apply_to_selection(self.scene, lambda verts: transforms.translate(verts, dx, dy))
        self._last = pos

    def on_mouse_up(self, pos):
        self._last = None


class RotateTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._pivot = None
        self._last_angle = None

    def on_mouse_down(self, pos):
        self._pivot = _selection_centroid(self.scene)
        if self._pivot is not None:
            self.scene.save_undo_snapshot()
            self._last_angle = self._angle_to(pos)

    def on_mouse_drag(self, pos):
        if self._pivot is None:
            return
        angle = self._angle_to(pos)
        delta = angle - self._last_angle
        _apply_to_selection(self.scene, lambda verts: transforms.rotate(verts, delta, self._pivot))
        self._last_angle = angle

    def on_mouse_up(self, pos):
        self._pivot = None
        self._last_angle = None

    def _angle_to(self, pos):
        return math.degrees(math.atan2(pos[1] - self._pivot[1], pos[0] - self._pivot[0]))


class ScaleTool(Tool):
    def __init__(self, scene):
        super().__init__(scene)
        self._pivot = None
        self._last_dist = None

    def on_mouse_down(self, pos):
        self._pivot = _selection_centroid(self.scene)
        if self._pivot is not None:
            self.scene.save_undo_snapshot()
            self._last_dist = self._distance_to(pos) or 1e-6

    def on_mouse_drag(self, pos):
        if self._pivot is None:
            return
        dist = self._distance_to(pos) or 1e-6
        factor = dist / self._last_dist
        _apply_to_selection(self.scene, lambda verts: transforms.scale(verts, factor, factor, self._pivot))
        self._last_dist = dist

    def on_mouse_up(self, pos):
        self._pivot = None
        self._last_dist = None

    def _distance_to(self, pos):
        return math.hypot(pos[0] - self._pivot[0], pos[1] - self._pivot[1])


class _ReflectTool(Tool):
    axis = None

    def on_mouse_down(self, pos):
        pivot = _selection_centroid(self.scene)
        if pivot is None:
            return
        self.scene.save_undo_snapshot()
        _apply_to_selection(self.scene, lambda verts: transforms.reflect(verts, self.axis, pivot))


class ReflectXTool(_ReflectTool):
    axis = "x"


class ReflectYTool(_ReflectTool):
    axis = "y"


class ReflectXYTool(_ReflectTool):
    axis = "xy"
