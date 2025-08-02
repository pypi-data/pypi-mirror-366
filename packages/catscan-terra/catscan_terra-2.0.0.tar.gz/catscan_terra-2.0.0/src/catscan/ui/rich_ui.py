"""Rich-based UI implementations"""

import getpass
from datetime import datetime
from typing import List, Dict
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from .console import console
from .tables import format_timestamp
from ..config import SERVICE_NAME, VERSION
from ..auth import (
    check_keyring_availability, get_stored_credentials, 
    store_credentials, delete_credentials, verify_token, sanitize_token
)
from ..storage import load_config, load_scan_history, load_scan_details
from ..utils import get_key, clear_screen, USE_CURSES, get_logger

# Set up module logger
logger = get_logger('catscan.ui.rich_ui')


def show_scan_history():
    """Interactive scan history viewer - routes to platform-specific implementation"""
    logger.debug("Starting scan history viewer")
    history = load_scan_history()
    
    if not history:
        logger.info("No scan history found")
        # Common handling for empty history
        console.print(Panel(
            "📭 [yellow]No scan history found[/yellow]\n"
            "   Run a scan first to build your history!",
            border_style="yellow",
            padding=(1, 2),
            title="[bold yellow]Empty History[/bold yellow]",
            title_align="left"
        ))
        console.print("\n[dim]Press any key to return to menu...[/dim]")
        get_key()
        return
    
    # Sort history once for both implementations
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    logger.debug(f"Found {len(history)} historical scans")
    
    # Route to platform-specific implementation
    if USE_CURSES:
        try:
            logger.debug("Using curses interface for scan history")
            from .curses_ui import show_scan_history_curses
            show_scan_history_curses(history)
        except Exception as e:
            # Fallback if curses fails
            logger.warning(f"Curses interface failed: {e}. Using standard interface.")
            console.print(f"[yellow]Curses interface failed: {e}. Using standard interface.[/yellow]")
            _show_scan_history_rich(history)
    else:
        logger.debug("Using Rich interface for scan history")
        _show_scan_history_rich(history)


def _show_scan_history_rich(history: List[Dict]):
    """Standard implementation using Rich"""
    logger.debug("Displaying scan history with Rich interface")
    selected_index = 0
    
    while True:
        clear_screen()
        
        table = Table(
            title="📈 Scan History (Use ↑↓ to navigate, Enter to view, Escape to return)",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Date/Time", style="cyan", width=20)
        table.add_column("Organization", style="green", width=25)
        table.add_column("Workspaces", style="yellow", width=12)
        table.add_column("Resources", style="blue", width=12)
        table.add_column("Status", style="white", width=15)
        
        for i, scan in enumerate(history):
            timestamp = format_timestamp(scan["timestamp"])
            org = scan["organization"]
            ws_count = scan["summary"]["processed_workspaces"]
            total_ws = scan["summary"]["total_workspaces"]
            resources = scan["summary"]["total_resources"]
            
            if scan["summary"]["error_workspaces"] > 0:
                status = f"✅ {ws_count} ⚠️ {scan['summary']['error_workspaces']}"
            else:
                status = f"✅ {ws_count}/{total_ws}"
            
            style = "bold white on blue" if i == selected_index else None
            
            table.add_row(
                timestamp, org, str(total_ws), str(resources), status,
                style=style
            )
        
        instructions = Panel(
            "🔍 [bold cyan]Navigation:[/bold cyan] ↑/↓ arrows | [bold green]Enter:[/bold green] View details | [bold red]Escape:[/bold red] Return to menu",
            border_style="dim white",
            padding=(0, 1)
        )
        
        console.print(table)
        console.print()
        console.print(instructions)
        
        key = get_key()
        logger.debug(f"User pressed key in scan history: {key}")
        
        if key == 'UP':
            selected_index = max(0, selected_index - 1)
        elif key == 'DOWN':
            selected_index = min(len(history) - 1, selected_index + 1)
        elif key == 'ENTER':
            logger.info(f"Viewing scan details for index {selected_index}")
            show_scan_details(history[selected_index])
        elif key == 'ESCAPE':
            logger.debug("Exiting scan history viewer")
            break


def show_scan_details(scan_summary: Dict):
    """Show detailed view of a specific historical scan"""
    logger.debug(f"Loading scan details for: {scan_summary.get('filename', 'unknown')}")
    scan_data = load_scan_details(scan_summary["filename"])
    
    if not scan_data:
        logger.error(f"Could not load scan details for: {scan_summary.get('filename', 'unknown')}")
        console.print("[red]❌ Could not load scan details[/red]")
        console.print("[dim]Press any key to continue...[/dim]")
        get_key()
        return
    
    while True:
        clear_screen()
        
        timestamp = format_timestamp(scan_data["timestamp"])
        scan_version = scan_data.get("version", "1.0")
        header = Panel(
            f"📊 [bold cyan]Historical Scan Details[/bold cyan]\n"
            f"   Date: [white]{timestamp}[/white]\n"
            f"   Organization: [green]{scan_data['organization']}[/green]\n"
            f"   Scanner Version: [dim]{scan_version}[/dim]",
            border_style="cyan",
            padding=(1, 2),
            title="[bold cyan]Complete Resource Inventory[/bold cyan]",
            title_align="left"
        )
        
        # Create detailed resource table
        table = Table(
            title=f"All Resources by Type and Workspace ({scan_data['organization']})",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Workspace", style="cyan", no_wrap=True)
        table.add_column("Resource Type", style="green")
        table.add_column("Count", style="yellow", justify="right")
        
        # Process each workspace
        total_resource_count = 0
        workspaces_data = scan_data.get("workspaces", [])
        
        for workspace in workspaces_data:
            ws_name = workspace["name"]
            resource_details = workspace.get("resource_details", {})
            
            if not resource_details and workspace.get("status") == "no_state":
                # No state file
                table.add_row(ws_name, "[dim]No state file[/dim]", "[dim]-[/dim]")
            elif not resource_details:
                # Empty or error
                table.add_row(ws_name, "[dim]No resources[/dim]", "[dim]0[/dim]")
            else:
                # Sort resources by count (descending) then by name
                sorted_resources = sorted(resource_details.items(), key=lambda x: (-x[1], x[0]))
                
                # Add each resource type as a separate row
                for i, (resource_type, count) in enumerate(sorted_resources):
                    # Only show workspace name on first row for that workspace
                    ws_display = ws_name if i == 0 else ""
                    table.add_row(ws_display, resource_type, str(count))
                    total_resource_count += count
                
                # Add a separator row if there are multiple workspaces
                if workspace != workspaces_data[-1] and resource_details:
                    table.add_row("", "[dim]────────────────────────[/dim]", "[dim]───[/dim]")
        
        # Summary statistics
        summary_data = scan_data.get("summary", {})
        unique_resource_types = set()
        for ws in workspaces_data:
            unique_resource_types.update(ws.get("resource_details", {}).keys())
        
        summary = Panel(
            f"📈 [bold white]Summary[/bold white]\n"
            f"   Total Workspaces: [cyan]{summary_data.get('total_workspaces', len(workspaces_data))}[/cyan]\n"
            f"   With Resources: [green]{summary_data.get('processed_workspaces', 0)}[/green]\n"
            f"   Empty/No State: [yellow]{summary_data.get('error_workspaces', 0)}[/yellow]\n"
            f"   Total Resources: [blue]{summary_data.get('total_resources', total_resource_count)}[/blue]\n"
            f"   Unique Resource Types: [magenta]{len(unique_resource_types)}[/magenta]",
            border_style="white",
            padding=(1, 2)
        )
        
        instructions = Panel(
            "[bold red]Escape:[/bold red] Return to history list",
            border_style="dim white",
            padding=(0, 1)
        )
        
        console.print(header)
        console.print()
        console.print(table)
        console.print()
        console.print(summary)
        console.print()
        console.print(instructions)
        
        key = get_key()
        if key == 'ESCAPE':
            logger.debug("Exiting scan details viewer")
            break


def manage_stored_credentials():
    """Manage stored credentials in keyring"""
    logger.debug("Starting credential management")
    
    if not check_keyring_availability():
        logger.warning("Keyring not available")
        console.print(Panel(
            "❌ [bold red]Keyring not available[/bold red]\n"
            "   Install keyring to use secure credential storage:\n"
            "   [cyan]pip install keyring[/cyan]",
            border_style="red",
            padding=(1, 2)
        ))
        console.print("\n[dim]Press any key to return to menu...[/dim]")
        get_key()
        return
    
    # List all stored organizations
    saved_config = load_config()
    known_orgs = []
    
    # Get from config history
    if saved_config.get('org_name'):
        known_orgs.append(saved_config['org_name'])
    
    # Try to find more from scan history
    history = load_scan_history()
    for scan in history:
        org = scan.get('organization')
        if org and org not in known_orgs:
            known_orgs.append(org)
    
    logger.debug(f"Found {len(known_orgs)} known organizations")
    
    if not known_orgs:
        logger.info("No known organizations found")
        console.print(Panel(
            "📭 [yellow]No stored credentials found[/yellow]\n"
            "   Run a scan first to store credentials",
            border_style="yellow",
            padding=(1, 2)
        ))
        console.print("\n[dim]Press any key to return to menu...[/dim]")
        get_key()
        return
    
    # Check which orgs have stored credentials
    orgs_with_creds = []
    for org in known_orgs:
        if get_stored_credentials(org):
            orgs_with_creds.append(org)
    
    logger.debug(f"Found {len(orgs_with_creds)} organizations with stored credentials")
    
    if not orgs_with_creds:
        logger.info("No stored credentials found in keyring")
        console.print(Panel(
            "📭 [yellow]No stored credentials found in keyring[/yellow]\n"
            "   Credentials will be stored when you run your next scan",
            border_style="yellow",
            padding=(1, 2)
        ))
        console.print("\n[dim]Press any key to return to menu...[/dim]")
        get_key()
        return
    
    # Show stored credentials
    console.print(Panel(
        "🔐 [bold cyan]Stored Credentials[/bold cyan]\n"
        "   Select an organization to manage its credentials",
        border_style="cyan",
        padding=(1, 2),
        title="[bold cyan]Credential Manager[/bold cyan]",
        title_align="left"
    ))
    console.print()
    
    # Interactive selection
    selected_index = 0
    
    while True:
        clear_screen()
        
        # Re-print the header panel
        console.print(Panel(
            "🔐 [bold cyan]Stored Credentials[/bold cyan]\n"
            "   Select an organization to manage its credentials",
            border_style="cyan",
            padding=(1, 2),
            title="[bold cyan]Credential Manager[/bold cyan]",
            title_align="left"
        ))
        console.print()
        
        table = Table(
            title="Organizations with Stored Credentials (Use ↑↓ to navigate, Enter to manage, Escape to return)",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Organization", style="green", width=40)
        table.add_column("Status", style="yellow", width=20)
        
        for i, org in enumerate(orgs_with_creds):
            style = "bold white on blue" if i == selected_index else None
            table.add_row(
                str(i + 1),
                org,
                "🔒 Stored",
                style=style
            )
        
        console.print(table)
        console.print()
        console.print("[dim]Navigate: ↑/↓ | Select: Enter | Back: Escape[/dim]")
        
        key = get_key()
        logger.debug(f"User pressed key in credential manager: {key}")
        
        if key == 'UP':
            selected_index = max(0, selected_index - 1)
        elif key == 'DOWN':
            selected_index = min(len(orgs_with_creds) - 1, selected_index + 1)
        elif key == 'ENTER':
            logger.info(f"Managing credential for: {orgs_with_creds[selected_index]}")
            manage_single_credential(orgs_with_creds[selected_index])
        elif key == 'ESCAPE':
            logger.debug("Exiting credential manager")
            break


def manage_single_credential(org_name: str):
    """Manage a single stored credential"""
    logger.debug(f"Managing credential for organization: {org_name}")
    clear_screen()
    
    console.print(Panel(
        f"🔐 [bold cyan]Credential Management[/bold cyan]\n"
        f"   Organization: [green]{org_name}[/green]\n"
        f"   Status: [yellow]Token stored in keyring[/yellow]",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print()
    
    options = [
        "[V] Verify token",
        "[U] Update token", 
        "[D] Delete token",
        "[B] Back"
    ]
    
    for opt in options:
        console.print(f"   {opt}")
    console.print()
    
    choice = Prompt.ask("Choose an option", choices=["v", "u", "d", "b", "V", "U", "D", "B"]).lower()
    logger.info(f"User selected credential action: {choice} for org: {org_name}")
    
    if choice == "v":
        # Verify token
        token = get_stored_credentials(org_name)
        if token:
            console.print("[dim]🔍 Verifying token...[/dim]")
            if verify_token(org_name, token):
                logger.info(f"Token verified successfully for: {org_name}")
                console.print("[green]✅ Token is valid and working[/green]")
            else:
                logger.warning(f"Token verification failed for: {org_name}")
                console.print("[red]❌ Token is invalid or expired[/red]")
        else:
            logger.error(f"No token found for: {org_name}")
            console.print("[red]❌ No token found[/red]")
        
    elif choice == "u":
        # Update token
        console.print("🔐 Enter new Terraform Cloud API Token (input will be hidden)")
        while True:
            new_token = getpass.getpass("   Enter token: ")
            try:
                new_token = sanitize_token(new_token)
                break
            except ValueError as e:
                console.print(f"[bold red]❌ {e}[/bold red]")
        
        console.print("[dim]🔍 Verifying new token...[/dim]")
        if verify_token(org_name, new_token):
            if store_credentials(org_name, new_token):
                logger.info(f"Token updated successfully for: {org_name}")
                console.print("[green]✅ Token updated successfully[/green]")
            else:
                logger.error(f"Failed to update token for: {org_name}")
                console.print("[red]❌ Failed to update token[/red]")
        else:
            logger.warning(f"New token verification failed for: {org_name}")
            console.print("[red]❌ New token verification failed[/red]")
    
    elif choice == "d":
        # Delete token
        if Confirm.ask(f"⚠️  Delete stored token for {org_name}?", default=False):
            if delete_credentials(org_name):
                logger.info(f"Token deleted successfully for: {org_name}")
                console.print("[green]✅ Token deleted successfully[/green]")
            else:
                logger.error(f"Failed to delete token for: {org_name}")
                console.print("[red]❌ Failed to delete token[/red]")
    
    if choice != "b":
        console.print("\n[dim]Press any key to continue...[/dim]")
        get_key()


def view_detailed_results(org_name: str, workspaces_data: List[Dict]):
    """Show detailed view of all resources from the current scan"""
    logger.debug(f"Viewing detailed results for org: {org_name} with {len(workspaces_data)} workspaces")
    
    while True:
        clear_screen()
        
        # Header info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = Panel(
            f"📊 [bold cyan]Infrastructure Details[/bold cyan]\n"
            f"   Date: [white]{timestamp}[/white]\n"
            f"   Organization: [green]{org_name}[/green]\n"
            f"   Scanner Version: [dim]{VERSION}[/dim]",
            border_style="cyan",
            padding=(1, 2),
            title="[bold cyan]Complete Resource Inventory[/bold cyan]",
            title_align="left"
        )
        
        # Create detailed resource table
        table = Table(
            title=f"All Resources by Type and Workspace ({org_name})",
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("Workspace", style="cyan", no_wrap=True)
        table.add_column("Resource Type", style="green")
        table.add_column("Count", style="yellow", justify="right")
        
        # Process each workspace
        total_resource_count = 0
        for workspace in workspaces_data:
            ws_name = workspace["name"]
            resource_details = workspace.get("resource_details", {})
            
            if not resource_details and workspace["status"] == "no_state":
                # No state file
                table.add_row(ws_name, "[dim]No state file[/dim]", "[dim]-[/dim]")
            elif not resource_details:
                # Empty or error
                table.add_row(ws_name, "[dim]No resources[/dim]", "[dim]0[/dim]")
            else:
                # Sort resources by count (descending) then by name
                sorted_resources = sorted(resource_details.items(), key=lambda x: (-x[1], x[0]))
                
                # Add each resource type as a separate row
                for i, (resource_type, count) in enumerate(sorted_resources):
                    # Only show workspace name on first row for that workspace
                    ws_display = ws_name if i == 0 else ""
                    table.add_row(ws_display, resource_type, str(count))
                    total_resource_count += count
                
                # Add a separator row if there are multiple workspaces
                if workspace != workspaces_data[-1] and resource_details:
                    table.add_row("", "[dim]────────────────────────[/dim]", "[dim]───[/dim]")
        
        # Summary statistics
        processed_count = sum(1 for ws in workspaces_data if ws["status"] == "success")
        error_count = sum(1 for ws in workspaces_data if ws["status"] in ["error", "no_state"])
        
        summary = Panel(
            f"📈 [bold white]Summary[/bold white]\n"
            f"   Total Workspaces: [cyan]{len(workspaces_data)}[/cyan]\n"
            f"   With Resources: [green]{processed_count}[/green]\n"
            f"   Empty/No State: [yellow]{error_count}[/yellow]\n"
            f"   Total Resources: [blue]{total_resource_count}[/blue]\n"
            f"   Unique Resource Types: [magenta]{len(set(rt for ws in workspaces_data for rt in ws.get('resource_details', {}).keys()))}[/magenta]",
            border_style="white",
            padding=(1, 2)
        )
        
        # Instructions
        instructions = Panel(
            "[bold red]Escape:[/bold red] Return to menu",
            border_style="dim white",
            padding=(0, 1)
        )
        
        console.print(header)
        console.print()
        console.print(table)
        console.print()
        console.print(summary)
        console.print()
        console.print(instructions)
        
        # Wait for escape key
        key = get_key()
        if key == 'ESCAPE':
            logger.debug("Exiting detailed results viewer")
            break