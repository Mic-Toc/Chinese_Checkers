import sys
import pygame
import peds
import board


class ChineseCheckersLogic:

    def __init__(self) -> None:
        self._board = board.Board()
        self._players = []
        self._current_player = None





    def run(self):

        # Creating a clock object to control the frame rate
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():

                # If the user clicks the close button, close the window
                # and stop the game from running
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


            pygame.display.flip()  # Update the display

            clock.tick(60)  # 60 frames per second
