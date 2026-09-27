import copy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .constants import FILL_COLOR

Vertex = Tuple[float, float]
Rect = Tuple[float, float, float, float]  # xmin, ymin, xmax, ymax
Color = Tuple[int, int, int]

MAX_UNDO_HISTORY = 20


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Line:
    start: Vertex
    end: Vertex
    algorithm: str = "bresenham"  # "dda" or "bresenham"


@dataclass
class Polygon:
    vertices: List[Vertex]


@dataclass
class Circle:
    center: Vertex
    radius: float


def _bbox(vertices: List[Vertex]) -> Rect:
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    return min(xs), min(ys), max(xs), max(ys)


def _bbox_overlaps_rect(bbox: Rect, rect: Rect) -> bool:
    bxmin, bymin, bxmax, bymax = bbox
    rxmin, rymin, rxmax, rymax = rect
    return bxmin <= rxmax and bxmax >= rxmin and bymin <= rymax and bymax >= rymin


@dataclass
class Scene:
    points: List[Point] = field(default_factory=list)
    lines: List[Line] = field(default_factory=list)
    polygons: List[Polygon] = field(default_factory=list)
    circles: List[Circle] = field(default_factory=list)
    selected_points: List[Point] = field(default_factory=list)
    selected_lines: List[Line] = field(default_factory=list)
    selected_polygons: List[Polygon] = field(default_factory=list)
    clip_window: Optional[Rect] = None
    fills: List[dict] = field(default_factory=list)
    fill_color: Color = FILL_COLOR
    preview_rect: Optional[Rect] = None
    in_progress_polygon_vertices: List[Vertex] = field(default_factory=list)
    _undo_history: List[dict] = field(default_factory=list, repr=False)

    def save_undo_snapshot(self) -> None:
        """Records the current committed state so a later undo() can restore
        it. Call this right before a discrete action (creating a shape,
        transforming a selection, clipping, filling) commits its change."""
        snapshot = {
            "points": copy.deepcopy(self.points),
            "lines": copy.deepcopy(self.lines),
            "polygons": copy.deepcopy(self.polygons),
            "circles": copy.deepcopy(self.circles),
            "clip_window": self.clip_window,
             "fills": [
                {key: value for key, value in request.items() if key != "surface"}
                for request in self.fills
            ],
        }
        self._undo_history.append(snapshot)
        if len(self._undo_history) > MAX_UNDO_HISTORY:
            self._undo_history.pop(0)

    def undo(self) -> None:
        """Restores the state recorded by the most recent save_undo_snapshot().
        A no-op when there is no history left. Clears the current selection,
        since it may reference objects that no longer exist after restoring."""
        if not self._undo_history:
            return
        snapshot = self._undo_history.pop()
        self.points = snapshot["points"]
        self.lines = snapshot["lines"]
        self.polygons = snapshot["polygons"]
        self.circles = snapshot["circles"]
        self.clip_window = snapshot["clip_window"]
        self.fills = snapshot["fills"]
        self.clear_selection()
        self.in_progress_polygon_vertices = []

    def select_in_rect(self, rect: Rect) -> None:
        self.selected_points = [
            p for p in self.points
            if rect[0] <= p.x <= rect[2] and rect[1] <= p.y <= rect[3]
        ]
        self.selected_lines = [
            line for line in self.lines
            if _bbox_overlaps_rect(_bbox([line.start, line.end]), rect)
        ]
        self.selected_polygons = [
            polygon for polygon in self.polygons
            if _bbox_overlaps_rect(_bbox(polygon.vertices), rect)
        ]

    def clear_selection(self) -> None:
        self.selected_points = []
        self.selected_lines = []
        self.selected_polygons = []
