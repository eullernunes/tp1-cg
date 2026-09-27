from ..constants import STROKE_COLOR
from .base import Tool


class _BoundaryFillTool(Tool):
    connectivity = 4

    def on_mouse_down(self, pos):
        self.scene.save_undo_snapshot()
        self.scene.fills.append({
            "algorithm": "boundary",
            "seed": (round(pos[0]), round(pos[1])),
            "border_color": STROKE_COLOR,
            "fill_color": self.scene.fill_color,
            "connectivity": self.connectivity,
        })


class BoundaryFillTool4(_BoundaryFillTool):
    connectivity = 4


class BoundaryFillTool8(_BoundaryFillTool):
    connectivity = 8


class _FloodFillTool(Tool):
    connectivity = 4

    def on_mouse_down(self, pos):
        self.scene.save_undo_snapshot()
        self.scene.fills.append({
            "algorithm": "flood",
            "seed": (round(pos[0]), round(pos[1])),
            "fill_color": self.scene.fill_color,
            "connectivity": self.connectivity,
        })


class FloodFillTool4(_FloodFillTool):
    connectivity = 4


class FloodFillTool8(_FloodFillTool):
    connectivity = 8
