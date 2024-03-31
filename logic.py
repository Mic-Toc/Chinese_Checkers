import sys
from typing import Tuple, List, Union, Set

import pygame
from ped import Ped
from board import Board
from pygame_switch import InitGui

X_COORD = 0
Y_COORD = 1

PED_RADIUS = 4.7
CELL_RADIUS = 9.3

Coordinates = Tuple[float, float]


class ChineseCheckersGame:

    def __init__(self, num_players: int) -> None:

        self._board = Board()  # Initialize the board
        self._gui = self._board.gui  # Initialize the GUI
        self._create_and_place_peds()  # Place the peds in their starting positions

        self._players = []  # Initialize the players
        self._current_player = None  # Initialize the current player

    def _create_and_place_peds(self) -> None:
        """Placing the peds in their starting positions in the board."""

        # Initialize the peds
        peds = self._create_peds()

        # Place the peds in their starting positions
        self._board.place_peds(peds)

    def _create_peds(self) -> List[Ped]:
        """Create the peds of the game."""

        peds = []

        # Create the peds of the game by retrieving the positions
        # of the colored triangles from the gui.
        for color, positions in self._gui.get_color_positions_dict().items():
            for position in positions:
                new_ped = Ped(color, position)
                peds.append(new_ped)

        return peds

    def _handle_events(self) -> None:
        """Handle the events of the game."""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                # Check if the left mouse button was clicked
                if event.button == 1:

                    # Get the position of the mouse
                    pos = pygame.mouse.get_pos()
                    print("Mouse position: ", pos)

                    # handle the click
                    # True if a player made a turn successfully,
                    # False otherwise
                    make_turn = self._handle_click(pos)

                    if make_turn:
                        print("Player made a turn successfully.")
                        # If a player made a turn successfully,
                        # update the gui and exit the function
                        # self._gui.update_ped()
                        return

                    # If a player failed to make a turn, let him try again
                    else:
                        print("Player failed to make a turn. Try again.")

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle the click of the player."""

        # Iterate through the positions of the peds in the board
        # and check if a click was made on a ped
        for position in self._board.get_peds_locations():
            ped_x = position[X_COORD]
            ped_y = position[Y_COORD]

            # Check if the click was made on the boundaries of the ped
            if ((ped_x - PED_RADIUS) <= mouse_pos[X_COORD] <= (ped_x + PED_RADIUS) and
                    (ped_y - PED_RADIUS) <= mouse_pos[Y_COORD] <= (ped_y + PED_RADIUS)):

                # # Check if the ped belongs to the current player
                # if self._current_player.get_color() == color:
                #     self._current_player.set_location((ped_x, ped_y))

                # if we're here, it means that we are in a turn state
                is_moved = self._turn((ped_x, ped_y))

                # Update the display
                pygame.display.flip()

                if is_moved:  # if the move was successful
                    return True  # NEED TO IMPLEMENT

                else:
                    # else, there was some sort of error with the move,
                    # so do the turn from the beginning
                    return False  # NEED TO IMPLEMENT

        # If the click was not made on a ped, return False
        return False

    def _turn(self, location: Tuple[float, float]) -> bool:
        """Handle the turn of the current player."""

        # select the ped and his possible moves
        ped, possible_moves = self._select_ped(location)

        # If there was an error with the location, do nothing
        if ped is None and possible_moves is None:
            self._show_temp_message(
                "An error occurred. Restarting turn.")
            return False

        # If the ped has no possible moves, prompt the player to select another ped
        elif possible_moves is None:

            self._show_temp_message("This ped has no possible moves. Restarting turn.")
            return False

        # If the ped has possible moves
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        print("setting cursor to broken_x")
        # Highlight the possible moves (guaranteed to exist)
        self._gui.highlight_locations(self._gui.get_highlight_surface(),
                                      possible_moves)

        # wait for a move
        new_location = self._wait_for_move(possible_moves)

        # If the player clicked on something other than a possible move,
        # unhighlight the possible moves and prompt the player to select another ped
        if new_location is None:

            self._gui.unhighlight_surface(self._gui.get_highlight_surface())
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            print("setting cursor to arrow")
            self._show_temp_message("Please select a valid move. Restarting turn.")
            return False

        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        # The location was chosen, unhighlight the possible moves
        self._gui.unhighlight_surface(self._gui.get_highlight_surface())


        # Move the ped to the selected location
        self._board.move_ped(ped, new_location)

        return True


    def _select_ped(self, location: Tuple[float, float]) -> \
            Union[Tuple[Ped, List[Coordinates]], Tuple[None, None], Tuple[Ped, None]]:
        """Select a ped and highlight its possible moves.
        Then, wait for the player to make a move. """

        try:
            # Get the ped object from the board
            ped = self._board.get_ped_by_location(location)

        # If the location is not in the board, do nothing
        except KeyError:
            return None, None

        # # Check if the ped belongs to the current player
        # if self._current_player.get_color() == color:

        # Bring the possible moves of the selected ped from the board
        print("getting possible moves")
        possible_moves = self._board.find_valid_moves(ped.get_location()    )
        # If there are no possible moves, prompt the player to select another ped
        # and do nothing
        if not possible_moves:
            return ped, None

        return ped, possible_moves

    @staticmethod
    def _wait_for_move(possible_moves: List[Coordinates]) -> Union[Coordinates, None]:
        """Wait for the player to make a move from the highlighted locations.
        Returns the location of the move if it was made, None otherwise. """

        done_a_move = False

        while not done_a_move:
            for event in pygame.event.get():

                # Check if the player wants to quit the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Get the position of the mouse
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if the mouse click was made on one of
                    # the highlighted (possible moves) locations
                    for location in possible_moves:

                        cell_x = location[X_COORD]
                        cell_y = location[Y_COORD]

                        # Check if the click was made on the boundaries of the location
                        if ((cell_x - CELL_RADIUS) <= mouse_pos[X_COORD] <= (cell_x + CELL_RADIUS) and
                                (cell_y - CELL_RADIUS) <= mouse_pos[Y_COORD] <= (cell_y + CELL_RADIUS)):

                            return location

                    # if the click was not made on a possible move, stop
                    # waiting for a move
                    done_a_move = True

        # if the player made invalid move, return None
        return None

    def _show_temp_message(self, message: str) -> None:
        """Show a temporary message on the screen."""

        self._gui.show_message(message)

        # Wait for a short time before clearing the message
        pygame.time.delay(1800)  # 1.8 seconds

        # Clear the message from the screen
        self._gui.clear_message()

    def run(self):

        pygame.mouse.set_cursor(*pygame.cursors.arrow)  # Set the cursor to the default arrow

        # Creating a clock object to control the frame rate
        clock = pygame.time.Clock()

        while True:

            self._handle_events()  # Handle the events

            pygame.display.flip()  # Update the display

            clock.tick(60)  # 60 frames per second


if __name__ == "__main__":

    game = ChineseCheckersGame(6)  # Creating the game object

    game.run()  # Running the game
