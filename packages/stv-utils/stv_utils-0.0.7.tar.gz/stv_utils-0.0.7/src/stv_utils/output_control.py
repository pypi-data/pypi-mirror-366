import sys


class ColorizedOutput:
    """
    A class to colorize the output of print statements based on a starting string.

    Attributes:
        original_stdout (file object): The original stdout file object.
        start (str): The starting string that triggers colorization.
        color_code (str): The ANSI escape code for the color.

    Methods:
        write(text): Writes the text to stdout, colorizing it if it starts with the specified string.
        flush(): Flushes the stdout buffer.
        __getattr__(name): Forwards attribute access to the original stdout.
    """
    try:
        def __init__(self, original_stdout, start_str = None, color_code = None):
            self.original_stdout = original_stdout
            self.start = '|>' if start_str is None else start_str
            self.color_code = '\033[90m' if color_code is None else color_code

        def write(self, text):
            if text.startswith(self.start):
                self.original_stdout.write(self.color_code)
                self.original_stdout.write(text)
                self.original_stdout.write('\033[0m')
            else:
                self.original_stdout.write(text)

        def flush(self):
            self.original_stdout.flush()

        def __getattr__(self, name):
            return getattr(self.original_stdout, name)
    except Exception as e:
        print("Error In site-packages 'stv_utils' ColorizedOutput")
        print(f"[DEBUG] {e}")


class SuppressedOutput:
    """
    A class to suppress the output of print statements based on a starting string.

    Attributes:
        original_stdout (file object): The original stdout file object.
        start_str (str): The starting string that triggers suppression.
        suppress (bool): Whether to suppress the output or not.

    Methods:
        write(text): Writes the text to stdout, suppressing it if it starts with the specified string and suppression is enabled.
        flush(): Flushes the stdout buffer.
        __getattr__(name): Forwards attribute access to the original stdout.
    """
    try:
        def __init__(self, original_stdout, start_str="|>", suppress: bool = True):
            self.original_stdout = original_stdout
            self.start_str = "|>" if start_str is None else start_str
            self.suppress = suppress

        def write(self, text):
            if not (self.suppress and text.startswith(self.start_str)):
                self.original_stdout.write(text)

        def flush(self):
            self.original_stdout.flush()

        def __getattr__(self, name):
            return getattr(self.original_stdout, name)
    except Exception as e:
        print("Error In site-packages 'stv_utils' SuppressedOutput")
        print(f"[DEBUG] {e}")


def colorize(func=None, *, start_str='|>', color_code='\033[90m'):
    """
    A decorator to colorize the output of a function based on a starting string.

    Args:
        func (callable, optional): The function to decorate.
        start_str (str): The starting string that triggers colorization.
        color_code (str): The ANSI escape code for the color.

    Returns:
        callable: The decorated function.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            original_stdout = sys.stdout
            sys.stdout = ColorizedOutput(original_stdout, start_str, color_code)
            try:
                result = f(*args, **kwargs)
            finally:
                sys.stdout = original_stdout
            return result
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def suppress_print(func=None, *, start_str=None, suppress: bool = True):
    """
    A decorator to suppress the output of a function based on a starting string.

    Args:
        func (callable, optional): The function to decorate.
        start_str (str): The starting string that triggers suppression.
        suppress (bool): Whether to suppress the output or not.

    Returns:
        callable: The decorated function.
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            original_stdout = sys.stdout
            sys.stdout = SuppressedOutput(original_stdout, start_str, suppress)
            try:
                result = f(*args, **kwargs)
            finally:
                sys.stdout = original_stdout
            return result
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)
