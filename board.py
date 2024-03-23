from typing import Tuple, List, Dict
import pygame
import peds

Coordinates = Tuple[int, int]


Y_COORD = 0
X_COORD = 1


class Board:

    def __init__(self) -> None:

        board: Dict[Coordinates, Tuple[int, str]] = dict()

        # creating a dictionary whose keys are coordinates
        # and values are car names or '_'
        for i in range(1, 7):

            for j in range(10):

                coordinate: Coordinates = (i, j)

                board[coordinate] = (-1, '_')

        for k in range(61):

            coordinate = (0, k)

            board[coordinate] = (-1, '_')

        self._board = board
        self._peds: List[peds.Peds] = []

    def place_ped(self, ped: peds.Peds) -> None:

        if ped in self._peds:
            raise Exception("This ped already exists")

        # else
        self._board[ped.get_location()] = (ped.get_serial_number(),
                                           ped.get_color())
        self._peds.append(ped)

    def move_ped(self, ped: peds.Peds, new_location: Coordinates) -> None:

        if ped not in self._peds:
            raise Exception("This ped does not exist")

        # else
        # remove the ped from the old location
        self._board[ped.get_location()] = (-1, '_')

        # place the ped in the new location and update the ped's location
        self._board[new_location] = (ped.get_serial_number(), ped.get_color())
        ped.set_location(new_location)
