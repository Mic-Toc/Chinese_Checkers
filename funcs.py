import re
import webcolors


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
