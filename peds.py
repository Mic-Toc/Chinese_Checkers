from typing import Tuple, List, Dict
import pygame

class Peds:

    def __init__(self, color: str, x: float, y: float, radius: float) -> None:

        self._color = color
        self._location = tuple((x, y))
        self._radius = radius

    def get_color(self):
        return self._color

    def get_location(self):
        return self._location

    def set_location(self, x: float, y: float) -> None:
        self._location = tuple((x, y))

    def same_color(self, other: 'Peds') -> bool:
        return self._color == other.get_color()

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, self._color, self._location, self._radius)









