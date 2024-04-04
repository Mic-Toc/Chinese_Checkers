from typing import Tuple, List, Dict, Union, Optional

from ped import Ped
from pygame_switch import InitGui

Coordinates = Tuple[float, float]

# Constants from the GUI
FRAME_HEIGHT = 590
FRAME_WIDTH = 930
BOARD_HEIGHT = 0.95 * FRAME_HEIGHT
BOARD_WIDTH = 0.6 * FRAME_WIDTH

X_COORD = 0
Y_COORD = 1


class Board:

    def __init__(self, num_players: int) -> None:

        self._peds: List[Ped] = []
        self.gui = InitGui(num_players)

        board: Dict[Coordinates, Union[Ped, None]] = dict()

        # Getting the locations of all cells from the gui object
        all_locations = self.get_all_positions()
        for location in all_locations:
            board[location] = None

        self._board = board

        self.board_state: List[Dict[Coordinates, Union[Ped, None]]] = []

    def place_peds(self, peds: List[Ped]) -> None:
        """Placing the given peds on their initial locations on the board."""

        for ped in peds:
            if ped in self._peds:
                raise Exception("This ped already exists")

            # else, place the ped on the board
            self._board[ped.get_location()] = ped
            self._peds.append(ped)  # add the ped to the list of peds

        self._update_board_state()

    def _find_neighbors(self, curr_pos: Coordinates) -> List[Coordinates]:
        """Return a list of the neighbor positions of the given position."""

        neighbors = []
        cell_dist = self.gui.get_cell_distance()

        # Define the bounding box around the cell based on its distance from
        # other cells. We multiply by 1.1 because the placement between
        # several cells is not exact, so we need to take a larger area.
        min_x = curr_pos[X_COORD] - cell_dist * 1.2
        max_x = curr_pos[X_COORD] + cell_dist * 1.2
        min_y = curr_pos[Y_COORD] - cell_dist * 1.2
        max_y = curr_pos[Y_COORD] + cell_dist * 1.2

        def is_valid_neighbor(position: Coordinates) -> bool:
            """Return True if the given position is valid, False otherwise.
            Assumes that the position that is given is from the
            dictionary/list from the gui object."""

            x, y = position

            return min_x <= x <= max_x and min_y <= y <= max_y

        for pos in self.get_all_positions():
            if pos != curr_pos and is_valid_neighbor(pos):
                neighbors.append(pos)

        # print("pos: ", curr_pos, "neighbors: ", neighbors)
        return neighbors

    def _is_valid_move(self, curr_location: Coordinates,
                       end_location: Coordinates) -> Tuple[bool, bool]:
        """Return True if the move is valid, False otherwise.
        In addition, return True if the move was a hop.
        Assumes that the new location is one of the locations
        of the dictionary or list from the gui."""

        curr_ped = self._board[curr_location]
        in_opposite_home = self.gui.is_in_opposite_home(curr_ped)

        # if the ped is in the foreign home, moving out of it is invalid
        if in_opposite_home:
            opposite_color = self.gui.color_of_opposite_home(curr_location)
            # print("In the home of: ", opposite_color)
            # Means that the ped is not in any foreign home
            # (although we checked that it is in a foreign home)
            if opposite_color is None:
                print("There is a problem.")  # Not supposed to happen (check)
                pass

            elif (end_location not in
                    self.gui.get_color_positions_dict()[opposite_color]):
                return False, False

        # if the new location is occupied by another ped,
        # the move is invalid
        if self._board[end_location] is not None:
            return False, False

        # if the new location is in the list of neighbors of the current
        # location, the move is valid
        if end_location in self._find_neighbors(curr_location):
            return True, False

        # else, we need to check if we can hop over another ped/s
        # to the new location
        else:

            is_hop = self._can_hop_over(curr_location, end_location)
            return is_hop, is_hop

    def _can_hop_over(self, curr_location: Coordinates,
                      end_location: Coordinates,
                      ) -> bool:
        """A function that checks if we can get from
        the current location to the new one using a single hop.
        Assumes that the new location is one of the locations
        of the dictionary or list from the gui."""

        # Iterate through the neighbors of the current location and
        # check if hopping over is possible
        for neighbor in self._find_neighbors(curr_location):

            # if the neighbor is not visited and is occupied by a ped,
            # meaning we can possibly hop over it
            if self._board[neighbor] is not None:

                # Calculate the new location after hopping over the ped
                new_x = 2 * neighbor[X_COORD] - curr_location[X_COORD]
                new_y = 2 * neighbor[Y_COORD] - curr_location[Y_COORD]
                new_location = (new_x, new_y)

                # we need a little bit of offset because the placement
                # is not perfect
                offset_x = 5
                offset_y = 5

                # check for the end location in the center positions list
                for pos in self.gui.get_center_positions_list():

                    if (new_x - offset_x <= pos[
                        X_COORD] <= new_x + offset_x and
                            new_y - offset_y <= pos[
                                Y_COORD] <= new_y + offset_y and
                            self._board[pos] is None):
                        new_location = pos

                        if new_location == end_location:
                            return True

                # If we didn't find the new location at the center,
                # we need to check if the new location is within
                # the outer triangles locations
                for colors, positions in self.gui.get_color_positions_dict().items():
                    for pos in positions:
                        if (new_x - offset_x <= pos[X_COORD] <= new_x + offset_x and
                                new_y - offset_y <= pos[Y_COORD] <= new_y + offset_y and
                                self._board[pos] is None):
                            new_location = pos

                            # if we found the new location, we can break
                            if new_location == end_location:
                                return True

        return False  # we didn't find a way to hop over

    def find_valid_moves(self, curr_pos: Coordinates) -> List[List[Coordinates]]:
        """Return a list of valid moves for the given ped."""

        print("Finding valid moves for", curr_pos)
        valid_moves = []
        neighbor_moves = []
        hop_moves = []

        # Get all the positions of the board
        all_positions = self.get_all_positions()

        # Iterate through all the positions of the board
        for position in all_positions:

            # skip the current position
            if position == curr_pos:
                print("position is the same as curr_pos: " + str(position))
                continue

            # if the move is valid, add it to the list of valid moves
            is_valid, is_hop = self._is_valid_move(curr_pos, position)
            if is_valid and not is_hop:
                neighbor_moves.append(position)
            elif is_valid and is_hop:
                hop_moves.append(position)

        valid_moves.append(neighbor_moves)
        valid_moves.append(hop_moves)

        return valid_moves

    def get_all_positions(self) -> List[Coordinates]:
        """Return a list of all the positions of the board,
        retrieved from the gui object."""

        all_positions = []

        for color, positions in self.gui.get_color_positions_dict().items():
            all_positions.extend(positions)

        all_positions.extend(self.gui.get_center_positions_list())

        return all_positions

    def _find_peds_by_color(self, color: str) -> List[Ped]:
        """Return a list of peds with the given color."""

        peds_list = []

        for ped in self._peds:
            if ped.get_color() == color:
                peds_list.append(ped)

        return peds_list

    def get_ped_by_location(self, location: Coordinates) -> Optional[Ped]:
        """Return the ped at the given location.
        If no ped is found, raises an error."""

        if location in self._board.keys() and self._board[location] is not None:
            return self._board[location]

        print(location in self._board.keys(), self._board[location] is not None)
        raise KeyError("No ped found at this location")

    def move_ped(self, ped: Ped, new_location: Coordinates) -> None:
        """Move the ped to the new location."""

        if ped not in self._peds:
            raise Exception("This ped does not exist")

        # if the new location is not valid, raise an exception
        if not self._is_valid_move(ped.get_location(), new_location):
            raise Exception("Invalid move")

        # else
        # remove the ped from the old location
        old_location = ped.get_location()
        self._board[old_location] = None

        # update the ped's location and place the ped in the new location
        ped.set_location(new_location)
        self._board[new_location] = ped

        # update the gui
        self.gui.update_ped(self.gui.get_temp_surface(), old_location, ped)

        self._update_board_state()

    def get_peds_locations_by_color(self, color: str) -> List[Coordinates]:
        """Return a list of all the locations of peds with the given color."""

        locations = []

        for ped in self._peds:
            if ped.get_color() == color:
                locations.append(ped.get_location())

        return locations

    def get_all_peds_locations(self) -> List[Coordinates]:
        """Return a list of all the locations of all the peds."""

        locations = []

        for ped in self._peds:
            locations.append(ped.get_location())

        return locations

    def get_all_peds(self):
        """Return all the ped objects on the board."""

        return self._peds

    def _update_board_state(self) -> None:
        """Update the state of the board based on the move number."""

        self.board_state.append(self._board)
