import locale
import os
import platform
import sys


def is_ch():
    """
    Determine if the current system is in a Chinese environment.
    Check if "Chinese" is present in the system localization settings to identify the environment.

    Args: None

    Returns:
      bool: Returns True if the system is in a Chinese environment, otherwise returns False.
    """
    return 'Chinese' in str(locale.getlocale())


def system_check(verbose=False, more_verbose=False):
    """
    Check system information and return the system name with different levels of detail.
    Control the return result's detail level based on the passed parameters `verbose` and `more_verbose`:
    - Return simplified mapping of OS name when `verbose=True`;
    - Return original system identifier when `more_verbose=True`;
    - Return boolean indicating if it's Windows when both parameters are not passed (default).

    Args:
      verbose      (bool): Whether to return a simplified OS name. Default is False.
      more_verbose (bool): Whether to return the original system identifier. Default is False.

    Returns:
      Union[str, bool]: System name (string type; returns "Windows", etc. for Windows; returns boolean if no parameters are passed).
    """
    os_name_map = {
        "Windows": "Windows",
        "Linux": "Linux",
        "Darwin": "macOS"
    }
    system_id = platform.system()
    if verbose:
        return os_name_map.get(system_id, "Unknown")
    elif more_verbose:
        return system_id
    else:
        return system_id == "Windows"


def is_idle():
    """
    Determine if the current Python environment is the `IDLE` integrated development environment.
    Check if the 'idlelib' module exists in `sys.modules` to determine if running in IDLE.

    Args: None

    Returns:
      bool: Returns True if 'idlelib' is in `sys.modules`, otherwise returns False.
    """
    return 'idlelib' in sys.modules


def system_clear(force=False):
    """
    Clear the console interface (console clearing operation).
    Decide whether to execute the console clearing operation based on the `force` parameter or if it's not an IDLE environment (i.e., `is_idle()` returns False).
    When `force` is True, or if not in IDLE, call the system command ("cls" for Windows, "clear" for others) to clear the console.

    Args:
      force (bool): Whether to force the clearing operation. Default is False.

    Returns:
      None
    """
    if force or (not is_idle()):
        os.system("cls" if system_check() else "clear")


