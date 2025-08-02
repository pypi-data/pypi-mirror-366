"""Logging configuration for CatSCAN - for debug and audit capabilities."""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

from catscan.config import HISTORY_DIR


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        debug: Enable debug level logging
        log_file: Optional log file path (defaults to history dir)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger('catscan')
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Console handler (only for warnings and errors to not interfere with Rich)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file or debug:
        log_dir = HISTORY_DIR / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        if not log_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f'catscan_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = 'catscan') -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)
