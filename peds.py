from typing import Tuple, List, Dict
import pygame

Coordinates = Tuple[int, int]


class Peds:

    def __init__(self, color: str, location: Coordinates,
                 serial_number: int) -> None:

        self._color = color
        self._location = location
        self._serial_number = serial_number

    def get_color(self):
        return self._color

    def get_location(self):
        return self._location

    def get_serial_number(self):
        return self._serial_number

    def set_location(self, location: Coordinates) -> None:
        self._location = location

    def same_color(self, other: 'Peds') -> bool:
        return self._color == other.get_color()








