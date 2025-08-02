
"""
Input validation for CatSCAN

This module provides validation functions for user input
to ensure security and prevent injection attacks.
"""

import re

from catscan.config import ORG_NAME_MAX_LENGTH, TOKEN_MIN_LENGTH, TOKEN_MAX_LENGTH

from catscan.utils import get_logger
logger = get_logger('catscan.auth.validators')

# Validation patterns
ORG_NAME_PATTERN = re.compile(r'^[A-Za-z0-9._-]+$')
TOKEN_PATTERN = re.compile(r'^[\x21-\x7e]+$')  # Printable ASCII chars


def sanitize_org_name(name: str) -> str:
    """Sanitize organization name to prevent injection attacks"""
    logger.debug(f"Validating organization name: '{name}'")
    
    name = name.strip()
    if not name:
        logger.warning("Organization name validation failed: empty name")
        raise ValueError("Organization name cannot be empty")
    if len(name) > 64:  # Reasonable limit
        logger.warning(f"Organization name validation failed: too long ({len(name)} chars)")
        raise ValueError("Organization name too long (max 64 characters)")
    if not ORG_NAME_PATTERN.fullmatch(name):
        logger.warning(f"Organization name validation failed: invalid characters in '{name}'")
        raise ValueError("Organization name may only contain letters, digits, dots, underscores or hyphens")
    
    logger.debug(f"Organization name validated successfully: '{name}'")
    return name


def sanitize_token(token: str) -> str:
    """Sanitize API token to ensure it's valid"""
    logger.debug("Validating API token format")
    
    token = token.strip()
    if not token:
        logger.warning("Token validation failed: empty token")
        raise ValueError("API token cannot be empty")
    if len(token) < 20 or len(token) > 200:  # Terraform tokens are typically 40-100 chars
        logger.warning(f"Token validation failed: invalid length ({len(token)} chars)")
        raise ValueError("API token length seems invalid")
    if not TOKEN_PATTERN.fullmatch(token):
        logger.warning("Token validation failed: contains invalid characters")
        raise ValueError("Token contains invalid characters")
    
    logger.debug("Token format validated successfully")
    return token