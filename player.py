from typing import List

from ped import Ped


class Player:
    """A class to represent a player in the game."""

    def __init__(self, peds_color: str) -> None:
        self._peds_color = peds_color
        self._peds: List[Ped] = []

    def get_color(self) -> str:
        return self._peds_color

    def get_peds(self) -> list:
        return self._peds

    def add_ped(self, ped: Ped) -> None:
        self._peds.append(ped)
