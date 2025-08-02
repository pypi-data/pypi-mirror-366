
"""
Keyring authentication for CatSCAN

This module handles secure credential storage using the system keyring.
"""

from typing import Optional

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

from catscan.config import SERVICE_NAME

from catscan.utils import get_logger
logger = get_logger('catscan.auth.keyring')


def check_keyring_availability() -> bool:
    """Check if keyring is available and working"""
    logger.debug("Checking keyring availability")
    
    if not KEYRING_AVAILABLE:
        logger.info("Keyring module not installed")
        return False
    
    try:
        # Test keyring functionality
        keyring.get_password("test-service", "test-user")
        logger.debug("Keyring is available and functional")
        return True
    except Exception as e:
        logger.warning(f"Keyring not functional: {type(e).__name__}: {str(e)}")
        return False


def get_stored_credentials(org_name: str) -> Optional[str]:
    """Retrieve stored credentials from keyring"""
    logger.debug(f"Attempting to retrieve stored credentials for org: {org_name}")
    
    if not check_keyring_availability():
        logger.info("Keyring not available, cannot retrieve stored credentials")
        return None
    
    try:
        token = keyring.get_password(SERVICE_NAME, org_name)
        if token:
            logger.info(f"Successfully retrieved stored token for org: {org_name}")
        else:
            logger.debug(f"No stored token found for org: {org_name}")
        return token
    except Exception as e:
        logger.error(f"Error accessing keyring for org {org_name}: {type(e).__name__}: {str(e)}")
        console.print(f"[yellow]⚠️ Error accessing keyring: {e}[/yellow]")
        return None


def store_credentials(org_name: str, token: str) -> bool:
    """Store credentials securely in keyring"""
    logger.debug(f"Attempting to store credentials for org: {org_name}")
    
    if not check_keyring_availability():
        logger.warning("Keyring not available, cannot store credentials")
        return False
    
    try:
        keyring.set_password(SERVICE_NAME, org_name, token)
        logger.info(f"Successfully stored credentials for org: {org_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to store credentials for org {org_name}: {type(e).__name__}: {str(e)}")
        console.print(f"[yellow]⚠️ Failed to save to keyring: {e}[/yellow]")
        return False


def delete_credentials(org_name: str) -> bool:
    """Delete stored credentials from keyring"""
    logger.debug(f"Attempting to delete credentials for org: {org_name}")
    
    if not check_keyring_availability():
        logger.warning("Keyring not available, cannot delete credentials")
        return False
    
    try:
        keyring.delete_password(SERVICE_NAME, org_name)
        logger.info(f"Successfully deleted credentials for org: {org_name}")
        return True
    except Exception as e:
        logger.warning(f"Could not delete credentials for org {org_name}: {type(e).__name__}: {str(e)}")
        return False