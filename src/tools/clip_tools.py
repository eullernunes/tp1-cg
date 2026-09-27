from .. import clipping
from ._geometry import normalize_rect
from .base import Tool


class _ClipTool(Tool):
    clip_fn = None

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

        self.scene.save_undo_snapshot()
        self.scene.clip_window = rect
        # Track which original lines were selected by identity
        selected_ids = {id(line) for line in self.scene.selected_lines}
        new_lines = []
        new_selected = []
        for line in self.scene.lines:
            result = type(self).clip_fn(line, rect)
            if result is not None:
                new_lines.append(result)
                # If the original line was selected, add the new clipped result to selections
                if id(line) in selected_ids:
                    new_selected.append(result)
        self.scene.lines = new_lines
        self.scene.selected_lines = new_selected


class ClipCohenSutherlandTool(_ClipTool):
    clip_fn = staticmethod(clipping.cohen_sutherland)


class ClipLiangBarskyTool(_ClipTool):
    clip_fn = staticmethod(clipping.liang_barsky)
