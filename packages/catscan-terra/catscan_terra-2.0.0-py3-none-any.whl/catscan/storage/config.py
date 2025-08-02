"""Configuration file management for CatSCAN."""

import json
from pathlib import Path
from typing import Dict
from rich.console import Console
from catscan.utils import get_logger
logger = get_logger('catscan.storage.config')

from catscan.config import CONFIG_FILE

console = Console()


def load_config() -> Dict:
    """Load saved configuration from file"""
    logger.debug(f"Loading configuration from {CONFIG_FILE}")
    
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                logger.info(f"Successfully loaded configuration with {len(config)} keys")
                logger.debug(f"Config keys: {list(config.keys())}")
                return config
        else:
            logger.debug("Configuration file does not exist")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse configuration file: {str(e)}")
    except IOError as e:
        logger.error(f"Failed to read configuration file: {str(e)}")
    
    logger.debug("Returning empty configuration")
    return {}


def save_config(config: Dict):
    """Save configuration to file (excluding sensitive data)"""
    logger.debug(f"Saving configuration to {CONFIG_FILE}")
    
    try:
        # Only save non-sensitive configuration
        safe_config = {k: v for k, v in config.items() if k not in ['token', 'api_key']}
        logger.debug(f"Saving {len(safe_config)} config keys (excluded {len(config) - len(safe_config)} sensitive keys)")
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(safe_config, f, indent=2)
        
        logger.info(f"Configuration saved successfully to {CONFIG_FILE}")
    except IOError as e:
        logger.error(f"Failed to save configuration: {str(e)}")
        console.print("[yellow]⚠️ Could not save configuration[/yellow]")