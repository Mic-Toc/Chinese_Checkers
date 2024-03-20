import re
import webcolors


def convert_to_rgb(hex_color):
    """Convert a color of a certain type to RGB."""

    # If the color is already in RGB, return it as is
    if isinstance(hex_color, tuple) and len(hex_color) == 3:
        return hex_color

    # If the color is in hexadecimal, convert it to RGB
    if isinstance(hex_color, str) and re.match(r'^#[0-9a-fA-F]{6}$', hex_color):

        # Remove the hash symbol from the hexadecimal color
        hex_color = hex_color[1:]

        # splitting the rest of the string into chunks of two characters.
        # Each chunk represents a color channel (red, green, blue) in hexadecimal.
        # Then we convert each chunk to an integer using the base 16.
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # If the color is a recognized color name, convert it to RGB
    try:
        return webcolors.name_to_rgb(hex_color)

    except ValueError:
        pass

    # If the color is not listed above, return default color
    return convert_to_rgb("#CDAA7D")
