
"""Platform detection and platform-specific utilities for CatSCAN."""

import os
import sys
import platform
from rich.console import Console
from rich.panel import Panel

from catscan.config import CURSES_ENABLED

# Platform detection constants
IS_WINDOWS = platform.system() == "Windows"

# Curses availability detection
try:
    if not IS_WINDOWS:
        import curses
        CURSES_AVAILABLE = True
    else:
        CURSES_AVAILABLE = False
except ImportError:
    CURSES_AVAILABLE = False

# Determine if we should use curses
USE_CURSES = CURSES_AVAILABLE and not IS_WINDOWS and CURSES_ENABLED

console = Console()


def clear_screen():
    """Clear the terminal screen reliably across platforms"""
    if IS_WINDOWS:
        os.system('cls')
    else:
        # Use both methods for better compatibility
        os.system('clear')
        print("\033[H\033[2J", end="")  # ANSI escape codes as backup
        sys.stdout.flush()


def debug_platform_info():
    """Debug function to show platform detection info"""
    console.print(Panel(
        f"[bold cyan]Platform Detection Info[/bold cyan]\n"
        f"Platform: [yellow]{platform.system()}[/yellow]\n"
        f"IS_WINDOWS: [yellow]{IS_WINDOWS}[/yellow]\n"
        f"CURSES_AVAILABLE: [yellow]{CURSES_AVAILABLE}[/yellow]\n"
        f"USE_CURSES: [yellow]{USE_CURSES}[/yellow]\n"
        f"CATSCAN_NO_CURSES env: [yellow]{os.getenv('CATSCAN_NO_CURSES', 'not set')}[/yellow]",
        border_style="cyan",
        padding=(1, 2)
    ))