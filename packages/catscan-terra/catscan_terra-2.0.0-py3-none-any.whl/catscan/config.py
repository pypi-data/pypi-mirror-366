"""
CatSCAN Configuration Constants

This module contains all configuration constants used throughout the application.
These can be overridden via environment variables or command-line flags.
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "CatSCAN"
VERSION = "2.0"
SERVICE_NAME = "catscan-terraform"

# API Configuration
TFC_API_URL = os.getenv("TFC_API_URL", "https://app.terraform.io/api/v2")
RATE_LIMIT_CALLS = int(os.getenv("CATSCAN_RATE_LIMIT", "30"))  # API calls per second
MAX_WORKERS = int(os.getenv("CATSCAN_MAX_WORKERS", str(min(10, (os.cpu_count() or 1) * 2))))

# Timeouts and Retries
API_TIMEOUT = int(os.getenv("CATSCAN_API_TIMEOUT", "30"))
API_RETRY_COUNT = int(os.getenv("CATSCAN_API_RETRIES", "3"))
API_RETRY_DELAY = float(os.getenv("CATSCAN_RETRY_DELAY", "2.0"))

# Aliases for backwards compatibility
MAX_RETRIES = API_RETRY_COUNT  # Used by api.client

# File Paths
CONFIG_DIR = Path(os.getenv("CATSCAN_CONFIG_DIR", str(Path.home())))
CONFIG_FILE = CONFIG_DIR / ".catscan_config.json"
HISTORY_DIR = CONFIG_DIR / ".catscan_history"
HISTORY_RETENTION = int(os.getenv("CATSCAN_HISTORY_RETENTION", "30"))  # Number of scans to keep

# Pagination
PAGE_SIZE = int(os.getenv("CATSCAN_PAGE_SIZE", "100"))

# UI Configuration
TABLE_MAX_WIDTH = int(os.getenv("CATSCAN_TABLE_WIDTH", "120"))
CURSES_ENABLED = os.getenv("CATSCAN_NO_CURSES", "").lower() != "true"

# Security Configuration
ORG_NAME_MAX_LENGTH = 64
TOKEN_MIN_LENGTH = 20
TOKEN_MAX_LENGTH = 200

# Connection Pool Configuration
POOL_CONNECTIONS = int(os.getenv("CATSCAN_POOL_CONNECTIONS", "20"))
POOL_MAXSIZE = int(os.getenv("CATSCAN_POOL_MAXSIZE", "20"))

# Alias for backwards compatibility
CONNECTION_POOL_SIZE = POOL_CONNECTIONS  # Used by api.client