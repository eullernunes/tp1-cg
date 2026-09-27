import pygame

from .constants import BACKGROUND_COLOR


class Framebuffer:
    def __init__(self, width, height, background=BACKGROUND_COLOR):
        self.width = width
        self.height = height
        self.background = background
        self._surface = pygame.Surface((width, height))
        self.clear()

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self._surface.set_at((x, y), color)

    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return tuple(self._surface.get_at((x, y)))[:3]
        return None

    def clear(self):
        self._surface.fill(self.background)

    def to_surface(self):
        return self._surface
