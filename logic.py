import logging
import datetime
import sys
from typing import Tuple, List, Union, Optional, Set

import pygame
from ped import Ped
from board import Board
from player import Player

X_COORD = 0
Y_COORD = 1

NEIGHBOR_MOVES = 0
HOP_MOVES = 1

PED_RADIUS = 4.7
CELL_RADIUS = 9.3

Coordinates = Tuple[float, float]

PLAYER_TURNS = 1
ANOTHER_TURN = 2

PLAYER_ORDER = [[4, 1, 3, 6, 2, 5],
                [4, 1, 3, 6],
                [4, 2, 6],
                [4, 1]]


class ChineseCheckersGame:

    def __init__(self, num_players: int, num_real_players: int) -> None:

        self._board = Board(num_players)  # Initialize the board

        for order in PLAYER_ORDER:
            if len(order) == num_players:
                self._player_order = order
                break

        self._gui = self._board.gui  # Initialize the GUI

        self._players: List[Player] = []  # Initialize the players
        self._current_player = None  # Initialize the current player
        self._initialize_players(num_players, num_real_players)  # Initialize the players
        self._create_and_place_peds()  # Place the peds in their starting positions

        # Initializing the log file.
        # the format is the date and time of the log, the name of the logger,
        # and the message.
        logging.basicConfig(filename='game.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(message)s')

    def _initialize_players(self, num_players: int, num_real_players: int) -> None:
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
                    # stating the time of the turn, to be used in the log file
                    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logging.info(f"Player {self._players.index(self._current_player) + 1} "
                                 f"started his turn at {start_time}")
                    # True if a player made a turn successfully,
                    # False otherwise
                    make_turn, locations = self._handle_click(pos)

                    if make_turn:

                        # # log the move of the player
                        # logging.info(f"Player {self._players.index(self._current_player) + 1} "
                        #              f"moved from {locations[0]} to {locations[1]}")
                        # Check if the any player won the game
                        won_index = self._check_winner()
                        if won_index is not None:
                            print("Player won the game!")
                            return "Player " + str(won_index) + " won the game!"

                        # If no player won the game, continue the game
                        print("Player made a turn successfully.")

                        # If the player made a hop, let him do another turn
                        # from the new location, if possible
                        if locations is not None:
                            print("locations: ", locations)
                            old_location, current_location = locations

                            # Create a set of the visited locations
                            visited = set()
                            visited.add(old_location)

                            # Check if the player can make another turn/s
                            new_location = self._check_another_turn(
                                visited, current_location)

                            while new_location is not None:

                                # Updating the locations
                                old_location = current_location
                                current_location = new_location
                                visited.add(old_location)

                                print("Player can make another turn.")
                                new_location = self._check_another_turn(
                                    visited, current_location)

                                # # for any case, unhighlight leftovers
                                # self._gui.unhighlight_surface(
                                #     self._gui.get_highlight_surface())

                        self._change_player()  # change the player
                        return won_index

                    # If a player failed to make a turn, let him try again
                    else:
                        print("Player failed to make a turn. Try again.")

    def _handle_click(self, mouse_pos: Tuple[int, int]) -> \
            Tuple[bool, Optional[Tuple[Coordinates, Coordinates]]]:
        """Handle the click of the player.
        Returns True if the player made a turn successfully, False otherwise.
        In addition, returns the old and new locations if the player
        made a hop, None otherwise."""

        # Get the peds of the current player
        player_peds = self._current_player.get_peds()

        # Iterate through the positions of the current player's peds
        # in the board and check if a click was made on a ped
        for ped in player_peds:

            position = ped.get_location()
            ped_x = position[X_COORD]
            ped_y = position[Y_COORD]

            # Check if the click was made on the boundaries of a ped
            if ((ped_x - PED_RADIUS) <= mouse_pos[X_COORD] <= (ped_x + PED_RADIUS) and
                    (ped_y - PED_RADIUS) <= mouse_pos[Y_COORD] <= (ped_y + PED_RADIUS)):

                # if we're here, it means that we are in a turn state
                is_moved, new_location = self._turn(ped)

                # Update the display
                pygame.display.flip()

                if is_moved:  # if the move was successful

                    # If the player made a hop move, return the new location
                    # with the old location of the ped. Otherwise, return None.
                    if new_location is not None:
                        return True, (position, new_location)

                    return True, None  # A neighbor move was made

                else:
                    # else, there was some sort of error with the move,
                    # so do the turn from the beginning
                    return False, None

        # If the click was not made on a ped, return False
        return False, None

    def _turn(self, ped: Ped) -> Tuple[bool, Optional[Coordinates]]:
        """Handle the turn of the current player.
        Return True if the turn was successful, False otherwise.
        In addition, return the new location if the player made a hop move,
        None otherwise."""

        # Bring the possible moves of the selected ped from the board
        print("getting possible moves")
        possible_moves = self._board.find_valid_moves(ped.get_location())

        # If there are no possible moves, prompt the player to select
        # another ped and do nothing
        if (possible_moves[NEIGHBOR_MOVES] == [] and
                possible_moves[HOP_MOVES] == []):
            self._show_message("An error occurred. Restarting turn.")
            return False, None

        # If the ped has possible moves, change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

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
            # print("setting cursor to arrow")
            self._show_message("Please select a valid move. Restarting turn.")
            return False, None

        # The location was chosen, unhighlight the possible moves
        # and change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self._gui.unhighlight_surface(self._gui.get_highlight_surface())

        try:
            # Move the ped to the selected location
            self._board.move_ped(ped, new_location)

        except Exception as e:
            print("Error: ", e)
            sys.exit()

        # If the player made a hop move
        if new_location in possible_moves[HOP_MOVES]:
            return True, new_location

        # If the player made a neighbor move
        return True, None

    def _check_another_turn(self, visited: Set[Coordinates],
                            curr_location: Coordinates) -> \
            Optional[Coordinates]:
        """Check if the player can make another turn, from
        the new location, if it's not been visited before.
        The move can only be a hop move.
        If the player can make a move, return True and the new location.
        Otherwise, return None."""

        try:
            # Get the ped object from the board
            ped = self._board.get_ped_by_location(curr_location)

        except KeyError as e:
            print("Error: ", e)
            sys.exit()

        # Bring the possible moves of the selected ped from the board
        possible_moves = self._board.find_valid_moves(ped.get_location())

        for loc in possible_moves[HOP_MOVES]:
            if loc in visited:
                possible_moves[HOP_MOVES].remove(loc)

        # If there are no possible moves, or the possible moves are only
        # neighbor moves, do nothing
        if not possible_moves[HOP_MOVES]:
            return None

        # print("highlighting neighbor moves: ", possible_moves[NEIGHBOR_MOVES])
        # print("highlighting hop moves: ", possible_moves[HOP_MOVES])

        # Making it that only hop moves are possible
        hop_moves_only = [possible_moves[HOP_MOVES]]

        # If the ped has possible moves, change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        # Highlight the possible moves (guaranteed to exist)
        self._gui.highlight_locations(self._gui.get_highlight_surface(),
                                      hop_moves_only)

        self._show_message(f"Player {self._players.index(self._current_player) + 1} "
                           f"can make another turn! \nPlease select a move to "
                           f"continue, or click anywhere else to finish the "
                           f"turn.", ANOTHER_TURN)

        # wait for a move
        new_location = self._wait_for_move(possible_moves)  # to fix

        # If the player clicked on something other than a possible move,
        # in means that the player wants to finish the turn
        if new_location is None:

            self._gui.unhighlight_surface(self._gui.get_highlight_surface())
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self._show_message("Finishing turn.")
            return None

        # The location was chosen, unhighlight the possible moves
        # and change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self._gui.unhighlight_surface(self._gui.get_highlight_surface())

        try:
            # Move the ped to the selected location
            self._board.move_ped(ped, new_location)

        except Exception as e:
            print("Error: ", e)
            sys.exit()

        return new_location

    def _select_ped(self, ped: Ped) -> Optional[List[List[Coordinates]]]:
        """Select the given ped and highlight its possible moves.
        Then, wait for the player to make a move.
        Returns the ped's possible moves."""

        # Bring the possible moves of the selected ped from the board
        print("getting possible moves")
        possible_moves = self._board.find_valid_moves(ped.get_location())

        # If there are no possible moves, prompt the player to select another ped
        # and do nothing
        if (possible_moves[NEIGHBOR_MOVES] == [] and
                possible_moves[HOP_MOVES] == []):
            return None

        return possible_moves

    @staticmethod
    def _wait_for_move(possible_moves: List[List[Coordinates]]) -> Optional[Coordinates]:
        """Wait for the player to make a move from the given possible moves.
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
                    for move_type in possible_moves:
                        for location in move_type:

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

        if purpose != PLAYER_TURNS:
            # Wait for a short time before clearing the message
            if purpose == ANOTHER_TURN:
                pygame.time.delay(5000)  # 5 seconds

            else:
                pygame.time.delay(1800)  # 1.8 seconds

            # Clear the message from the screen
            self._gui.clear_message()

    def _check_winner(self) -> Optional[int]:
        """Check if the game has a winner."""

        for player in self._players:

            # Check if all the peds of the player are in the home of the opponent
            if all(self._gui.is_in_opposite_home(ped)
                   for ped in player.get_peds()):

                return self._players.index(player) + 1

        return None



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

    # Creating the game object
    game = ChineseCheckersGame(num_of_players, num_of_real_players)
    # game._show_message(
    #     f"Player {game._players.index(game._current_player) + 1} "
    #     f"can make another turn! \nPlease select a move to "
    #     f"continue, or click anywhere else to finish the "
    #     f"turn.", ANOTHER_MOVE)

    game.run()  # Running the game
