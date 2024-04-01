import sys
from typing import Tuple, List, Union, Optional

import pygame
from ped import Ped
from board import Board
from player import Player

X_COORD = 0
Y_COORD = 1

PED_RADIUS = 4.7
CELL_RADIUS = 9.3

Coordinates = Tuple[float, float]

PLAYER_TURNS = 1

PLAYER_ORDER = [[4, 1, 3, 6, 2, 5],
                [4, 1, 3, 6],
                [4, 2, 6],
                [4, 1]]


class ChineseCheckersGame:

    def __init__(self, num_players: int) -> None:

        self._board = Board(num_players)  # Initialize the board

        for order in PLAYER_ORDER:
            if len(order) == num_players:
                self._player_order = order
                break

        self._gui = self._board.gui  # Initialize the GUI

        self._players: List[Player] = []  # Initialize the players
        self._current_player = None  # Initialize the current player
        self._initialize_players(num_players)  # Initialize the players
        self._create_and_place_peds()  # Place the peds in their starting positions

    def _initialize_players(self, num_players: int) -> None:
        """Initialize the players of the game."""

        for i in range(num_players):

            # Create a player with the color as ordered in the player_order list.
            # num-1 because the list is we're starting the player order from 1
            color = list(self._gui.get_color_positions_dict().keys())[self._player_order[i]-1]

            self._players.append(Player(color))

        self._current_player = self._players[0]

        # Showing a message that indicates the current player
        self._show_message("Player 1's turn", PLAYER_TURNS)

    def _change_player(self) -> None:
        """Change the current player to the next one."""

        # Changing the index of the current player to the next one
        player_index = self._players.index(self._current_player)
        next_player_index = (player_index + 1) % len(self._players)
        self._current_player = self._players[next_player_index]

        # Showing a message that indicates the next player
        self._show_message(f"Player {next_player_index + 1}'s turn",
                           PLAYER_TURNS)

    def _create_and_place_peds(self) -> None:
        """Placing the peds in their starting positions in the board."""

        # Initialize the peds
        peds = self._create_peds()

        # Place the peds in their starting positions
        self._board.place_peds(peds)

    def get_player_by_color(self, color: str) -> Union[Player, None]:
        """Return the player with the given color."""

        for player in self._players:
            if player.get_color() == color:
                return player

        raise ValueError("No player with the color", color)

    def _create_peds(self) -> List[Ped]:
        """Creating the peds of the game, and assigning them to the players."""

        peds = []

        # Getting the colors of the players in the order they play,
        # taking into account the number of players
        playable_colors = self._gui.playable_colors()

        # # Getting the colors of the players in the order they play,
        # # taking into account the number of players
        # for num in self._player_order:
        #     playable_colors.append(list(self._gui.get_color_positions_dict().keys())[num-1])

        # Create the peds of the game by retrieving the positions
        # of the colored triangles from the gui.
        for color in playable_colors:
            for position in self._gui.get_color_positions_dict()[color]:
                new_ped = Ped(color, position)

                try:
                    # Assign the ped to the player with the same color
                    player_by_color = self.get_player_by_color(color)

                except ValueError as e:
                    print(e)
                    sys.exit()

                player_by_color.add_ped(new_ped)
                peds.append(new_ped)

        return peds

    def _handle_events(self) -> Optional[str]:
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

                        # Check if the any player won the game
                        won_index = self._check_winner()
                        if won_index is not None:
                            print("Player won the game!")
                            return "Player " + str(won_index) + " won the game!"

                        # If no player won the game, continue the game
                        print("Player made a turn successfully.")

                        self._change_player()  # change the player
                        return won_index

                    # If a player failed to make a turn, let him try again
                    else:
                        print("Player failed to make a turn. Try again.")

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle the click of the player."""

        player_peds = self._current_player.get_peds()  # Get the peds of the current player

        # Iterate through the positions of the current player's peds
        # in the board and check if a click was made on a ped
        for ped in player_peds:

            position = ped.get_location()
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
            self._show_message("An error occurred. Restarting turn.")
            return False

        # If the ped has no possible moves, prompt the player to select another ped
        elif possible_moves is None:

            self._show_message(
                "This ped has no possible moves. Restarting turn.")
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
            self._show_message("Please select a valid move. Restarting turn.")
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
        possible_moves = self._board.find_valid_moves(ped.get_location())

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

    def _show_message(self, message: str, purpose: int = 0) -> None:
        """Show a temporary message on the screen."""

        self._gui.show_message(message, purpose)

        if purpose == 0:
            # Wait for a short time before clearing the message
            pygame.time.delay(1800)  # 1.8 seconds

            # Clear the message from the screen
            self._gui.clear_message()

    def _check_winner(self) -> Optional[int]:
        """Check if the game has a winner."""

        for i in range(len(self._players)):

            # Check if all the peds of the player are in the home of the opponent
            if all(self._is_opposite_home(i + 1, ped.get_location())
                   for ped in self._players[i].get_peds()):

                return i+1

        return None

    def _is_opposite_home(self, player_index: int,
                          location: Coordinates) -> bool:
        """Check if the ped in the given location (assuming there is
        a ped there) is in the home of the opposite corner."""

        player_index_by_order = self._player_order[player_index-1]

        # there is 3 (len(PLAYER_ORDER[0]) / 2) because the number of
        # triangles in a hexagram is always 6, and the opposite
        # triangle is 3 places to step from the current.
        opposite_index = player_index_by_order - len(PLAYER_ORDER[0]) // 2  # 3
        if opposite_index <= 0:
            opposite_index += 6

        # find the matching color home locations
        home_locations = list(self._gui.get_color_positions_dict().values())[opposite_index]

        # if the given location is in the matching color home, return true,
        # otherwise false.
        return location in home_locations

    def run(self):

        pygame.mouse.set_cursor(*pygame.cursors.arrow)  # Set the cursor to the default arrow

        # Creating a clock object to control the frame rate
        clock = pygame.time.Clock()

        winner = None

        # The main loop of the game
        while winner is None:

            pygame.display.flip()  # Update the display

            clock.tick(60)  # 60 frames per second

            winner = self._handle_events()  # Handle the events

        self._show_message(f"Player {winner} wins!")  # Show the winner message


if __name__ == "__main__":

    try:
        # Number of players in the game using command line arguments
        # Assuming that what was given is legal
        num_of_players = int(sys.argv[1])
        possible_num_of_players = [2, 3, 4, 6]

        if num_of_players not in possible_num_of_players:
            raise ValueError

    except (ValueError, IndexError):
        print("Please enter a valid number of players [2,3,4,6].")
        sys.exit()

    try:
        # Number of players in the game using command line arguments
        # Assuming that what was given is legal
        num_of_real_players = int(sys.argv[2])

        if (num_of_real_players > num_of_players or
                num_of_real_players not in (possible_num_of_players + [0])):
            raise ValueError

    except (ValueError, IndexError):
        print("Please enter a valid number of real players, "
              "which is expected to be within the number of players.")
        sys.exit()

    game = ChineseCheckersGame(num_of_players)  # Creating the game object

    game.run()  # Running the game
