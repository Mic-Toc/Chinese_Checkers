import sys

import pygame

from logic import ChineseCheckersGame

NUM_OF_PLAYERS = 1
NUM_OF_REAL_PLAYERS = 2


class GameOrLoad:
    """Class to run or load Chinese Checkers games"""

    def __init__(self) -> None:
        """Creating the game Chinese Checkers."""

        # Initialize the history of the games
        self._history = []

        running = True
        while running:

            play = input("Do you want to play a game? (Y/N): \n")

            while play.upper() not in ["Y", "N"]:
                print("Please enter a valid input.")
                play = input("Do you want to play the game? (Y/N): \n")

            if play.upper() == "Y":

                try:
                    self._play()

                except SystemExit or KeyboardInterrupt or pygame.error or EOFError:
                    print("Goodbye!")
                    pygame.quit()
                    continue

            else:

                view = input("Do you want to view the games history? (Y/N): \n")

                while view.upper() not in ["Y", "N"]:
                    print("Please enter a valid input.")
                    view = input("Do you want to view the games history? (Y/N): \n")

                if view.upper() == "Y":

                    try:
                        self._load()

                    except (SystemExit or KeyboardInterrupt or
                            pygame.error or EOFError):

                        print("Goodbye!")
                        pygame.quit()
                        continue

                else:
                    print("Goodbye!")
                    running = False

    def _play(self) -> None:
        """Main function to play the game."""

        # The user enters numbers of players in the game
        num_of_players = input("Enter number of players to play from: "
                               "[2, 3, 4, 6]\n")
        possible_num_of_players = [2, 3, 4, 6]

        while (not (num_of_players.isdigit() or
               int(num_of_players) not in possible_num_of_players)):
            print("Please enter a valid input.")

            # The user enters of players in the game
            num_of_players = input("Enter number of players to play from: "
                                   "[2, 3, 4, 6]\n")

        num_of_players = int(num_of_players)

        # The user enters number of players in the game
        num_of_real_players = input("Enter number of real players.\nThe number is "
                                    "expected to be within the number of players."
                                    "\nAt least include one real player\n")

        while (not (num_of_real_players.isdigit() or
               int(num_of_real_players) > num_of_players or
               int(num_of_real_players) <= 0)):
            print("Please enter a valid input.")

            # The user enters number of players in the game
            num_of_real_players = input("Enter number of real players.\nThe number is "
                                        "expected to be within the number of players."
                                        "\nAt least include one real player.\n")

        num_of_real_players = int(num_of_real_players)

        # Creating the game object
        self._game = ChineseCheckersGame(num_of_players, num_of_real_players)

        try:
            self._game.run()

        except SystemExit or KeyboardInterrupt or pygame.error or EOFError as e:
            print("Goodbye!")
            self._history.append(self._game)
            raise e

        # Saving the game to the history
        self._history.append(self._game)
        print("Game saved to history.")

    def _load(self) -> None:
        """Main function to load games."""

        if not self._history:
            print("No games to load.")
            sys.exit()

        for i in range(len(self._history)):
            print(f"{i + 1}: {self._history[i].log_file_name}")

        # The user chooses a game to load
        choice = input("Enter the number of the game you want to load.\n")

        while not (choice.isdigit() or
                   int(choice) > 0 or
                   int(choice) <= len(self._history)):

            print("Please enter a valid input.")

            # The user chooses a game to load
            choice = input("Enter the number of the game you want to load.\n")

        choice = int(choice)

        try:
            # Loading the game
            self._history[choice - 1].view_game()

        except SystemExit or KeyboardInterrupt or pygame.error or EOFError as e:
            print("Goodbye!")
            raise e


if __name__ == "__main__":

    try:
        GameOrLoad()

    except KeyboardInterrupt:
        print("Goodbye!")
        pygame.quit()
        sys.exit()
