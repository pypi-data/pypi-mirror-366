"""Terraform Cloud specific API functionality."""

import io
import json
import time
import zipfile
from typing import Dict, List, Optional, Tuple

import requests
from rich.console import Console

from catscan.config import TFC_API_URL, API_TIMEOUT
from catscan.exceptions import APIError
from catscan.api.client import make_api_request, get_session
from catscan.api.rate_limiter import rate_limiter


console = Console()


def get_workspaces(headers: Dict[str, str]) -> List[Dict]:
    """Fetch all workspaces from Terraform Cloud with pagination support.
    
    Args:
        headers: Request headers including Authorization and org_name
        
    Returns:
        List of workspace objects
    """
    all_workspaces = []
    page_number = 1
    total_pages = None
    
    try:
        # Get org name from headers
        org_name = headers.get('org_name')
        if not org_name:
            raise ValueError("org_name not found in headers")
        
        # Initial URL with pagination parameters
        base_url = f"{TFC_API_URL}/organizations/{org_name}/workspaces"
        url = f"{base_url}?page[size]=100&page[number]={page_number}"
        
        # Simple progress indication
        console.print("[dim]Fetching workspaces...[/dim]")
        
        while url:
            response = make_api_request(url, headers)
            if not response:
                console.print("[bold red]Failed to fetch workspaces[/bold red]")
                return all_workspaces
            
            data = response.json()
            
            # Add workspaces from this page
            all_workspaces.extend(data.get("data", []))
            
            # Update progress info
            if "meta" in data and "pagination" in data["meta"]:
                pagination = data["meta"]["pagination"]
                current_page = pagination.get("current-page", page_number)
                total_pages = pagination.get("total-pages", 1)
                total_count = pagination.get("total-count", len(all_workspaces))
                
                # Simple progress update
                console.print(f"[dim]Fetched page {current_page}/{total_pages} ({len(all_workspaces)}/{total_count} workspaces)[/dim]")
            
            # Check for next page
            links = data.get("links", {})
            next_url = links.get("next")
            
            if next_url:
                # TFC returns full URLs in links
                url = next_url
                page_number += 1
                # Small delay between pages to be respectful
                time.sleep(0.2)
            else:
                # No more pages
                url = None
        
        return all_workspaces
        
    except (KeyError, TypeError) as e:
        console.print(f"[bold red]Unexpected API response format: {e}[/bold red]")
        return all_workspaces
    except Exception as e:
        console.print(f"[bold red]Error fetching workspaces: {e}[/bold red]")
        return all_workspaces


def get_state_version(workspace_id: str, headers: Dict[str, str]) -> Optional[str]:
    """Get current state version download URL for a workspace.
    
    Args:
        workspace_id: The workspace ID
        headers: Request headers including Authorization
        
    Returns:
        State download URL if available, None otherwise
    """
    try:
        url = f"{TFC_API_URL}/workspaces/{workspace_id}/current-state-version"
        response = make_api_request(url, headers)
        
        if not response:
            return None
            
        if response.status_code == 404:
            return None
            
        data = response.json()
        return data["data"]["attributes"]["hosted-state-download-url"]
        
    except (KeyError, TypeError):
        return None


def fetch_state_file(state_url: str, headers: Dict[str, str]):
    """Fetch state file from URL.
    
    Args:
        state_url: URL to download state from
        headers: Request headers including Authorization
        
    Returns:
        Response object or None if failed
    """
    # Use rate limiter
    with rate_limiter:
        try:
            # Use session for connection pooling
            sess = get_session()
            response = sess.get(state_url, headers={
                "Authorization": headers["Authorization"],
                "Content-Type": "application/vnd.api+json"
            }, timeout=API_TIMEOUT, allow_redirects=True)
            
            if response.status_code == 429:
                # Rate limited
                retry_after = response.headers.get('Retry-After', 2)
                console.print(f"[yellow]Rate limited on state download. Waiting {retry_after} seconds...[/yellow]")
                time.sleep(float(retry_after))
                # Retry once
                response = sess.get(state_url, headers={
                    "Authorization": headers["Authorization"],
                    "Content-Type": "application/vnd.api+json"
                }, timeout=API_TIMEOUT, allow_redirects=True)
            
            if response.status_code != 200:
                return None
                
            return response
            
        except requests.exceptions.RequestException as e:
            console.print(f"[yellow]Warning: Failed to fetch state: {str(e)[:50]}[/yellow]")
            return None
