import json
import logging
import sys
import time
import random
from datetime import datetime
from typing import Tuple, List, Union, Optional, Set

import pygame

import funcs
from board import Board
from ped import Ped
from players import Human, Bot
from pygame_switch import InitGui

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

    def __init__(self, num_players: int, num_real_players: int,
                 board: Board = None, gui: InitGui = None,
                 players: List[Union[Human, Bot]] = None,
                 current_player: Union[Human, Bot] = None,
                 log_file=None) -> None:

        from board import Board  # local import

        if board is not None and gui is not None and \
                players is not None and current_player is not None:

            self._board = board
            self._gui = gui
            self._num_players = num_players
            self._num_real_players = num_real_players
            self._players = players
            self._current_player = current_player

            self.log_file_name = log_file

            # Showing a message that indicates the current player
            self._show_message(f"{self._is_bot(self._current_player)} "
                               f"{self._players.index(current_player) + 1}'s turn",
                               PLAYER_TURNS)

        else:

            # self._game_history = GameHistory(LOG_FILE, Board(num_players), num_players)
            self._board = Board(num_players)  # Initialize the board

            for order in PLAYER_ORDER:
                if len(order) == num_players:
                    self._player_order = order
                    break

            self._gui = self._board.gui  # Initialize the GUI

            self._players: List[Union[Human, Bot]] = []  # Initialize the players
            self._num_players = num_players
            self._num_real_players = num_real_players

            self._current_player = None  # Initialize the current player
            self._initialize_players()  # Initialize the players
            self._create_and_place_peds()  # Place the peds in their starting positions

            # Initializing the log file.
            self.log_file_name = f"game_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}" \
                                 f".txt"
            logging.basicConfig(filename=self.log_file_name, level=logging.INFO)

    def _initialize_players(self) -> None:
        """Initialize the players of the game."""

        for i in range(self._num_real_players):

            # Create a player with the color as ordered in the player_order list.
            # num-1 because the list is we're starting the player order from 1
            color = list(self._gui.get_color_positions_dict().keys())[
                self._player_order[i] - 1]

            self._players.append(Human(color))

        for j in range(self._num_real_players, self._num_players):
            # Create a bot player with the color as ordered in the player_order list.
            # num-1 because the list is we're starting the player order from 1
            color = list(self._gui.get_color_positions_dict().keys())[
                self._player_order[j] - 1]

            self._players.append(Bot(color))

        self._current_player = self._players[0]

        # Showing a message that indicates the current player
        self._show_message(f"{self._is_bot(self._current_player)} 1's turn", PLAYER_TURNS)

    def _change_player(self) -> None:
        """Change the current player to the next one."""

        # Changing the index of the current player to the next one
        player_index = self._players.index(self._current_player)
        next_player_index = (player_index + 1) % len(self._players)
        self._current_player = self._players[next_player_index]

        # Showing a message that indicates the next player
        self._show_message(f"{self._is_bot(self._current_player)} {next_player_index + 1}"
                           f"'s turn",
                           PLAYER_TURNS)

    def _create_and_place_peds(self) -> None:
        """Placing the peds in their starting positions in the board."""

        # Initialize the peds
        peds = self._create_peds()

        # Place the peds in their starting positions
        self._board.place_peds(peds)

    def get_player_by_color(self, color: str) -> Union[Human, Bot, None]:
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
                    self._clear_log_file()
                    sys.exit()

                player_by_color.add_ped(new_ped)
                peds.append(new_ped)

        return peds

    def handle_events(self) -> Optional[str]:
        """Handle the events of the game."""

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                raise SystemExit


            elif (event.type == pygame.MOUSEBUTTONDOWN or
                  self._is_bot(self._current_player) == "Bot"):

                # Check if the left mouse button was clicked
                if self._is_bot(self._current_player) == "Bot" or event.button == 1:
                    return self._start_player_turn()

    def _start_player_turn(self) -> Optional[str]:
        """Start the turn of the current player."""

        # Get the position of the mouse
        pos = pygame.mouse.get_pos()

        # log the start of the turn
        self._log_game_data(
            (self._is_bot(self._current_player) + (" " +
                                                   str(self._players.index(
                                                       self._current_player) + 1))),
            message="started his turn")

        locations = None
        is_hop = False
        if self._is_bot(self._current_player) == "Bot":
            locations, is_hop = self._handle_bot_turn()

        if self._is_bot(self._current_player) == "Human":
            # Returns True if a player made a turn successfully,
            # False otherwise
            locations, is_hop = self._handle_human_turn(pos)

        if locations is not None:

            # log the move of the player
            self._log_game_data(
                (self._is_bot(self._current_player) + (" " +
                                                       str(self._players.index(
                                                           self._current_player) + 1))),
                start_location=locations[0], end_location=locations[1])

            # Check if the any player won the game
            won_index = self._check_winner()
            if won_index is not None:
                return f"{self._is_bot(self._current_player)} " \
                       + str(won_index) + " won the game!"

            # If no player won the game, continue the game

            # If the player made a hop, let him do another turn
            # from the new location, if possible
            if is_hop:
                old_location, current_location = locations

                # Create a set of the visited locations
                visited = set()
                visited.add(old_location)

                # Check if the player can make another hop turn/s
                new_hop_location = self._check_another_turn(
                    visited, current_location)

                while new_hop_location is not None:
                    # logging the hop turn
                    self._log_game_data(
                        (self._is_bot(self._current_player) + (" " +
                         str(self._players.index(self._current_player) + 1))),
                        start_location=new_hop_location,
                        end_location=locations[1],
                        message="had an additional hop.")

                    # Updating the locations
                    old_location = current_location
                    current_location = new_hop_location
                    visited.add(old_location)

                    new_hop_location = self._check_another_turn(
                        visited, current_location)

            self._change_player()  # change the player
            return won_index

        # If a player failed to make a turn, let him try again
        # and delete the last log message, because the player
        # didn't actually started his turn
        else:
            self._delete_last_log_message()

    def _handle_bot_turn(self) -> Tuple[Optional[Tuple[Coordinates, Coordinates]], bool]:
        """Handle the turn of the bot."""

        chosen_ped = random.choice(self._current_player.get_peds())
        ped_position = chosen_ped.get_location()
        # if we're here, it means that we are in a turn state
        new_location, is_hop = self._turn(chosen_ped)

        # Update the display
        pygame.display.flip()

        if new_location is not None:  # if the move was successful

            # If the player made a hop move, return the new location
            # with the old location of the ped. Otherwise, return None.
            if is_hop:
                return (ped_position, new_location), True

            return (ped_position, new_location), False  # A neighbor move was made

        else:
            # else, there was some sort of error with the move,
            # so do the turn from the beginning
            return None, False

    def _handle_human_turn(self, mouse_pos: Tuple[int, int]) -> \
            Tuple[Optional[Tuple[Coordinates, Coordinates]], bool]:
        """Handle the click of the player.
        Returns the old and new locations if the player made a turn
        successfully, None otherwise.
        In addition, returns True if the player made a hop, False otherwise."""

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
                new_location, is_hop = self._turn(ped)

                # Update the display
                pygame.display.flip()

                if new_location is not None:  # if the move was successful

                    # If the player made a hop move, return the new location
                    # with the old location of the ped. Otherwise, return None.
                    if is_hop:
                        return (position, new_location), True

                    return (position, new_location), False  # A neighbor move was made

                else:
                    # else, there was some sort of error with the move,
                    # so do the turn from the beginning
                    return None, False

        # If the click was not made on a ped, return None, False
        return None, False

    def _turn(self, ped: Ped) -> Tuple[Optional[Coordinates], bool]:
        """Handle the turn of the current player.
        Returns the new location if the player made a turn successfully,
        None otherwise.
        In addition, returns True if the player made a hop move,
        False otherwise."""

        # Bring the possible moves of the selected ped from the board
        possible_moves = self._board.find_valid_moves(ped.get_location())

        # If there are no possible moves, prompt the player to select
        # another ped and do nothing
        if (possible_moves[NEIGHBOR_MOVES] == [] and
                possible_moves[HOP_MOVES] == []):
            if self._is_bot(self._current_player) == "Human":
                self._show_message("This ped has no possible move. Restarting turn.")
            return None, False

        # If the ped has possible moves, change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        # Highlight the possible moves (guaranteed to exist)
        self._gui.highlight_locations(self._gui.get_highlight_surface(),
                                      possible_moves)

        if self._is_bot(self._current_player) == "Bot":
            new_location = random.choice(possible_moves[NEIGHBOR_MOVES] +
                                         possible_moves[HOP_MOVES])
        else:
            # wait for a move
            new_location = self._wait_for_move(possible_moves)

        # If the player clicked on something other than a possible move,
        # unhighlight the possible moves and prompt the player to select
        # another ped. In addition, log it.
        if new_location is None:

            self._gui.unhighlight_surface(self._gui.get_highlight_surface())
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self._show_message("Please select a valid move. Restarting turn.")

            # If the click was not made on a ped, log that the player
            # changed his mind and return False
            self._log_game_data((self._is_bot(self._current_player) + (" " +
                                 str(self._players.index(
                                  self._current_player) + 1))),
                                message="changed his mind.")

            return None, False

        # The location was chosen, unhighlight the possible moves
        # and change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        self._gui.unhighlight_surface(self._gui.get_highlight_surface())

        try:
            # Move the ped to the selected location
            self._board.move_ped(ped, new_location)

        except Exception as e:
            print("Error: ", e)
            self._clear_log_file()
            sys.exit()

        # If the player made a hop move
        if new_location in possible_moves[HOP_MOVES]:
            return new_location, True

        # If the player made a neighbor move
        return new_location, False

    def _check_another_turn(self, visited: Set[Coordinates],
                            curr_location: Coordinates) -> \
            Optional[Coordinates]:
        """Check if the player can make another turn, from
        the current location, if it's not been visited before.
        The move can only be a hop move.
        If the player can make a move, return True and the new location.
        Otherwise, return None."""

        try:
            # Get the ped object from the board
            ped = self._board.get_ped_by_location(curr_location)

        except KeyError as e:
            print("Error: ", e)
            self._clear_log_file()
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

        # Making it that only hop moves are possible
        hop_moves_only = [possible_moves[HOP_MOVES]]

        # If the ped has possible moves, change the cursor
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        # Highlight the possible moves (guaranteed to exist)
        self._gui.highlight_locations(self._gui.get_highlight_surface(),
                                      hop_moves_only)

        # Showing a message on the screen about a possible additional move.
        message = (f"{self._is_bot(self._current_player)} "
                   f"{self._players.index(self._current_player) + 1} "
                   f"can make another turn!")

        if self._is_bot(self._current_player) == "Human":
            message += "Please select a move to continue, or click anywhere else " \
                       "to finish the turn."
        self._show_message(message, ANOTHER_TURN)

        if self._is_bot(self._current_player) == "Bot":
            new_location = random.choice(possible_moves[HOP_MOVES])

        else:
            # wait for a move
            new_location = self._wait_for_move(hop_moves_only)

        # If the player clicked on something other than a possible move,
        # in means that the player wants to finish the turn
        if new_location is None:

            self._gui.unhighlight_surface(self._gui.get_highlight_surface())
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            self._show_message("Finishing turn.")

            # log that the player finished his turn
            self._log_game_data((self._is_bot(self._current_player) + (" " +
                                 str(self._players.index(
                                  self._current_player) + 1))),
                                message="finished his turn.")

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
            self._clear_log_file()
            sys.exit()

        return new_location

    @staticmethod
    def _wait_for_move(possible_moves: List[List[Coordinates]]) \
            -> Optional[Coordinates]:
        """Wait for the player to make a move from the given possible moves.
        Returns the location of the move if it was made, None otherwise. """

        done_a_move = False

        while not done_a_move:
            for event in pygame.event.get():

                # Check if the player wants to quit the game
                if event.type == pygame.QUIT:
                    raise SystemExit
                    # pygame.quit()
                    # sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Get the position of the mouse
                    mouse_pos = pygame.mouse.get_pos()

                    # Check if the mouse click was made on one of
                    # the highlighted (possible moves) locations
                    for move_type in possible_moves:
                        for location in move_type:

                            cell_x = location[X_COORD]
                            cell_y = location[Y_COORD]

                            # Check if the click was made on the boundaries
                            # of the location
                            if ((cell_x - CELL_RADIUS) <= mouse_pos[X_COORD]
                                    <= (cell_x + CELL_RADIUS) and

                                    (cell_y - CELL_RADIUS) <=
                                    mouse_pos[Y_COORD] <= (cell_y + CELL_RADIUS)):

                                return location

                    # if the click was not made on a possible move, stop
                    # waiting for a move
                    done_a_move = True

        # if the player made invalid move, return None
        return None

    def _show_message(self, message: str, purpose: int = 0) -> None:
        """Show a temporary message on the screen."""

        if self._is_bot(self._current_player) == "Bot":
            message = "  " + message

        self._gui.show_message(message, purpose)

        if purpose != PLAYER_TURNS:
            # Wait for a short time before clearing the message
            if purpose == ANOTHER_TURN:
                pygame.time.delay(4500)  # 4.5 seconds

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

    @staticmethod
    def _log_game_data(player: str,
                       start_location: Optional[Coordinates] = None,
                       end_location: Optional[Coordinates] = None,
                       message: Optional[str] = None) -> None:
        """Construct log data dictionary."""

        log_data = {
            "player": player,
            "time": str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())),
            "from": str(start_location) if start_location is not None else "N/A",
            "to": str(end_location) if end_location is not None else "N/A",
            "message": message if message is not None else "N/A"
        }

        data = ('%s', log_data)
        logging.info(json.dumps(data))

    def _clear_log_file(self) -> None:
        """Clear the log file of the game."""

        with open(self.log_file_name, "w") as log_file:
            log_file.write("")

    def _delete_last_log_message(self) -> None:
        """Delete the last line from the log file."""

        # Read all lines from the file
        with open(self.log_file_name, 'r') as f:
            lines = f.readlines()

        # Remove the last line
        lines = lines[:-1]

        # Write the updated lines back to the file
        with open(self.log_file_name, 'w') as f:
            f.writelines(lines)

    @staticmethod
    def _is_bot(player: Union[Human, Bot]) -> str:
        """Check if the given player is a bot or a human player,
        and return the appropriate string. """

        if isinstance(player, Bot):
            return "Bot"
        else:
            return "Human"

    def view_game(self) -> None:

        """Asks the player if he wants to view the game.
        If yes, asks the player to enter the move number to view the board state,
        and showing him it.
        If no, does nothing."""

        actions, moves, winner = funcs.parse_data_from_file(self.log_file_name)

        if moves is None:
            print("No moves have been made in the game.")
            return None

        # Ask the user if he wants to view the game
        view_game = input("Do you want to view the game? (Y/N)\n")

        while view_game.upper() not in ["Y", "N"]:
            print("Invalid input. Please enter 'Y' or 'N'.")

            view_game = input("Do you want to view the game? (Y/N)\n")

        if view_game.upper() == "Y":

            if moves == 0:
                print("No moves have been made in the game.")
                return None

            # Display the board state at the specified move number.
            # Do it again and again and again until the user decides to exit.
            view_state = True
            while view_state:

                # Ask the user for input
                move_number = input(f"Enter move number to view board state: "
                                    f"1 - {len(moves)}\n")

                # Validate the input move number
                while (not (move_number.isdigit()) or int(move_number) > len(moves) or
                       int(move_number) <= 0):

                    print("Invalid move number. Please enter a positive integer "
                          "that is less than or equal to the total moves.")

                    move_number = input(f"Enter move number to view board state: "
                                        f"1 - {len(moves)}\n")

                move_number = int(move_number)

                # Getting the screen copies from the gui
                screen_copies = self._gui.get_screen_copies()

                # Display the board state at the specified move number
                if move_number <= len(screen_copies):
                    # Display the screen copy at the specified move number
                    self._gui.view_board_at_move(move_number)

                else:
                    print("Sorry, there are no screen copy available "
                          "for the selected move number.")

                # Ask the user if he wants to view another board state
                view_state_answer = input("Do you want to view another "
                                          "board state? (Y/N)\n")

                while view_state_answer.upper() not in ["Y", "N"]:
                    print("Invalid input. Please enter 'Y' or 'N'.")

                    view_state_answer = input("Do you want to view another "
                                              "board state? (Y/N)\n")

                if view_state_answer.upper() == "N":
                    view_state = False

        from history import GameHistory
        # After reviewing the game, ask the user if he wants to continue playing,
        # if the game is not over yet.

        continue_playing = input("Do you want to continue playing? (Y/N)\n")

        # If the user wants to continue playing
        if continue_playing.upper() == "Y":

            continue_playing = True
            while winner is None or not continue_playing:
                board = Board(len(self._players))
                gui = InitGui(len(self._players))

                history_game = GameHistory(self.log_file_name,
                                           board,
                                           gui,
                                           self._num_players,
                                           self._num_real_players,
                                           self._players.index(self._current_player),
                                           self._player_order)

                history_game.run()

                # Ask the user if he wants to view another board state
                view = input("Do you want to continue playing? (Y/N)\n")

                while view.upper() not in ["Y", "N"]:
                    print("Invalid input. Please enter 'Y' or 'N'.")

                    view = input("Do you want to continue playing? (Y/N)\n")

                if view.upper() == "N":
                    continue_playing = False

        return None

    def run(self) -> None:
        """Run the game."""

        pygame.mouse.set_cursor(*pygame.cursors.arrow)  # Set the cursor to an arrow

        # Creating a clock object to control the frame rate
        clock = pygame.time.Clock()

        winner = None

        # The main loop of the game
        while winner is None:
            try:
                pygame.display.flip()  # Update the display

                clock.tick(60)  # 60 frames per second

                winner = self.handle_events()  # Handle the events

                pygame.time.delay(1000)  # Delay for 1 second before the next move

            except SystemExit or KeyboardInterrupt or pygame.error or EOFError as e:

                # If the user closes the window, end the game
                raise e

        if winner is not None:
            # Show the winner message
            self._show_message(f"{self._is_bot(self._current_player)} {winner} wins!")

            # log that the player won
            self._log_game_data((self._is_bot(self._current_player) + (" " +
                                 str(self._players.index(
                                  self._current_player) + 1))),
                                message="Won the game!")
