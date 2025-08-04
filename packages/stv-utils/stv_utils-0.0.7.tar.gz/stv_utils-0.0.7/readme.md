# stv_utils - Python Utility Library

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-0.0.7-lightgrey)

`stv_utils` is a Python utility library containing commonly used functions, particularly useful for projects requiring terminal output beautification, system environment detection, and console operations.

## Features

### 🎨 Terminal Colors & Styles
- Generate ANSI escape codes
- Control foreground, background colors and text styles
- Includes normal and bright versions of colors

### 🌈 Colorized Output
- Enhanced print function supports hex color codes
- Automatically converts hex colors to the closest 256-color ANSI codes
- Maintains all parameters of native print function

### 🎭 Output Control
- Colorize output based on specific string prefixes
- Suppress output of specific lines by prefix
- Decorators simplify output control

### 🖥️ System Utilities
- Detect Chinese language environment
- Identify operating system type
- Check if running in IDLE environment
- Cross-platform console clearing function

## Installation

```bash
pip install stv_utils
```

## Quick Start

### Basic Color Control
```python
from stv_utils import color

# Get color and style dictionaries
fg, bg, styles = color()

print(f"{fg['red']}Red text{styles['reset_all']}")
print(f"{bg['blue']}Blue background{styles['reset_all']}")
print(f"{styles['bold']}Bold text{styles['reset_all']}")
```

### Colorized Output
```python
from stv_utils import print

# Using hex color codes
print(";#ff0000;This is red text")
print(";#00ff00;This is green text")
print(";#0000ff;This is blue text")
```

### Output Control
```python
from stv_utils import colorize, suppress_print

@colorize(color_code="\033[93m")  # Yellow
def my_function():
    print("|> This line will be colored")
    print("This line remains default color")

@suppress_print(start_str="|>")
def my_quiet_function():
    print("|> This line will be suppressed")
    print("This line will display normally")
```

### System Utilities
```python
from stv_utils import is_ch, system_check, system_clear

# Detect Chinese environment
if is_ch():
    print("Chinese environment detected")

# Get OS information
print(f"Current system: {system_check(verbose=True)}")

# Clear screen
system_clear()
```

## Module Overview

### color.py
Provides ANSI escape sequence generation:
- 8 basic colors (black, red, green, yellow, blue, magenta, cyan, white) and their bright versions
- 9 text styles (bold, dim, italic, underline, blink, reverse, hidden, strikethrough, reset_all)

### output.py
Extends Python's built-in print function to support hex color codes in `;#xxxxxx;` format, automatically converting to the closest 256-color ANSI code.

### output_control.py
Provides output control capabilities:
- `ColorizedOutput`: Colorize text with specific prefixes
- `SuppressedOutput`: Suppress text output with specific prefixes
- `colorize` decorator: Simplify function output coloring
- `suppress_print` decorator: Simplify function output suppression

### system_utils.py
System utility functions:
- `is_ch()`: Detect Chinese language environment
- `system_check()`: Get operating system information
- `is_idle()`: Check if running in IDLE environment
- `system_clear()`: Cross-platform screen clearing function

## Contributing

Contributions are welcome! Please submit issues or pull requests via GitHub:
https://github.com/StarWindv/stv_utils

## License

This project is licensed under the MIT License.