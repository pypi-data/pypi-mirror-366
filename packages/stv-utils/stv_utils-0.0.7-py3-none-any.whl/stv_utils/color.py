def color():
    """
    Generates ANSI escape codes for terminal text styling.

    Returns:
        A list containing three dictionaries:
        1. `fg`: Foreground color codes.
        2. `bg`: Background color codes.
        3. `style`: Text style codes.

    Each dictionary maps a string name to its corresponding ANSI escape code.
    The `fg` and `bg` dictionaries include normal and bright versions of the following colors:
    - black
    - red
    - green
    - yellow
    - blue
    - magenta
    - cyan
    - white

    The `style` dictionary includes the following text styles:
    - bold
    - dim
    - italic
    - underline
    - blink
    - reverse
    - hidden
    - strikethrough
    - reset_all (resets all styles)

    Example usage:
        colors = color()
        fg_colors = colors[0]
        bg_colors = colors[1]
        text_styles = colors[2]

        print(f"{fg_colors['red']}This is red text{fg_colors['reset']}")
        print(f"{bg_colors['blue']}This text has a blue background{bg_colors['reset']}")
        print(f"{text_styles['bold']}This text is bold{text_styles['reset_all']}")
    """
    colors = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]

    fg = {
        **{Color: f"\033[{30 + i}m" for i, Color in enumerate(colors)},
        **{f"bright_{Color}": f"\033[{90 + i}m" for i, Color in enumerate(colors)},
        "reset": "\033[39m"
    }

    bg = {
        **{Color: f"\033[{40 + i}m" for i, Color in enumerate(colors)},
        **{f"bright_{Color}": f"\033[{100 + i}m" for i, Color in enumerate(colors)},
        "reset": "\033[49m"
    }

    style_mapping = [
        ("bold", 1), ("dim", 2), ("italic", 3), ("underline", 4),
        ("blink", 5), ("reverse", 7), ("hidden", 8), ("strikethrough", 9),
        ("reset_all", 0)
    ]
    style = {name: f"\033[{code}m" for name, code in style_mapping}

    return [fg, bg, style]
