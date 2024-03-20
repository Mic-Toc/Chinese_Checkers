import math
import tkinter as tk

from typing import Callable, Dict, List, Any, Tuple

OUTER_COLOR = "#CDC8B1"
FRAME_COLOR = "#ede8d5"

IN_BOARD_COLOR = "#CDAA7D"
BOARD_WIDTH = 480
BOARD_HEIGHT = 480

FRAME_HEIGHT = 540
FRAME_WIDTH = 910


class ChineseCheckersGui:

    def __init__(self) -> None:
        self._root = tk.Tk()
        self._root.title("Chinese Checkers")

        # making the window non-resizable
        self._root.resizable(False, False)

        self._buttons: Dict[str, tk.Button] = dict()

        self._create_board()

        self._draw_hexagram()
        # self._create_buttons()

    # def set_display(self, display_text: str) -> None:
    #     self._display_label["text"] = display_text

    def _create_board(self) -> None:

        # Creating a label widget
        # and add it to the root window
        self._top_label = tk.Label(self._root, text="Chinese Checkers", font=("Courier", 20))
        self._top_label.grid(row=0, column=0, padx=10, pady=24, columnspan=16)

        # self._canvas.create_polygon(50, 50, 50, 100, 100, 75, fill="green")

        # Create spacer labels
        left_spacer = tk.Label(self._root, width=10)
        right_spacer = tk.Label(self._root, width=10)

        # add the board frame to the root window
        # and add spacers to the left and right
        left_spacer.grid(row=1, column=0, rowspan=8)

        self._game_frame = tk.Frame(self._root, width=FRAME_WIDTH, height=FRAME_HEIGHT,
                                    border=1, bg=FRAME_COLOR, highlightthickness=3,
                                    highlightbackground=OUTER_COLOR)
        self._game_frame.grid(row=1, column=1, rowspan=8, columnspan=12, padx=20, sticky="nsew")

        right_spacer.grid(row=1, column=13, rowspan=8)

        # add a label to the board frame
        self._board_label = tk.Label(self._game_frame, bg=FRAME_COLOR)
        self._board_label.grid(row=0, column=0)

        # Creating a canvas widget
        self._canvas = tk.Canvas(self._game_frame, width=FRAME_WIDTH,
                                 height=FRAME_HEIGHT, bg=FRAME_COLOR)
        self._canvas.grid(columnspan=12, rowspan=6)

        # Calculating the center of the brown frame
        center_y = FRAME_HEIGHT / 2
        center_x = FRAME_WIDTH / 2

        # Setting the coordinates for the top-left corner of the board
        board_x0 = center_x - BOARD_WIDTH / 2
        board_y0 = center_y - BOARD_HEIGHT / 2

        # Drawing the rectangle
        self._canvas.create_rectangle(board_x0, board_y0, board_x0 + BOARD_WIDTH,
                                      board_y0 + BOARD_HEIGHT, fill=IN_BOARD_COLOR)

        # Create some margin at the bottom
        bottom_margin_label = tk.Label(self._root)
        bottom_margin_label.grid(row=9, column=0, pady=6)

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
        center_y = FRAME_HEIGHT / 2
        center_x = FRAME_WIDTH / 2

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

        # Drawing two triangles to form the hexagram.
        for i in range(2):
            triangle_points = [points[j] for j in indices[i]]
            self._canvas.create_polygon(*triangle_points, fill="white")

    def run(self) -> None:
        self._root.mainloop()


if __name__ == "__main__":
    ccg = ChineseCheckersGui()
    # ccg.set_display("TEST MODE")
    ccg.run()



