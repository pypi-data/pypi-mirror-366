"""Workspace processing logic for CatSCAN scanner."""

from typing import Dict
from rich.console import Console

from catscan.api import get_state_version, fetch_state_file
from catscan.scanner.state import extract_state_from_response, parse_state_data
from catscan.scanner.resources import format_resource_summary
from catscan.utils import get_logger

logger = get_logger('catscan.scanner.workspace')
console = Console()


def process_single_workspace(ws: Dict, headers: Dict) -> Dict:
    """Process a single workspace - designed for parallel execution"""
    name = ws["attributes"]["name"]
    ws_id = ws["id"]
    
    logger.info(f"Processing workspace: {name} (ID: {ws_id})")
    
    try:
        state_url = get_state_version(ws_id, headers)
        if not state_url:
            logger.debug(f"No state version found for workspace: {name}")
            return {
                "name": name,
                "resource_summary": "No state",
                "resource_count": 0,
                "status": "no_state",
                "row_data": (name, "[dim]No state[/dim]", "🚫 No State")
            }
        
        logger.debug(f"Found state URL for workspace {name}: {state_url}")
        
        # Fetch the state file (returns HTTP response)
        state_response = fetch_state_file(state_url, headers)
        
        if not state_response:
            logger.warning(f"Failed to fetch state file for workspace: {name}")
            return {
                "name": name,
                "resource_summary": "Empty/Error",
                "resource_count": 0,
                "status": "error",
                "row_data": (name, "[dim]Empty/Error[/dim]", "⚠️ Empty")
            }
        
        # Extract state data from response
        state_data = extract_state_from_response(state_response)
        
        if not state_data:
            logger.warning(f"Failed to extract state data for workspace: {name}")
            return {
                "name": name,
                "resource_summary": "Empty/Error",
                "resource_count": 0,
                "status": "error",
                "row_data": (name, "[dim]Empty/Error[/dim]", "⚠️ Empty")
            }
        
        # Parse state data to get resource counts
        resource_counts = parse_state_data(state_data)
        
        if not resource_counts:
            logger.warning(f"No resources found in state for workspace: {name}")
            return {
                "name": name,
                "resource_summary": "Empty/Error",
                "resource_count": 0,
                "status": "error",
                "row_data": (name, "[dim]Empty/Error[/dim]", "⚠️ Empty")
            }
        else:
            # Format the resource summary
            resource_summary = format_resource_summary(resource_counts)
            total_resources = sum(resource_counts.values())
            
            logger.info(f"Workspace {name} processed successfully: {total_resources} resources in {len(resource_counts)} types")
            logger.debug(f"Resource breakdown for {name}: {dict(resource_counts)}")
            
            return {
                "name": name,
                "resource_summary": resource_summary,
                "resource_count": total_resources,
                "resource_details": resource_counts,
                "status": "success",
                "row_data": (name, resource_summary, f"✅ {total_resources}")
            }
    except Exception as e:
        logger.error(f"Error processing workspace '{name}': {type(e).__name__}: {str(e)}", exc_info=True)
        # Log the specific error for debugging
        console.print(f"[red]Error in process_single_workspace for '{name}': {type(e).__name__}: {str(e)}[/red]")
        return {
            "name": name,
            "resource_summary": f"Error: {str(e)[:50]}",
            "resource_count": 0,
            "status": "error",
            "row_data": (name, "[dim]Processing Error[/dim]", "❌ Failed")
        }