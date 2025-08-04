__version__ = "0.0.7"
__author__ = "星灿长风v(StarWindv)"

from .output import print
from .color import color
from .output_control import suppress_print, colorize
from .system_utils import is_ch, is_idle, system_check, system_clear

__all__ = [
    'print', 'color', 'suppress_print', 'colorize',
    'is_ch', 'is_idle', 'system_clear', 'system_check'
]