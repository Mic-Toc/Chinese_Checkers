from typing import Tuple, List, Dict

Coordinates = Tuple[int, int]


class Board:

    def __init__(self) -> None:

        board = dict()

        # creating a dictionary whose keys are coordinates
        # and values are car names or '_'
        for i in range(1, 7):

            for j in range(10):

                coordinate: Coordinates = (i, j)

                board[coordinate] = '_'

        for k in range(61):

            coordinate: Coordinates = (0, k)

            board[coordinate] = '_'






