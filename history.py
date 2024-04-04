from typing import Tuple, List, Union

import pygame

import funcs
from board import Board
from ped import Ped
from players import Human, Bot
from pygame_switch import InitGui
from logic import ChineseCheckersGame

Coordinates = Tuple[float, float]

X_COORD = 0
Y_COORD = 1

NEIGHBOR_MOVES = 0
HOP_MOVES = 1

PED_RADIUS = 4.7
CELL_RADIUS = 9.3

PLAYER_TURNS = 1
ANOTHER_TURN = 2

PLAYER_ORDER = [[4, 1, 3, 6, 2, 5],
                [4, 1, 3, 6],
                [4, 2, 6],
                [4, 1]]

FROM = 0
TO = 1


class GameHistory:
    """Class to store and view the history of the game Chinese Checkers."""

    def __init__(self, log_file: str,
                 board: Board, gui: InitGui,
                 num_players: int, num_real_players: int,
                 current_player_index: int, player_order: List[int]) -> None:
        """Creating the history of the game."""

        self._log_file = log_file
        self._board = board
        self._gui = gui

        self._players: List[Union[Human, Bot]] = []
        self._num_players = num_players
        self._num_real_players = num_real_players
        self._player_order = player_order

        self._initialize_players(current_player_index)

    def get_all_moves_from_file(self) -> List[Tuple[Coordinates, Coordinates]]:
        """Get all moves from the log file.
        Returns a list of tuples representing moves, each tuple contains
        start and end coordinates of the move."""

        actions, moves, winner = funcs.parse_data_from_file(self._log_file)

        return moves

    def _place_peds(self) -> List[Ped]:
        """Place the peds in their starting positions."""

        peds = []

        # Getting the colors of the players in the order they play,
        # taking into account the number of players
        playable_colors = self._gui.playable_colors()

        # Create the peds of the game by retrieving the positions
        # of the colored triangles from the gui.
        for color in playable_colors:
            for position in self._gui.get_color_positions_dict()[color]:
                new_ped = Ped(color, position)

                player_by_color = None
                try:
                    # Assign the ped to the player with the same color
                    player_by_color = self._get_player_by_color(color)

                except ValueError as e:
                    print(e)
                    pygame.quit()

                player_by_color.add_ped(new_ped)
                peds.append(new_ped)

        return peds

    def _initialize_players(self, current_player_index: int) -> None:
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

        self._current_player = self._players[current_player_index]

    def _get_player_by_color(self, color: str) -> Union[Human, Bot, None]:
        """Return the player with the given color."""

        for player in self._players:
            if player.get_color() == color:
                return player

        raise ValueError("No player with the color", color)

    def run(self) -> None:
        """Run the game history, from the last move played"""

        # Place the peds in their starting positions
        peds = self._place_peds()

        # Place the peds in their starting positions
        self._board.place_peds(peds)
        moves = self.get_all_moves_from_file()

        for move in moves:
            print(move[FROM], move[TO])
            self._board.move_ped(self._board.get_ped_by_location(move[FROM]), move[TO])

        pygame.mouse.set_cursor(*pygame.cursors.arrow)  # Set the cursor to an arrow

        # Creating a game object
        resume_game = ChineseCheckersGame(self._num_players, self._num_real_players,
                                          board=self._board, gui=self._gui,
                                          players=self._players,
                                          current_player=self._current_player,
                                          log_file=self._log_file)
        try:
            resume_game.run()  # Handle the events

        except SystemExit or KeyboardInterrupt or pygame.error or EOFError as e:
            raise e
