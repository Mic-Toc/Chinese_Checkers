from typing import Tuple, List

import pygame
import sys
import math
import funcs

# Constants
OUTER_COLOR = "#CDC8B1"
FRAME_COLOR = "#f0e4bb"

BOARD_COLOR = "burlywood4"
BOARD_WIDTH = 480
BOARD_HEIGHT = 480

FRAME_HEIGHT = 540
FRAME_WIDTH = 910

COLORS = ["blue", "green", "red", "purple", "yellow", "white"]

X_COORD = 0
Y_COORD = 1


class ChineseCheckersGame:

    def __init__(self):

        # Initialize the game
        pygame.init()
        self._screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))

        # make the window title
        pygame.display.set_caption("Chinese Checkers")

        self._screen.fill(FRAME_COLOR)  # Set the background color
        self._create_board()
        # self._draw_hexagram()

    def _create_board(self):

        # Draw the game board (hexagonal grid)
        center_x = FRAME_WIDTH // 2
        center_y = FRAME_HEIGHT // 2
        board_x0 = center_x - BOARD_WIDTH // 2
        board_y0 = center_y - BOARD_HEIGHT // 2

        # Draw the inner board

        pygame.draw.rect(self._screen, BOARD_COLOR,
                         (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT))

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
        # so that the label is centered inside of it.
        label_rect = label_surface.get_rect(center=(FRAME_WIDTH // 2, 30))

        # Placing the text label on the screen.
        self._screen.blit(label_surface, label_rect)

        # Call the method to draw the hexagram
        self._draw_hexagram()

    def _draw_hexagram(self):

        cos_30 = math.cos(math.pi / 6)
        sin_30 = math.sin(math.pi / 6)
        size_ratio = 0.90  # The ratio of the hexagram size to the board
        radius_of_cells = 7.2  # The radius of the cells in the board

        # Calculate the center of the board, to ensure that the hexagram is drawn
        # in its center.

        # The reason why we use frame dimensions instead of board dimensions is because
        # the frame dimensions represent the total dimensions of the frame including
        # any borders or padding, while the board dimensions represent the inner dimensions
        # of the board excluding any borders or padding.
        center_y = FRAME_HEIGHT // 2
        center_x = FRAME_WIDTH // 2

        # Calculating the size of the hexagram based on the board size.
        # The hexagram will be inside the board.
        # The size of the hexagram is the distance from its center to any of its outer points.
        hexagram_size = (min(BOARD_WIDTH, BOARD_HEIGHT) * size_ratio) / 2

        # Note: We are dividing the size by 2 because without it, it is just the distance
        # between one side of the hexagram to the other, and we want the distance to be
        # from it to the center.

        # Calculate the coordinates of the six points of the hexagram
        points = [
            (center_x, center_y - hexagram_size),  # Top
            (center_x + hexagram_size * cos_30, center_y - hexagram_size * sin_30),  # Top-right
            (center_x + hexagram_size * cos_30, center_y + hexagram_size * sin_30),  # Bottom-right
            (center_x, center_y + hexagram_size),  # Bottom
            (center_x - hexagram_size * cos_30, center_y + hexagram_size * sin_30),  # Bottom-left
            (center_x - hexagram_size * cos_30, center_y - hexagram_size * sin_30)  # Top-left
        ]

        # Defining the indices for creating the triangles.
        # Each tuple represents the points to be used for a triangle.
        indices = [(0, 2, 4), (3, 1, 5)]

        board_color_rgb = funcs.convert_to_rgb(BOARD_COLOR)  # Converting the board color to rgb
        transparency = 255  # 0 is fully transparent, 255 is fully opaque

        hexagram_color = (*board_color_rgb[:3], transparency)

        # Creating a new surface with an alpha channel, so the hexagram
        # could be transparent
        temp_surface = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)

        # Draw two big triangles that form the hexagram on the temporary surface
        for i in range(len(indices)):
            triangle_points = [points[j] for j in indices[i]]
            pygame.draw.polygon(temp_surface, hexagram_color, triangle_points)

        # Doing this seperately so the cells will be drawn on top of the hexagram
        for q in range(len(points)):

            rotation_angle = 60

            self._draw_cells(temp_surface, points[q],
                             radius_of_cells, COLORS[q],
                             rotation_angle * q)

        self._draw_center_cells(temp_surface, radius_of_cells - 1, "brown")

        # Blit the temporary surface onto the screen surface
        self._screen.blit(temp_surface, (0, 0))

    @staticmethod
    def _rotate_point(point: Tuple[float, float],
                      center_x: float, center_y: float,
                      angle: int) -> Tuple[float, float]:

        # Normalizing the angle to the range [0, 360) degrees (ensuring only)
        # and then converting the angle to radians
        angle_rad = math.radians(angle % 360)

        # Translating the point so that the origin coords
        # are at the center of the triangle
        new_x = point[X_COORD] - center_x
        new_y = point[Y_COORD] - center_y

        # Rotating the point according to the formula for
        # rotating a point around the origin
        # [ x′ = x⋅cos(θ) − y⋅sin(θ) , y′ = x⋅sin(θ) + y⋅cos(θ) ]
        rotated_x = new_x * math.cos(angle_rad) - new_y * math.sin(angle_rad)
        rotated_y = new_x * math.sin(angle_rad) + new_y * math.cos(angle_rad)

        # Translating the point back to its original position
        new_x = rotated_x + center_x
        new_y = rotated_y + center_y

        return new_x, new_y

    def _draw_cells(self,
                    surface: pygame.Surface,
                    point: Tuple[float, float],
                    radius: float,
                    color: str,
                    angle: int) -> None:

        # Calculating an setting the distance between each cell and
        # setting the number of rows
        dist = 2 * radius + 17  # 17 is the padding between the cells
        rows = 4

        for i in range(rows):

            # number of cells in the current row
            cells_in_row = i + 1

            # Calculate the y coordinate of the current row
            y = point[Y_COORD] + i * dist

            for j in range(cells_in_row):

                # Calculate the x coordinate of the current cell
                x = (point[X_COORD] - (cells_in_row - 1) *
                     dist / 2 + j * dist)

                rotated_x, rotated_y = self._rotate_point((x, y),
                                                          point[X_COORD],
                                                          point[Y_COORD],
                                                          angle)

                # Draw the cell
                pygame.draw.circle(surface, color,
                                   (rotated_x, rotated_y), radius)

    @staticmethod
    def _draw_center_cells(surface: pygame.Surface, radius_center_cells: float,
                           color: str):

        # The distance between the centers of adjacent cells
        dist = 2 * radius_center_cells + 20  # 20 is the padding between the cells

        # The number of cells on each side of the hexagon
        cells_on_side = 5

        # The center of the hexagon that the center cells are forming is
        # also the center of the screen
        center_x = FRAME_WIDTH // 2
        center_y = FRAME_HEIGHT // 2

        for i in range(cells_on_side):
            for j in range(cells_on_side):
                # Calculate the x and y coordinates of the current cell
                x = center_x - (
                            cells_on_side - 1) * dist / 2 + j * dist + i * dist / 2
                y = center_y - (cells_on_side - 1) * dist / 2 + i * dist

                # Draw the cell
                pygame.draw.circle(surface, color, (int(x), int(y)),
                                   int(radius_center_cells))


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


def test_rotation():
    center_x = 100
    center_y = 100
    point = (150, 100)  # Point to be rotated
    angle = 90  # Rotation angle in degrees

    # Test rotation
    rotated_point = ChineseCheckersGame._rotate_point(point, center_x, center_y, angle)
    print(rotated_point)


def test_triangle_placement():
    center_x = 100
    center_y = 100
    hexagram_size = 50
    cos_30 = math.cos(math.pi / 6)
    sin_30 = math.sin(math.pi / 6)

    points = [
        (center_x, center_y - hexagram_size),  # Top
        (center_x + hexagram_size * cos_30, center_y - hexagram_size * sin_30),
        # Top-right
        (center_x - hexagram_size * cos_30, center_y - hexagram_size * sin_30),
        # Top-left
        (center_x, center_y + hexagram_size),  # Bottom
        (center_x + hexagram_size * cos_30, center_y + hexagram_size * sin_30),
        # Bottom-right
        (center_x - hexagram_size * cos_30, center_y + hexagram_size * sin_30)
        # Bottom-left
    ]

    for i, triangle_points in enumerate([(0, 4, 5), (3, 1, 2)]):
        print(f"Triangle {i + 1}:")

        # Calculate the center of the current triangle
        triangle_center_x = sum(
            points[index][0] for index in triangle_points) / 3
        triangle_center_y = sum(
            points[index][1] for index in triangle_points) / 3

        for point_index in triangle_points:
            # Rotate the current point around the center of the triangle
            rotated_point = ChineseCheckersGame._rotate_point(points[point_index],
                                          triangle_center_x, triangle_center_y,
                                          i * -60)
            print(rotated_point)


if __name__ == "__main__":

    game = ChineseCheckersGame()  # Creating the game object
    # test_rotation()  # Testing the rotation function
    test_triangle_placement()  # Testing the triangle placement
    game.run()  # Running the game




