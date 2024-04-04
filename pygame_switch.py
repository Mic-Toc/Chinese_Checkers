from typing import Tuple, List, Dict, Optional

import pygame
import math

import funcs

from ped import Ped

# Constants
OUTER_COLOR = "#CDC8B1"
FRAME_COLOR = "#f0e4bb"

BOARD_COLOR = "burlywood4"

CENTER_CELLS_COLOR = "darkred"

FRAME_HEIGHT = 590
FRAME_WIDTH = 930

BOARD_HEIGHT = 0.95 * FRAME_HEIGHT
BOARD_WIDTH = 0.6 * FRAME_WIDTH

COLORS = ["Aqua", "green", "grey", "purple", "yellow", "lavenderblush"]

rgb_colors = list(map(lambda x: funcs.convert_to_rgb(x), COLORS))

# Add transparency to the colors (x[:3] is the RGB part of the color,
# x[3] is the alpha channel).
# If the color has an alpha channel, it's set to 0.7 times the alpha channel value
# If the color has no alpha channel, it's set to 180 (the default is 255).
TRANSPARENT_COLORS = list(map(lambda x: (*x[:3], (180 if len(x) == 3 else 0.7 * x[3])),
                              rgb_colors))

HIGHLIGHT_COLOR = (255, 212, 78)  # Yellow  # 101

Coordinates = Tuple[float, float]

X_COORD = 0
Y_COORD = 1

PLAYER_TURNS = 1
ANOTHER_TURN = 2

PLAYER_ORDER = [[4, 1, 3, 6, 2, 5],
                [4, 1, 3, 6],
                [4, 2, 6],
                [4, 1]]

DEFAULT_CAPTION = "Chinese Checkers. If it's a bot's turn, " \
                  "drag your mouse to view the bot's moves. "
VIEWING_CAPTION = "Viewing the chosen move. Close the window to quit."


class InitGui:
    """Class to initialize the GUI of the game Chinese Checkers."""

    def __init__(self, num_players: int) -> None:
        """Initialize the GUI of the game Chinese Checkers."""

        # Initialize the game
        pygame.init()
        self._screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))

        # Creating a new surface with an alpha channel, so the hexagram
        # could be transparent
        self._temp_surface = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT),
                                            pygame.SRCALPHA)

        # Creating a new surface for the highlighting
        self._highlight_surface = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT),
                                                 pygame.SRCALPHA)

        # make the window title
        pygame.display.set_caption(DEFAULT_CAPTION)

        self._font = pygame.font.SysFont("Courier", 18)

        self._start_new_game(num_players)

        # Setting a previous state property to revert the
        # current state when needed
        self._previous_state_highlight = None
        self._previous_state_message = None

    def _start_new_game(self, num_players: int) -> None:
        """Start the game."""

        self._num_players = num_players  # Number of players

        for order in PLAYER_ORDER:
            if len(order) == num_players:
                self._player_order = order
                break

        self._screen.fill(FRAME_COLOR)  # Set the background color

        # Dictionary to store the positions of the cells in
        # outer triangles by color.
        self._color_positions: Dict[str, List[Coordinates]] = {}

        # List to store the positions of the cells in
        # the center of the board.
        self._center_positions: List[Coordinates] = []

        # Creating a list to store the screen copies for reviewing the game
        # after it's finished, and even to start from where it was left.
        self._screen_copies: List[pygame.Surface] = []

        # determine the number of players
        self.create_board()  # Create the game board

    def create_board(self) -> None:
        """Creating or updating the game board, depending on the state of the game."""

        # Draw the game board
        center_x = FRAME_WIDTH / 2
        center_y = FRAME_HEIGHT / 2
        board_x0 = center_x - BOARD_WIDTH / 2
        board_y0 = center_y - BOARD_HEIGHT / 2

        # Draw the inner board
        pygame.draw.rect(self._screen, BOARD_COLOR,
                         (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT))

        # Draw the outer frame
        pygame.draw.rect(self._screen, OUTER_COLOR,
                         (board_x0, board_y0, BOARD_WIDTH, BOARD_HEIGHT), 7)

        # Call the method to draw the hexagram
        self._draw_hexagram()

        # Update the display
        pygame.display.flip()

    def _draw_hexagram(self) -> None:
        """Draw the hexagram, which is the shape of the board."""

        cos_30 = math.cos(math.pi / 6)
        sin_30 = math.sin(math.pi / 6)
        size_ratio = 0.90  # The ratio of the hexagram size to the board
        self._radius_cells = 9.3  # The radius of the cells in the board
        self._radius_peds = 6.7  # The radius of the center cells in the board

        # The distance between the centers of adjacent cells in
        # the center of the board.

        # 15 is the padding between the cells
        self._cells_dist = 2 * self._radius_cells + 15

        # Calculate the center of the board, to ensure that the hexagram is drawn
        # in its center.

        # The reason why we use frame dimensions instead of board dimensions is because
        # the frame dimensions represent the total dimensions of the frame including
        # any borders or padding, while the board dimensions represent the
        # inner dimensions
        # of the board excluding any borders or padding.
        center_y = FRAME_HEIGHT / 2
        center_x = FRAME_WIDTH / 2

        # Calculating the size of the hexagram based on the board size.
        # The hexagram will be inside the board.
        # The size of the hexagram is the distance from its center to
        # any of its outer points.
        hexagram_size = (min(BOARD_WIDTH, BOARD_HEIGHT) * size_ratio) / 2

        # Note: We are dividing the size by 2 because without it, it is just the distance
        # between one side of the hexagram to the other, and we want the distance to be
        # from it to the center.

        # Calculate the coordinates of the six points of the hexagram
        points = [
            (center_x, center_y - hexagram_size),  # Top

            # Top-right
            (center_x + hexagram_size * cos_30, center_y - hexagram_size * sin_30),

            # Bottom-right
            (center_x + hexagram_size * cos_30, center_y + hexagram_size * sin_30),

            (center_x, center_y + hexagram_size),  # Bottom

            # Bottom-left
            (center_x - hexagram_size * cos_30, center_y + hexagram_size * sin_30),

            # Top-left
            (center_x - hexagram_size * cos_30, center_y - hexagram_size * sin_30)
        ]

        # Defining the indices for creating the triangles.
        # Each tuple represents the points to be used for a triangle.
        indices = [(0, 2, 4), (3, 1, 5)]

        # Converting the board color to rgb
        board_color_rgb = funcs.convert_to_rgb(BOARD_COLOR)
        transparency = 255  # 0 is fully transparent, 255 is fully opaque

        hexagram_color = (*board_color_rgb[:3], transparency)

        # Draw two big triangles that form the hexagram on the temporary surface
        for i in range(len(indices)):
            triangle_points = [(points[j]) for j in indices[i]]
            pygame.draw.polygon(self._temp_surface, hexagram_color, triangle_points)

        # Doing this separately so the cells will be drawn on top of the hexagram
        for q in range(len(points)):

            rotation_angle = 60

            if q == 2 or q == 5:  # for adjusting only purposes
                self._draw_outer_cells(self._temp_surface, points[q], self._radius_cells,
                                       TRANSPARENT_COLORS[q], rotation_angle * q,
                                       True)

            else:
                self._draw_outer_cells(self._temp_surface, points[q], self._radius_cells,
                                       TRANSPARENT_COLORS[q], rotation_angle * q,
                                       False)

        # Draw the 61 center cells
        self._draw_center_cells(self._temp_surface, self._radius_cells,
                                CENTER_CELLS_COLOR)

        # Place the peds in the outer cells
        self._place_peds(self._temp_surface, self._radius_peds)

        # Blit the temporary surface onto the screen surface
        self._screen.blit(self._temp_surface, (0, 0))

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

    def _draw_outer_cells(self,
                          surface: pygame.Surface,
                          point: Tuple[float, float],
                          radius: float,
                          color: Tuple,
                          angle: int,
                          adjust: bool) -> None:

        rows = 4
        cells_dist = self._cells_dist

        for i in range(rows):

            # number of cells in the current row
            cells_in_row = i + 1

            # Calculate the y coordinate of the current row
            y = point[Y_COORD] + i * cells_dist - 2  # 4 is the padding between the rows

            for j in range(cells_in_row):

                # Calculate the x coordinate of the current cell
                # all the ifs below is for adjustments only
                x = (point[X_COORD] - (cells_in_row - 1) *
                     (cells_dist + 5) / 2 + j * (cells_dist + 3))

                if j < cells_in_row // 2:
                    x = (point[X_COORD] - (cells_in_row - 1) *
                         (cells_dist + 2) / 2 + j * (cells_dist + 3))

                elif j == cells_in_row // 2 and j % 2 != 0:
                    x = (point[X_COORD] - (cells_in_row - 1) *
                         (cells_dist + 4) / 2 + j * (cells_dist + 3))

                elif adjust:
                    x = (point[X_COORD] - (cells_in_row - 1) *
                         (cells_dist + 4) / 2 + j * (cells_dist + 3))

                # Rotate the point
                rotated_x, rotated_y = self._rotate_point((x, y),
                                                          point[X_COORD],
                                                          point[Y_COORD],
                                                          angle)

                # (Actually it doesn't matter to convert the color to a name,
                # I'm doing it so the dictionary will be prettier to see)
                # Getting the color name without a transparency value
                color_name = funcs.rgba_to_name(color)

                # Add the position of the cell to the dictionary of positions,
                # at the key of the color of the cell.
                if color_name not in self._color_positions:
                    self._color_positions[color_name] = [(rotated_x, rotated_y)]

                else:
                    self._color_positions[color_name].append((rotated_x, rotated_y))

                # Draw the cell
                pygame.draw.circle(surface, color,
                                   (rotated_x, rotated_y), radius)

    def _draw_center_cells(self, surface: pygame.Surface,
                           radius_center_cells: float, color: str) -> None:

        # The center of the hexagon that the center cells are forming is
        # also the center of the screen
        center_x = FRAME_WIDTH / 2
        center_y = FRAME_HEIGHT / 2

        # The number of cells on each side of the hexagon
        rows = 9

        for i in range(rows):

            # The number of cells in the current row
            cells_in_row = 5 + i
            if i > rows // 2:
                cells_in_row = 5 + rows - i - 1

            # Calculate the y coordinate of the current row
            # (We deduct from the dest to make the hexagon more proportional)
            y = (center_y - (rows - 1) * self._cells_dist / 2 +
                 i * (self._cells_dist - 3) + 12)

            for j in range(cells_in_row):

                # Calculate the x coordinate of the current cell.
                # Appending 3 to the dist to make the hexagon more proportional
                # in the x axis.
                x = (center_x - (cells_in_row - 1) * self._cells_dist / 2 +
                     j * self._cells_dist)

                # if j < cells_in_row // 2:
                #     x = (center_x - (cells_in_row - 1) * self._cells_dist / 2 +
                #          j * self._cells_dist - 4)

                # Appending the coordinates to the list of center positions
                self._center_positions.append((x, y))

                # Draw the cell
                pygame.draw.circle(surface, color, (int(x), int(y)),
                                   radius_center_cells)

    def playable_colors(self) -> List[str]:
        """Return the colors of the players in the order they play."""
        playable_colors = []

        for num in self._player_order:
            playable_colors.append(list(self._color_positions.keys())[num-1])
        return playable_colors

    def _place_peds(self, surface: pygame.Surface, radius_peds: float) -> None:
        """Place the peds in the initial positions at the start of the game."""

        # Get the colors of the players in the order they play
        playable_colors = self.playable_colors()

        for color in playable_colors:
            for position in self._color_positions[color]:

                # Draw the ped inside the position of the cell
                # (because its radius is smaller than the cell's one),
                # and with the color of the cell but full opaque
                try:
                    pygame.draw.circle(surface, color,
                                       (position[X_COORD], position[Y_COORD]),
                                       radius_peds)

                    # Adding a small frame around the circle
                    if color != "black":
                        pygame.draw.circle(surface, "black",
                                           (position[X_COORD], position[Y_COORD]),
                                           radius_peds, 1)

                    else:
                        pygame.draw.circle(surface, "white",
                                           (position[X_COORD], position[Y_COORD]),
                                           radius_peds, 1)

                except Exception as e:
                    print(e)

        # update the screen
        pygame.display.flip()

    def update_ped(self, surface: pygame.Surface,
                   old_position: Coordinates, updated_ped: Ped) -> None:
        """Update the position of the ped on the screen according to the
        given position."""

        # Clear the screen
        surface.fill((0, 0, 0, 0))

        removed = False
        # Remove the ped from its previous position:

        # if the ped was in the outer triangles
        for color, positions in self._color_positions.items():
            if old_position in positions:

                pygame.draw.circle(surface, color,
                                   old_position, self._radius_cells)
                removed = True
                break

        # if the ped was in the center hexagon
        if not removed:
            pygame.draw.circle(surface, CENTER_CELLS_COLOR,
                               old_position, self._radius_cells)

        # Draw the peds in their new positions
        try:
            pygame.draw.circle(surface, updated_ped.get_color(),
                               updated_ped.get_location(), self._radius_peds)

            # Adding a small frame around the circle
            if updated_ped.get_color() != "black":
                pygame.draw.circle(surface, "black",
                                   updated_ped.get_location(),
                                   self._radius_peds, 1)

            else:
                pygame.draw.circle(surface, "white",
                                   updated_ped.get_location(),
                                   self._radius_peds, 1)

        except Exception as e:
            print(e)

        # Blit the surface on the screen
        self._screen.blit(surface, (0, 0))

        # Update the screen
        pygame.display.flip()

        # Append the current state to the list of previous states
        self._screen_copies.append(self._screen.copy())

    def highlight_locations(self, surface: pygame.Surface,
                            positions: List[List[Coordinates]]) -> None:
        """Highlight the given positions on the screen."""

        # Store the previous surface
        self._previous_state_highlight = self._screen.copy()

        # Clear the previous highlights
        surface.fill((0, 0, 0, 0))

        for move_types in positions:
            for position in move_types:
                pygame.draw.circle(surface, HIGHLIGHT_COLOR,
                                   (position[X_COORD], position[Y_COORD]),
                                   self._radius_cells, 3)

        # Blit the highlight surface on the temp surface
        self._screen.blit(surface, (0, 0))
        pygame.display.flip()  # Update the display

    def unhighlight_surface(self, surface: pygame.Surface) -> None:
        """Unhighlight the possible moves in the given surface."""

        # Clear the previous highlights
        surface.fill((0, 0, 0, 0))

        # # Blit the highlight surface on the temp surface
        # self._temp_surface.blit(surface, (0, 0))

        # Restore the previous state, if needed
        if self._previous_state_highlight is not None:
            self._screen.blit(self._previous_state_highlight, (0, 0))
            pygame.display.flip()  # Update the display
            self._previous_state_highlight = None  # Reset the previous state

        pygame.display.flip()  # Update the display

    def show_message(self, message: str, purpose: int = 0) -> None:
        """Showing a message to the user."""

        self._previous_state_message = self._screen.copy()

        # Split the message into lines, can be too long
        whole_text = []
        for elem in message.split("\n"):
            whole_text.append(self._font.render(elem, True, (0, 0, 0)))

        # get the whole text height and width

        # Getting the maximum width, to be used as the width of the surface
        text_width = max(text.get_width() for text in whole_text)

        # Getting the sum of the line heights, to be used as the height
        # of the surface
        text_height = sum(text.get_height() for text in whole_text)

        # Create a surface to display the text on, add a small margin
        text_surface = pygame.Surface((text_width + 5, text_height + 5))
        text_surface.fill((255, 255, 255))  # Fill the surface with white

        y_offset = 0
        for line in whole_text:

            # Draw the text on the surface, horizontally centered
            text_surface.blit(line, (
                text_surface.get_width() / 2 - line.get_width() / 2, y_offset))

            # Update the y_offset, to draw the next line below the current one
            y_offset += line.get_height()

        # Blit the surface on the screen
        if purpose == PLAYER_TURNS:

            self._screen.blit(text_surface, ((FRAME_WIDTH + BOARD_WIDTH) / 2,
                                             FRAME_HEIGHT / 4))

        else:

            self._screen.blit(text_surface,
                              (FRAME_WIDTH / 2 - text_surface.get_width() / 2,
                               FRAME_HEIGHT / 2 - text_surface.get_height() / 2))

        pygame.display.flip()  # Update the display

    def clear_message(self) -> None:
        """Clearing the message from the screen."""

        # Restore the previous state, if needed
        if self._previous_state_message is not None:
            self._screen.blit(self._previous_state_message, (0, 0))
            pygame.display.flip()  # Update the display
            self._previous_state_message = None  # Reset the previous state

    def is_in_opposite_home(self, ped: Ped) -> bool:
        """Check if the given ped is in the home of
         his matching opposite corner."""

        ped_color = ped.get_color()
        home_index = list(self._color_positions.keys()).index(ped_color) + 1
        # color_index_by_order = self._player_order[color_index - 1]

        # there is 3 (len(PLAYER_ORDER[0]) / 2) because the number of
        # triangles in a hexagram is always 6, and the opposite
        # triangle is 3 places to step from the current.
        # print("home_index: ", home_index)
        opposite_index = home_index - len(PLAYER_ORDER[0]) // 2  # 3
        if opposite_index <= 0:
            opposite_index += 6

        # find the matching opposite home locations
        opposite_home_locations = list(self._color_positions.values())[opposite_index-1]
        # print("opposite_home_color: ", opposite_home_locations)

        # if the location of the given ped is in the matching opposite home,
        # return true, otherwise false.
        return ped.get_location() in opposite_home_locations

    def color_of_opposite_home(self, location: Coordinates) -> Optional[str]:
        """Return the color of the foreign home if the given location is in it,
        None otherwise."""

        for color, positions in self._color_positions.items():
            if location in positions:
                return color

        return None

    def view_board_at_move(self, move_number: int) -> None:
        """Display the board state at the specified move number."""

        if move_number <= len(self._screen_copies):

            # Initialize pygame, because it is not initialized yet when we
            # are viewing the game.
            pygame.init()

            try:
                # Clear the screen
                self._screen.fill((0, 0, 0))

            except pygame.error:
                print("The display surface has been quit. "
                      "Recreating the display surface.")

                # Recreate the display surface
                self._screen = pygame.display.set_mode((FRAME_WIDTH, FRAME_HEIGHT))
                self._screen.fill((0, 0, 0))

            # Set the window title
            pygame.display.set_caption(VIEWING_CAPTION)

            # Blit the screen copy onto the main screen
            self._screen.blit(self._screen_copies[move_number - 1], (0, 0))

            # Update the display
            pygame.display.flip()

            # Keep the screen open until the user closes it
            running = True
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        raise SystemExit

        else:
            print("No screen copy available for the selected move number.")

    def get_color_positions_dict(self) -> Dict[str, List[Coordinates]]:
        return self._color_positions

    def get_center_positions_list(self) -> List[Coordinates]:
        return self._center_positions

    def get_cell_distance(self) -> float:
        return self._cells_dist

    def get_temp_surface(self) -> pygame.Surface:
        return self._temp_surface

    def get_highlight_surface(self) -> pygame.Surface:
        return self._highlight_surface

    def get_screen_copies(self) -> List[pygame.Surface]:
        return self._screen_copies
