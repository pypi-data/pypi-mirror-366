"""Utilities module for CatSCAN - platform detection, keyboard handling, and logging."""

from .keyboard import get_key
from .platform import (
    clear_screen,
    debug_platform_info,
    IS_WINDOWS,
    USE_CURSES,
    CURSES_AVAILABLE
)
from .logging import setup_logging, get_logger

__all__ = [
    # Keyboard functions
    'get_key',
    
    # Platform functions
    'clear_screen',
    'debug_platform_info',
    
    # Platform constants
    'IS_WINDOWS',
    'USE_CURSES',
    'CURSES_AVAILABLE',
    
    # Logging functions
    'setup_logging',
    'get_logger'
]