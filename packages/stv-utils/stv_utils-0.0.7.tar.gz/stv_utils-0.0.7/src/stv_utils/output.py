import re
import sys


def _hex_to_rgb(hex_code):
    """
    Convert a hex color code to an RGB tuple.

    Args:
        hex_code (str): A hex color code, e.g., '#1a2b3c'.

    Returns:
        tuple: A tuple of three integers representing the RGB values.

    Raises:
        ValueError: If the hex code is not of length 6.
    """
    hex_code = hex_code.lstrip('#')
    if len(hex_code) != 6:
        raise ValueError(f"The hex code's length must be 6.(got `{len(hex_code)}`)")
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_256(r, g, b):
    """
    Convert RGB values to the closest 256-color ANSI code.

    Args:
        r (int): Red component of the color.
        g (int): Green component of the color.
        b (int): Blue component of the color.

    Returns:
        int: The closest 256-color ANSI code.
    """
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232

    def normalize(x):
        return max(0, min(5, round(x / 255 * 5)))

    r_idx = normalize(r)
    g_idx = normalize(g)
    b_idx = normalize(b)
    return 16 + 36 * r_idx + 6 * g_idx + b_idx


def _get_closest_256_color(hex_code):
    """
    Get the closest 256-color ANSI code for a given hex color code.

    Args:
        hex_code (str): A hex color code, e.g., '#1a2b3c'.

    Returns:
        int or None: The closest 256-color ANSI code, or None if the hex code is invalid.
    """
    try:
        r, g, b = _hex_to_rgb(hex_code)
        return _rgb_to_256(r, g, b)
    except ValueError:
        return None


def print(*values, sep=' ', end='\n', file=sys.stdout, flush=False):
    """
    Print the values to the stream, converting hex color codes to ANSI color codes.
    The signature is exactly the same as the built-in `print` function in Python.

    Args:
        *values: Variable length argument list to be printed.
        sep (str, optional): String inserted between values, default is a space.
        end (str, optional): String appended after the last value, default is a newline.
        file (file-like object, optional): Stream to print to, default is sys.stdout.
        flush (bool, optional): Whether to forcibly flush the stream, default is False.
    """
    ansi_reset = "\033[0m"
    full_string = sep.join(str(v) + "\x1b[39m" for v in values)

    pattern = re.compile(r';(#?[0-9a-fA-F]{6});')

    def replace_color(match):
        hex_color = match.group(1)
        color_code = _get_closest_256_color(hex_color)
        if color_code is not None:
            return f"\033[38;5;{color_code}m"
        else:
            return match.group(0)

    final_output = pattern.sub(replace_color, full_string)

    file.write(final_output + ansi_reset + end)

    if flush:
        file.flush()
