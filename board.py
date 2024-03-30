from typing import Tuple, List, Dict, Union, Set
import pygame
from peds import Peds
from pygame_switch import InitGui

Coordinates = Tuple[int, int]

# Constants from the GUI
FRAME_HEIGHT = 590
FRAME_WIDTH = 930
BOARD_HEIGHT = 0.95 * FRAME_HEIGHT
BOARD_WIDTH = 0.6 * FRAME_WIDTH

X_COORD = 0
Y_COORD = 1


class Board:

    def __init__(self) -> None:

        board: Dict[Coordinates, Union[Peds, None]] = dict()

        # # creating a dictionary whose keys are coordinates
        # # and values are peds or None, depending on if
        # # the place is empty
        # for i in range(1, 7):
        #
        #     for j in range(10):
        #
        #         coordinate: Coordinates = (i, j)
        #
        #         board[coordinate] = None
        #
        # for k in range(61):
        #
        #     coordinate = (0, k)
        #
        #     board[coordinate] = None

        self._board = board

        self._peds: List[Peds] = []
        self._gui = InitGui()
        # self._convert_gui_location_dict()

    # def create_location_dict(self) -> Dict[int, Tuple[int, int]]:
    #
    #     # get the location dict from the gui object
    #     gui_location_dict = self._gui.get_positions_dict()
    #
    #     # initializing the max row (the most bottom row)
    #     # and the max column (the most east row)
    #     max_row, max_col = -1
    #

    # def _convert_gui_location_dict(self) -> None:
    #
    #     # number of rows in a triangle
    #     rows = 4
    #
    #     # getting the color positions dictionary from the gui object
    #     color_positions_dict = self._gui.get_color_positions_dict()
    #
    #     # getting the center positions list from the gui object
    #     center_positions_dict = self._gui.get_center_positions_list()
    #
    #     # Getting the distance between each cell
    #     cells_dist = self._gui.get_cell_distance()
    #
    #     # initializing the max row (the most bottom row)
    #     # and the max column (the most right row)
    #     max_row, max_col = -1, -1
    #
    #     # Dictionaries are ordered, so I know in advance that the top (1)
    #     # triangle is first, and then the order is going clockwise.
    #     # However, I want player1 to be the bottom (4) triangle,
    #     # and player2 to be the player in front player1 (1),
    #     # and so on counter-clockwise.
    #     player_order = [4, 1, 3, 6, 2, 5]
    #
    #     # Converting the dictionary to list, so it will be possible
    #     # to get the color name in the order of the player_order list above
    #     color_positions_list = list(color_positions_dict)
    #
    #     # print("list:", color_positions_list)
    #     print("dict:", color_positions_dict)
    #
    #     player_index = 1
    #     for num in player_order:
    #
    #         # getting the color name with the index num in the dictionary,
    #         # num-1 because we're started to count from 1 in player_order
    #         color_name = color_positions_list[num-1]
    #
    #         # getting the list of locations that have color_name
    #         # as a key in the dictionary:
    #         locations_list = color_positions_dict[color_name]
    #
    #         # sort the cells by y_coordinate, from top to bottom
    #         location_list_sorted = sorted(locations_list,
    #                                       key=lambda m: m[Y_COORD])
    #
    #         for i in range(rows):
    #
    #             if num in [1, 3, 5]:
    #                 cells_in_row = i + 1
    #
    #             else:
    #                 cells_in_row = rows - i
    #
    #             row_list = location_list_sorted[:cells_in_row]
    #
    #             # sort the cells in one row by the x_coordinate
    #             x_sorted_row_list = sorted(row_list)
    #
    #             for j in range(len(x_sorted_row_list)):
    #
    #                 coordinate = (player_index, j)
    #                 self._board[coordinate] = Peds(color_name,
    #                                                coordinate,
    #                                                j)
    #
    #         player_index += 1

    def _place_ped(self, ped: Peds) -> None:

        if ped in self._peds:
            raise Exception("This ped already exists")

        # else, place the ped on the board
        self._board[ped.get_location()] = ped
        self._peds.append(ped)

    # def possible_moves(self, ped: Peds) -> List[Coordinates]:
    #     """Return a list of possible moves for the given ped."""
    #
    #     # get the ped's current location
    #     ped_location = ped.get_location()

    def _find_neighbors(self, curr_pos: Coordinates) -> List[Coordinates]:
        """Return a list of the neighbor positions of the given position."""

        neighbors = []
        cell_dist = self._gui.get_cell_distance()

        # Define the bounding box around the cell based on its distance from
        # other cells. We multiply by 1.5 because the placement between
        # several cells is not exact, so we need to take a larger area.
        min_x = curr_pos[X_COORD] - cell_dist * 1.5
        max_x = curr_pos[X_COORD] + cell_dist * 1.5
        min_y = curr_pos[Y_COORD] - cell_dist * 1.5
        max_y = curr_pos[Y_COORD] + cell_dist * 1.5

        def is_valid_neighbor(position: Coordinates) -> bool:
            """Return True if the given position is valid, False otherwise.
            Assumes that the position that is given is from the
            dictionary/list from the gui object."""

            x, y = position

            return min_x <= x <= max_x and min_y <= y <= max_y

        # Iterate through the positions of the dictionary of the gui object,
        # and check if the position is a valid neighbor.
        for color, positions in self._gui.get_color_positions_dict().items():
            for pos in positions:
                if pos != curr_pos and is_valid_neighbor(pos):
                    neighbors.append(pos)

        # Iterate through the center positions list of the gui object,
        # and check if the position is a valid neighbor.
        for pos in self._gui.get_center_positions_list():
            if pos != curr_pos and is_valid_neighbor(pos):
                neighbors.append(pos)

        return neighbors

    def _is_valid_move(self, ped: Peds, end_location: Coordinates) -> bool:
        """Return True if the move is valid, False otherwise.
        Assumes that the new location is one of the locations
        of the dictionary or list from the gui."""

        # get the ped's current location
        curr_location = ped.get_location()

        # if the new location is occupied by another ped,
        # the move is invalid
        if self._board[end_location] is not None:
            return False

        # if the new location is in the list of neighbors of the current
        # location, and the new location is not occupied by another ped,
        # the move is valid
        if (end_location in self._find_neighbors(curr_location) and
                self._board[end_location] is None):
            return True

        # else, we need to check if we can hop over another ped/s
        # to the new location
        else:

            return self._can_hop_over(ped, end_location)

    def _can_hop_over(self, ped: Peds, end_location: Coordinates,
                      visited: Set[Coordinates] = None) -> bool:
        """A recursive function that checks if the given ped can hop over
        another ped or several ones to the new location.
        Assumes that the new location is one of the locations
        of the dictionary or list from the gui."""

        if visited is None:
            visited = set()

        curr_location = ped.get_location()

        # Add the current location to the visited set
        visited.add(curr_location)

        # Iterate through the neighbors of the current location and
        # recursively check if hopping over is possible
        for neighbor in self._find_neighbors(curr_location):

            # if the neighbor is not visited and is occupied by a ped,
            # meaning we can possibly hop over it
            if neighbor not in visited and self._board[neighbor] is not None:

                # Calculate the new location after hopping over the ped
                new_x = 2 * neighbor[X_COORD] - curr_location[X_COORD]
                new_y = 2 * neighbor[Y_COORD] - curr_location[Y_COORD]
                new_location = (new_x, new_y)

                # we need a little bit of offset because the placement
                # is not perfect
                offset_x = 5
                offset_y = 5

                changed = False
                # Check if the new location with the offset is in one of the
                # list of locations, and if it's not occupied by another ped
                for color in self._gui.get_color_positions_dict():
                    for pos in self._gui.get_color_positions_dict()[color]:
                        if (new_x - offset_x <= pos[X_COORD] <= new_x + offset_x and
                                new_y - offset_y <= pos[Y_COORD] <= new_y + offset_y and
                                self._board[new_location] is None):
                            new_location = pos
                            changed = True

                if not changed:
                    for pos in self._gui.get_center_positions_list():
                        if (new_x - offset_x <= pos[X_COORD] <= new_x + offset_x and
                                new_y - offset_y <= pos[Y_COORD] <= new_y + offset_y and
                                self._board[new_location] is None):
                            new_location = pos
                            changed = True

                # If we didn't land on any cell, means that
                # we are out of bounds, search for other neighbors.
                # Another possibility is that the new location is occupied
                if not changed:
                    continue

                # If the new location is the one we want to move to,
                # then we can hop over the ped
                if new_location == end_location:
                    return True

                # else, recursively check if we can hop over the ped
                # to the new location
                if self._can_hop_over(ped, end_location, visited):
                    return True

        # If we couldn't hop over any ped to the new location,
        # the move is invalid
        return False

    def _move_ped(self, ped: Peds, new_location: Coordinates) -> None:

        if ped not in self._peds:
            raise Exception("This ped does not exist")

        # if the new location is not valid, raise an exception
        if not self._is_valid_move(ped, new_location):
            raise Exception("Invalid move")

        # else
        # remove the ped from the old location
        self._board[ped.get_location()] = None

        # update the ped's location and place the ped in the new location
        ped.set_location(new_location)
        self._place_ped(ped)
