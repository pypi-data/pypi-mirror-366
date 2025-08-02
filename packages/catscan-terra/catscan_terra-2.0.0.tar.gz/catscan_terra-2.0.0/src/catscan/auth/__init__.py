"""
Authentication package for CatSCAN

This package provides authentication and credential management functionality.
"""

from .keyring_auth import (
    check_keyring_availability,
    get_stored_credentials,
    store_credentials,
    delete_credentials,
    KEYRING_AVAILABLE
)

from .config_auth import (
    get_config,
    get_interactive_config,
    verify_token
)

from .validators import (
    sanitize_org_name,
    sanitize_token,
    ORG_NAME_PATTERN,
    TOKEN_PATTERN
)

__all__ = [
    # Keyring functions
    'check_keyring_availability',
    'get_stored_credentials',
    'store_credentials',
    'delete_credentials',
    'KEYRING_AVAILABLE',
    
    # Config functions
    'get_config',
    'get_interactive_config',
    'verify_token',
    
    # Validators
    'sanitize_org_name',
    'sanitize_token',
    'ORG_NAME_PATTERN',
    'TOKEN_PATTERN',
]