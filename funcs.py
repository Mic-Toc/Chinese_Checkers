import json
import re
from typing import List, Tuple, Optional

import webcolors

Coordinates = Tuple[float, float]


def convert_to_rgb(color):
    """Convert a color of a certain type to RGB."""

    # If the color is already in RGB, return it as is
    if isinstance(color, tuple) and len(color) == 3 and re.match(r'^\d+$', str(color[0])):
        return color

    # If the color is in hexadecimal, convert it to RGB
    if isinstance(color, str) and re.match(r'^#[0-9a-fA-F]{6}$', color):

        # Remove the hash symbol from the hexadecimal color
        color = color[1:]

        # splitting the rest of the string into chunks of two characters.
        # Each chunk represents a color channel (red, green, blue) in hexadecimal.
        # Then we convert each chunk to an integer using the base 16.
        return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))

    # If the color is a recognized color name, convert it to RGB
    try:
        return webcolors.name_to_rgb(color)

    except ValueError:
        pass

    # If the color is not listed above, return default color
    return convert_to_rgb("#CDAA7D")


def rgba_to_name(color):
    """Get the name of a color from its RGB representation."""

    try:
        # Remove the alpha channel from the color
        color = color[:3]

    except TypeError:
        pass

    try:
        # If the color is a recognized color name, return it
        return webcolors.rgb_to_name(color)

    except ValueError or KeyError or IndexError:
        pass

    # If the color is not listed above, return it as a string of rgb or
    # rgba format, depending on the exception raised above.
    return str(color)


def make_transparent(color, alpha):
    """Make a color transparent by adding an alpha channel."""

    # If the color is already in RGBA, return it as is
    if isinstance(color, tuple) and len(color) == 4 and re.match(r'^\d+$', str(color[0])):
        return color

    # If the color is in RGB, add an alpha channel to it
    if isinstance(color, tuple) and len(color) == 3:
        return color + (alpha,)

    # If the color is not listed above, return default color
    return make_transparent(convert_to_rgb("#CDAA7D"), alpha)


def parse_data_from_file(log_file: str) -> \
        Tuple[List[str], List[Tuple[Coordinates, Coordinates]], Optional[bool]]:
    """Parse the board state from the file.
    Returns a list of tuples representing moves, each tuple contains
    start and end coordinates of the move."""

    actions = []
    winner = None
    moves = []

    with open(log_file, "r") as f:

        for line in f:

            # Splitting the line into parts
            parts = line.strip().split(":", 2)

            # Checking if everything is as expected in the file
            if len(parts) == 3 and parts[0] == 'INFO' and parts[1].startswith('root'):
                try:
                    data_list = json.loads(parts[2])

                    # Checking if everything is valid with the file
                    if len(data_list) == 2 and isinstance(data_list[1], dict):
                        move_format, data = data_list

                        # if there is a move in the data, append it to the moves list
                        if 'player' in data and 'from' in data and 'to' in data:
                            if data['from'] != "N/A" and data['to'] != "N/A":
                                action = "{} moved from: {} , to: {}".format(
                                    data['player'], data['from'], data['to'])

                                # Converting the string to tuple
                                data['from'] = eval(data['from'])
                                data['to'] = eval(data['to'])

                                # Appending the move to the moves list
                                move = (data['from'], data['to'])
                                moves.append(move)

                            elif 'message' in data and data['message'] != "N/A":
                                action = "{}: {}".format(data['player'], data['message'])

                                if "Won the game!" in data['message']:
                                    winner = True

                            # Appending the action to the actions list
                            actions.append(action)

                except json.JSONDecodeError:
                    print("Invalid log message format:", line)

    return actions, moves, winner
