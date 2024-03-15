from typing import Tuple, List, Dict

Coordinates = Tuple[int, int]


class Peds:

    def __init__(self, color: str, number: int, location: Coordinates) -> None:

        self.__color = color
        self.__number = number
        self.__location = location

    def get_color(self):
        return self.__color

    def get_number(self):
        return self.__number

    def get_location(self):
        return self.__location











