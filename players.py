from typing import List

from ped import Ped


class Human:
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

    @staticmethod
    def is_bot() -> bool:
        return False


class Bot:
    """A class to represent a bot (not real) player in the game."""

    def __init__(self, peds_color: str) -> None:
        self._peds_color = peds_color
        self._peds: List[Ped] = []

    def get_color(self) -> str:
        return self._peds_color

    def get_peds(self) -> list:
        return self._peds

    def add_ped(self, ped: Ped) -> None:
        self._peds.append(ped)

    @staticmethod
    def is_bot() -> bool:
        return True
