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

        pygame.draw.rect(self._screen, IN_BOARD_COLOR, (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT))

        # Call the method to draw the hexagram
        self._draw_hexagram()

        # Draw the outer frame
        pygame.draw.rect(self._screen, OUTER_COLOR, (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT), 4)

        # Add the label "Chinese Checkers"# Use the exact font and size
        font = pygame.font.SysFont("Courier", 32)  # Use the exact font and size
        label_text = "Chinese Checkers"
        label_surface = font.render(label_text, True, (0, 0, 0))  # Black color
        label_rect = label_surface.get_rect(center=(FRAME_WIDTH // 2, 30))  # Position the label

        self._screen.blit(label_surface, label_rect)

    def _draw_hexagram(self):

        cos_30 = math.cos(math.pi / 6)
        sin_30 = math.sin(math.pi / 6)
        size_ratio = 0.95

        center_y = FRAME_HEIGHT // 2
        center_x = FRAME_WIDTH // 2

        hexagram_size = min(BOARD_WIDTH, BOARD_HEIGHT) * size_ratio / 2

        points = [
            (center_x, center_y - hexagram_size),  # Top
            (center_x + hexagram_size * cos_30, center_y - hexagram_size * sin_30),  # Top-right
            (center_x - hexagram_size * cos_30, center_y - hexagram_size * sin_30),  # Top-left
            (center_x, center_y + hexagram_size),  # Bottom
            (center_x + hexagram_size * cos_30, center_y + hexagram_size * sin_30),  # Bottom-right
            (center_x - hexagram_size * cos_30, center_y + hexagram_size * sin_30)  # Bottom-left
        ]

        indices = [(0, 4, 5), (3, 1, 2)]

        for i in range(2):
            triangle_points = [points[j] for j in indices[i]]
            pygame.draw.polygon(self._screen, (255, 255, 255), triangle_points)

    def run(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self._screen.fill(FRAME_COLOR)
            self._create_board()

            pygame.display.flip()
            clock.tick(60)


if __name__ == "__main__":
    game = ChineseCheckersGame()
    game.run()

