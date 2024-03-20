import pygame
import sys
import math

# Constants
OUTER_COLOR = "#CDC8B1"
FRAME_COLOR = "#F6F3E7"

IN_BOARD_COLOR = "#CDAA7D"
BOARD_WIDTH = 480
BOARD_HEIGHT = 480

FRAME_HEIGHT = 540
FRAME_WIDTH = 910


class ChineseCheckersGame:

    def __init__(self):

        # Initialize the game
        pygame.init()
        self._screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))

        # make the window title
        pygame.display.set_caption("Chinese Checkers")

    def _create_board(self):

        # Draw the game board (hexagonal grid)
        center_x = FRAME_WIDTH // 2
        center_y = FRAME_HEIGHT // 2
        board_x0 = center_x - BOARD_WIDTH // 2
        board_y0 = center_y - BOARD_HEIGHT // 2

        # Draw the inner board
        pygame.draw.rect(self._screen, IN_BOARD_COLOR,
                         (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT))

        # Call the method to draw the hexagram
        self._draw_hexagram()

        # Draw the outer frame
        pygame.draw.rect(self._screen, OUTER_COLOR,
                         (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT), 4)

        # Adding the label "Chinese Checkers"
        font = pygame.font.SysFont("Courier", 32)
        label_text = "Chinese Checkers"

        # Creating the label surface, with the text,
        # smooth edges and black color
        label_surface = font.render(label_text, True, (0, 0, 0))

        # Getting the rectangle of the label surface,
        # such that the label is centered inside of it.
        label_rect = label_surface.get_rect(center=(FRAME_WIDTH // 2, 30))

        # Drawing th surface on the screen.
        self._screen.blit(label_surface, label_rect)

    def _draw_hexagram(self):

        cos_30 = math.cos(math.pi / 6)
        sin_30 = math.sin(math.pi / 6)
        size_ratio = 0.95

        # Calculate the center of the board, to ensure that the hexagram is drawn
        # in its center.

        # The reason why we use frame dimensions instead of board dimensions is because
        # the frame dimensions represent the total dimensions of the frame including
        # any borders or padding, while the board dimensions represent the inner dimensions
        # of the board excluding any borders or padding.
        center_y = FRAME_HEIGHT // 2
        center_x = FRAME_WIDTH // 2

        # Calculating the size of the hexagram based on the board size.
        # The hexagram will be board% of the frame size.
        # The size of the hexagram is the distance from its center to any of its outer points.
        hexagram_size = min(BOARD_WIDTH, BOARD_HEIGHT) * size_ratio / 2

        # Note: We are dividing the size by 2 because without it, it is just the distance
        # between one side of the hexagram to the other, and we want the distance to be
        # from it to the center.

        # Calculate the coordinates of the six points of the hexagram
        points = [
            (center_x, center_y - hexagram_size),  # Top
            (center_x + hexagram_size * cos_30, center_y - hexagram_size * sin_30),  # Top-right
            (center_x - hexagram_size * cos_30, center_y - hexagram_size * sin_30),  # Top-left
            (center_x, center_y + hexagram_size),  # Bottom
            (center_x + hexagram_size * cos_30, center_y + hexagram_size * sin_30),  # Bottom-right
            (center_x - hexagram_size * cos_30, center_y + hexagram_size * sin_30)  # Bottom-left
        ]

        # Defining the indices for creating the triangles.
        # Each tuple represents the points to be used for a triangle.
        indices = [(0, 4, 5), (3, 1, 2)]

        # Drawing the two triangles to form the hexagram.
        for i in range(2):
            triangle_points = [points[j] for j in indices[i]]
            pygame.draw.polygon(self._screen, (255, 255, 255), triangle_points)

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

            self._screen.fill(FRAME_COLOR)  # Set the background color
            self._create_board()

            pygame.display.flip()  # Update the display

            clock.tick(60)  # 60 frames per second


if __name__ == "__main__":

    game = ChineseCheckersGame()  # Creating the game object
    game.run()  # Running the game

