"""Reusable panel components"""

from rich.panel import Panel
from rich.text import Text
from typing import Optional, Dict

from .console import console
from ..utils import get_logger

# Set up module logger
logger = get_logger('catscan.ui.panels')


def create_error_panel(message: str, title: str = "Error") -> Panel:
    """Create a standardized error panel"""
    logger.debug(f"Creating error panel: {title}")
    return Panel(
        f"❌ [bold red]{message}[/bold red]",
        border_style="red",
        padding=(1, 2),
        title=f"[bold red]{title}[/bold red]",
        title_align="left"
    )


def create_warning_panel(message: str, title: str = "Warning") -> Panel:
    """Create a standardized warning panel"""
    logger.debug(f"Creating warning panel: {title}")
    return Panel(
        f"⚠️ [bold yellow]{message}[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
        title=f"[bold yellow]{title}[/bold yellow]",
        title_align="left"
    )


def create_success_panel(message: str, title: str = "Success") -> Panel:
    """Create a standardized success panel"""
    logger.debug(f"Creating success panel: {title}")
    return Panel(
        f"✅ [bold green]{message}[/bold green]",
        border_style="green",
        padding=(1, 2),
        title=f"[bold green]{title}[/bold green]",
        title_align="left"
    )


def create_info_panel(text: Text, title: str, border_style: str = "cyan") -> Panel:
    """Create a standardized info panel with rich text content"""
    logger.debug(f"Creating info panel: {title}")
    return Panel(
        text,
        border_style=border_style,
        padding=(1, 2),
        title=f"[bold {border_style}]{title}[/bold {border_style}]",
        title_align="left"
    )


def create_summary_panel(summary_data: Dict[str, str], title: str = "Summary") -> Panel:
    """Create a summary panel from key-value pairs"""
    logger.debug(f"Creating summary panel with {len(summary_data)} items")
    
    summary_text = Text()
    summary_text.append(f"📈 [bold white]{title}[/bold white]\n")
    
    for key, value in summary_data.items():
        summary_text.append(f"   {key}: ", style="dim white")
        summary_text.append(f"{value}\n", style="bold cyan")
    
    return Panel(
        summary_text,
        border_style="white",
        padding=(1, 2)
    )