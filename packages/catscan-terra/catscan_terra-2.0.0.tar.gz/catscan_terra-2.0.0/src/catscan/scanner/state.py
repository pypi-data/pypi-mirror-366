
"""State file parsing and resource extraction."""

import io
import json
import zipfile
from typing import Dict, Optional
import requests
from catscan.scanner.resources import count_resources_recursive
from catscan.utils import get_logger
logger = get_logger('catscan.scanner.state')


def parse_state_data(state_data: Dict) -> Dict[str, int]:
    """Parse state data and count resources by type.
    
    Args:
        state_data: The parsed state JSON data
        
    Returns:
        Dictionary mapping resource type to count
    """
    logger.debug("Parsing state data structure")
    resource_counts = {}
    
    # Handle different state file formats
    if "values" in state_data and "root_module" in state_data["values"]:
        # Modern format - recursively count resources
        logger.debug("Detected modern state format with values/root_module structure")
        resource_counts = count_resources_recursive(state_data["values"]["root_module"])
    elif "modules" in state_data:
        # Legacy format with modules array
        logger.debug("Detected legacy state format with modules array")
        for module in state_data.get("modules", []):
            resources = module.get("resources", {})
            for resource_name, resource_data in resources.items():
                # Skip data sources
                if resource_name.startswith("data."):
                    continue
                resource_type = resource_data.get("type", "unknown")
                resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
    elif "resources" in state_data:
        # Simple format - resources at top level
        logger.debug("Detected simple state format with top-level resources")
        resources = state_data.get("resources", [])
        for resource in resources:
            # Skip data sources
            if resource.get("mode") == "data":
                continue
            resource_type = resource.get("type", "unknown")
            resource_counts[resource_type] = resource_counts.get(resource_type, 0) + 1
    else:
        logger.warning("Unknown state file format - no recognized structure found")
    
    total_resources = sum(resource_counts.values())
    logger.debug(f"Parsed state data: found {total_resources} resources across {len(resource_counts)} types")
    
    return resource_counts


def extract_state_from_response(response: requests.Response) -> Optional[Dict]:
    """Extract state data from HTTP response (handles both JSON and ZIP formats).
    
    Args:
        response: HTTP response containing state data
        
    Returns:
        Parsed state data dictionary or None if extraction fails
    """
    logger.debug(f"Extracting state from response (Content-Type: {response.headers.get('content-type', 'unknown')})")
    
    # Check if response is ZIP (by content-type or by trying to parse)
    content_type = response.headers.get('content-type', '').lower()
    state_data = None
    
    if 'application/zip' in content_type or 'application/octet-stream' in content_type:
        logger.debug("Attempting to extract state from ZIP file")
        # Handle ZIP file
        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                logger.debug(f"ZIP file contains: {zf.namelist()}")
                # Terraform state ZIP usually contains a single state file
                for filename in zf.namelist():
                    if filename.endswith('.json') or filename == 'terraform.tfstate':
                        logger.debug(f"Extracting state from ZIP file: {filename}")
                        with zf.open(filename) as f:
                            state_data = json.load(f)
                            break
        except zipfile.BadZipFile:
            logger.debug("Not a valid ZIP file, will try JSON parsing")
            # Not a ZIP, try JSON
            pass
        except Exception as e:
            logger.error(f"Error extracting ZIP file: {type(e).__name__}: {str(e)}")
    
    # If not handled as ZIP, try as JSON
    if state_data is None:
        logger.debug("Attempting to parse response as JSON")
        try:
            state_data = response.json()
        except json.JSONDecodeError:
            logger.debug("Direct JSON parsing failed, trying text extraction")
            # Last resort - try to extract JSON from response text
            # Sometimes there might be extra content
            text = response.text.strip()
            if text.startswith('{'):
                try:
                    state_data = json.loads(text)
                    logger.debug("Successfully parsed JSON from response text")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from text: {str(e)}")
            else:
                logger.error("Response does not appear to contain valid JSON")
    
    if state_data:
        logger.debug("Successfully extracted state data")
    else:
        logger.error("Failed to extract state data from response")
    
    return state_data