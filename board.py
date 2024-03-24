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

    def possible_moves(self, ped: peds.Peds) -> List[Coordinates]:
        """
        Return a list of possible moves for the given ped.
        """
        # get the current location of the ped
        current_location = ped.get_location()

        # get the serial number of the ped
        serial_number = ped.get_serial_number()

        # get the x and y coordinates of the current location
        x, y = current_location

        # create a list to store the possible moves
        possible_moves = []

        # check if the ped is in the first row
        if x == 1:
            # check if the ped is in the first column
            if y == 0:
                # check if the ped is the first ped
                if serial_number == 0:
                    # add the possible moves
                    possible_moves.append((2, 0))
                    possible_moves.append((2, 1))
                else:
                    # add the possible moves
                    possible_moves.append((2, 0))
                    possible_moves.append((2, 1))
                    possible_moves.append((1, 1))
            # check if the ped is in the last column
            elif y == 9:
                # check if the ped is the last ped
                if serial_number == 9:
                    # add the possible moves
                    possible_moves.append((2, 8))
                    possible_moves.append((2, 9))
                else:
                    # add the possible moves
                    possible_moves.append((2, 8))
                    possible_moves.append((2, 9))
                    possible_moves.append((1, 8))
            # check if the ped is in the middle columns
            else:
                # add the possible moves
                possible_moves.append((2, y - 1))
                possible_moves.append((2, y))
                possible_moves.append((2, y + 1))
                possible_moves.append((1, y - 1))
                possible_moves.append((1, y))
                possible_moves.append((1, y + 1))

        # check if the ped is in the last row
        elif x == 6:
            # check if the ped is in the first column
            if y == 0:
                # check if the ped is the first ped
                if serial_number == 10:
                    # add the possible moves
                    possible_moves.append((5, 0))
                    possible_moves.append((5, 1))
                else:
                    # add the possible moves
                    possible_moves.append((5, 0))
                    possible_moves.append((5, 1))
                    possible_moves.append((6, 1))
            # check if the ped is in the last column
            elif y == 9:
                # check if the ped is the last ped
                if serial_number == 19:
                    # add the possible moves
                    possible_moves.append((5, 8))
                    possible_moves.append((5, 9))
                else:
                    # add the possible moves
                    possible_moves.append((5, 8))
                    possible_moves.append((5, 9))
                    possible_moves.append((6, 8))
            # check if the ped is in the middle columns
            else:
                # add the possible moves
                possible_moves.append((5, y - 1))
                possible_moves.append((5, y))
                possible_moves.append((5, y + 1))
                possible_moves.append((6, y - 1))
                possible_moves.append((6, y))
                possible_moves.append((6, y + 1))

        # check if the ped is in the middle rows
        else:
            # check if the ped is in the first column
            if y == 0:
                # add the possible moves
                possible_moves.append((x - 1, 0))
                possible_moves.append((x - 1, 1))
                possible_moves.append((x, 1))
                possible_moves.append((x + 1, 0))
                possible_moves.append((x + 1, 1))
            # check if the ped is in the last column
            elif y == 9:
                # add the possible moves
                possible_moves.append((x - 1, 8))
                possible_moves.append((x - 1, 9))
                possible_moves.append((x, 8))
                possible_moves.append((x + 1, 8))
                possible_moves.append((x + 1, 9))
            # check if the ped is in the middle columns
            else:
                # add the possible moves
                possible_moves.append((x - 1, y - 1))
                possible_moves.append((x - 1, y))
                possible_moves.append((x - 1, y + 1))
                possible_moves.append((x, y - 1))
                possible_moves.append((x, y + 1))
                possible_moves.append((x + 1, y - 1))
                possible_moves.append((x + 1, y))
                possible_moves.append((x + 1, y + 1))

        # create a list to store the valid moves
        valid_moves = []

        # iterate through the possible moves
        for move in possible_moves:
            # check if the move is valid
            if self.is_valid_move(ped, move):
                # add the move to the valid moves
                valid_moves.append(move)

        # return the valid moves
        return valid_moves

    def is_valid_move(self, ped: peds.Peds, new_location: Coordinates) -> bool:
        """
        Return True if the move is valid, False otherwise.
        """
        # get the current location of the ped
        current_location = ped.get_location()

        # get the x and y coordinates of the current location
        x, y = current_location

        # get the x and y coordinates of the new location
        new_x, new_y = new_location

        # get the serial number of the ped
        serial_number = ped.get_serial_number()

        # check if the new location is the same as the current location
        if new_location == current_location:
            return False

        # check if the new location is not on the board
        if new_x < 1 or new_x > 6 or new_y < 0 or new_y > 9:
            return False

        # check if the new location is occupied by another ped
        if self._board[new_location][0] != -1:
            return False

        # check if the new location is not a valid move
        if new_location not in self.possible_moves(ped):
            return False

        # check if the ped is in the first row
        if x == 1:
            # check if the ped is in the first column
            if y == 0:
                # check if the ped is the first ped
                if serial_number == 0:
                    # check if the new location is not a valid move
                    if new_location != (2, 0) and new_location != (2, 1):
                        return False
                else:
                    # check if the new location is not a valid move
                    if new_location != (2, 0) and new_location != (2, 1) and new_location != (1, 1):
                        return False
            # check if the ped is in the last column
            elif y == 9:
                # check if the ped is the last ped
                if serial_number == 9:
                    # check if the new location is not a valid move
                    if new_location != (2, 8) and new_location != (2, 9):
                        return False
                else:
                    # check if the new location is not a valid move
                    if new_location != (2, 8) and new_location:
                        return False
            # check if the ped is in the middle columns
            else:
                # check if the new location is not a valid move
                if new_location != (2, y - 1) and new_location != (2, y) and new_location != (2, y + 1) and new_location != (1, y - 1) and new_location != (1, y) and new_location != (1, y + 1):
                    return False
        # check if the ped is in the last row
        elif x == 6:
            # check if the ped is in the first column
            if y == 0:
                # check if the ped is the first ped
                if serial_number == 10:
                    # check if the new location is not a valid move
                    if new_location != (5, 0) and new_location != (5, 1):
                        return False
                else:
                    # check if the new location is not a valid move
                    if new_location != (5, 0) and new_location != (5, 1) and new_location != (6, 1):
                        return False
            # check if the ped is in the last column
            elif y == 9:
                # check if the ped is the last ped
                if serial_number == 19:
                    # check if the new location is not a valid move
                    if new_location != (5, 8) and new_location != (5, 9):
                        return False
                else:
                    # check if the new location is not a valid move
                    if new_location != (5, 8) and new_location != (5, 9) and new_location != (6, 8):
                        return False
            # check if the ped is in the middle columns
            else:
                # check if the new location is not a valid move
                if new_location != (5, y - 1) and new_location != (5, y) and new_location != (5, y + 1) and new_location != (6, y - 1) and new_location != (6, y) and new_location != (6, y + 1):
                    return False
        # check if the ped is in the middle rows
        else:
            # check if the ped is in the first column
            if y == 0:
                # check if the new location is not a valid move
                if new_location != (x - 1, 0) and new_location != (x - 1, 1) and new_location != (x, 1) and new_location != (x + 1, 0) and new_location != (x + 1, 1):
                    return False
            # check if the ped is in the last column
            elif y == 9:
                # check if the new location is not a valid move
                if new_location != (x - 1, 8) and new_location != (x - 1, 9) and new_location != (x, 8) and new_location != (x + 1, 8) and new_location != (x + 1, 9):
                    return False
            # check if the ped is in the middle columns
            else:
                # check if the new location is not a valid move
                if new_location != (x - 1, y - 1) and new_location != (x - 1, y) and new_location != (x - 1, y + 1) and new_location != (x, y - 1) and new_location != (x, y + 1) and new_location != (x + 1, y - 1) and new_location != (x + 1, y) and new_location != (x + 1, y + 1):
                    return False

        # return True if the new location is a valid move
        return True

    def move_ped(self, ped: peds.Peds, new_location: Coordinates) -> None:

        if ped not in self._peds:
            raise Exception("This ped does not exist")

        # else
        # remove the ped from the old location
        self._board[ped.get_location()] = (-1, '_')

        # place the ped in the new location and update the ped's location
        self._board[new_location] = (ped.get_serial_number(), ped.get_color())
        ped.set_location(new_location)
