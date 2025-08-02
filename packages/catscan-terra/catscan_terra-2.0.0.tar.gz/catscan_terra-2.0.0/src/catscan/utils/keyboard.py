
"""Cross-platform keyboard input handling for CatSCAN."""

import sys
import time
import platform

if platform.system() == "Windows":
    import msvcrt
else:
    import termios
    import tty


def get_key():
    """Cross-platform function to get a single keypress"""
    if platform.system() == "Windows":
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key == b'\xe0':  # Special key prefix
                    key = msvcrt.getch()
                    if key == b'H':  # Up arrow
                        return 'UP'
                    elif key == b'P':  # Down arrow
                        return 'DOWN'
                elif key == b'\r':  # Enter
                    return 'ENTER'
                elif key == b'\x1b':  # Escape
                    return 'ESCAPE'
                elif key in [b'h', b'H']:
                    return 'h'
                elif key in [b'r', b'R']:
                    return 'r'
                elif key in [b's', b'S']:
                    return 's'
                elif key in [b'd', b'D']:
                    return 'd'
                elif key in [b'q', b'Q']:
                    return 'q'
                elif key in [b'p', b'P']:
                    return 'p'
            time.sleep(0.01)
    else:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
            
            if key == '\x1b':  # Escape sequence
                next_chars = sys.stdin.read(2)
                if next_chars == '[A':  # Up arrow
                    return 'UP'
                elif next_chars == '[B':  # Down arrow
                    return 'DOWN'
                else:
                    return 'ESCAPE'
            elif key == '\r' or key == '\n':  # Enter
                return 'ENTER'
            elif key.lower() in ['h', 'r', 's', 'd', 'q', 'p']:
                return key.lower()
            else:
                return key
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)