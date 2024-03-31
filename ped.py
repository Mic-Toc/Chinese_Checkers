from typing import Tuple

Coordinates = Tuple[float, float]


class Ped:

    def __init__(self, color: str, location: Coordinates) -> None:

        self._color = color
        self._location = location

    def get_color(self):
        return self._color

    def get_location(self):
        return self._location

    def set_location(self, location: Coordinates) -> None:
        self._location = location

    def same_color(self, other: 'Ped') -> bool:
        return self._color == other.get_color()








