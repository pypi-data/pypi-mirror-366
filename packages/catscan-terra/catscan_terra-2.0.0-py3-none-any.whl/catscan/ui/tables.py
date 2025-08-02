"""Table formatting utilities"""

from datetime import datetime
from ..utils import get_logger

# Set up module logger
logger = get_logger('catscan.ui.tables')


def format_timestamp(iso_timestamp: str) -> str:
    """Format ISO timestamp for display"""
    try:
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug(f"Formatted timestamp: {iso_timestamp} -> {formatted}")
        return formatted
    except ValueError as e:
        logger.warning(f"Failed to format timestamp '{iso_timestamp}': {e}")
        return iso_timestamp