"""Storage module for CatSCAN - handles configuration and history persistence."""

from .config import load_config, save_config
from .history import (
    save_scan_results,
    cleanup_old_scans,
    load_scan_history,
    load_scan_details
)

__all__ = [
    # Config functions
    'load_config',
    'save_config',
    
    # History functions
    'save_scan_results',
    'cleanup_old_scans',
    'load_scan_history',
    'load_scan_details'
]