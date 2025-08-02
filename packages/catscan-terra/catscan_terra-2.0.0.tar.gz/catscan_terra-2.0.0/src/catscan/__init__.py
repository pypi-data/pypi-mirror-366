"""
CatSCAN - Terraform Infrastructure Scanner

A secure, high-performance tool for scanning and analyzing Terraform Cloud infrastructure.
"""

__version__ = "2.0.0"
__author__ = "Simon Farrell"

# Make key functions available at package level
from .auth import get_config, verify_token
from .config import VERSION

__all__ = [
    'get_config',
    'verify_token',
    'VERSION',
    '__version__',
]