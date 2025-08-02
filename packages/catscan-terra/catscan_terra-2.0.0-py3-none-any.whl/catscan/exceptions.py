"""
CatSCAN Custom Exceptions

This module defines custom exceptions used throughout the application
for better error handling and debugging.
"""


class CatSCANError(Exception):
    """Base exception for all CatSCAN errors"""
    pass


class ConfigurationError(CatSCANError):
    """Raised when there's an issue with configuration"""
    pass


class AuthenticationError(CatSCANError):
    """Raised when authentication fails"""
    pass


class APIError(CatSCANError):
    """Base class for API-related errors"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""
    def __init__(self, message, retry_after=None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class WorkspaceNotFoundError(APIError):
    """Raised when a workspace is not found"""
    def __init__(self, workspace_id):
        super().__init__(f"Workspace {workspace_id} not found", status_code=404)
        self.workspace_id = workspace_id


class StateFileError(CatSCANError):
    """Raised when there's an error processing state files"""
    pass


class ValidationError(CatSCANError):
    """Raised when input validation fails"""
    pass


class StorageError(CatSCANError):
    """Raised when there's an error with file storage operations"""
    pass


class KeyringError(CatSCANError):
    """Raised when keyring operations fail"""
    pass


class PlatformError(CatSCANError):
    """Raised when there's a platform-specific error"""
    pass