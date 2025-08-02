#!/usr/bin/env python3
"""CatSCAN CLI v2.0 - Main application orchestration"""

import os
import sys
import time
import platform
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich import print
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text
from typing import List, Dict

# Import from modules
from catscan.config import (
    TFC_API_URL, CONFIG_FILE, HISTORY_DIR, SERVICE_NAME,
    VERSION, MAX_WORKERS, RATE_LIMIT_CALLS, CURSES_ENABLED
)
from catscan.auth import (
    get_config, verify_token, sanitize_org_name, sanitize_token,
    check_keyring_availability, get_stored_credentials,
    store_credentials, delete_credentials
)
from catscan.api import (
    make_api_request, get_session, close_session,
    get_workspaces, get_state_version
)
from catscan.scanner import (
    process_single_workspace, format_resource_summary
)
from catscan.storage import (
    load_config, save_config,
    save_scan_results, cleanup_old_scans,
    load_scan_history, load_scan_details
)

# Import from UI module
from catscan.ui import (
    console, print_banner, show_scanning_panel,
    show_post_scan_menu, view_detailed_results
)

# Import utilities
from catscan.utils import (
    clear_screen, setup_logging, get_logger
)

# Set up module logger
logger = get_logger('catscan.main')


def cleanup():
    """Cleanup resources on exit"""
    close_session()  # Use the imported function


def main():
    """Main execution function with enhanced security"""
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description='CatSCAN - Terraform Infrastructure Scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug logging to file'
    )
    parser.add_argument(
        '--log-file', 
        type=str,
        help='Specify custom log file path (implies --debug)'
    )
    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip the ASCII art banner'
    )
    
    args = parser.parse_args()
    
    # Set up logging based on arguments
    if args.debug or args.log_file:
        log_instance = setup_logging(debug=True, log_file=args.log_file)
        logger.info(f"CatSCAN v{VERSION} starting with debug logging enabled")
        logger.debug(f"Platform: {platform.system()}, Python: {sys.version}")
        logger.debug(f"Command line args: {vars(args)}")
    
    try:
        while True:
            if not args.no_banner:
                print_banner()
            
            logger.info("Starting new scan session")
            
            try:
                # Get configuration with security measures
                org_name, token = get_config()
                logger.info(f"Configuration obtained for org: {org_name}")
            except KeyboardInterrupt:
                logger.info("Setup cancelled by user")
                console.print("\n[yellow]⚠️ Setup cancelled[/yellow]")
                exit(0)
            except Exception as e:
                logger.error(f"Configuration error: {str(e)}", exc_info=True)
                console.print(f"\n[bold red]❌ Configuration error: {e}[/bold red]")
                exit(1)
            
            # Prepare headers with sanitized values
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/vnd.api+json",
                "org_name": org_name  # Already sanitized
            }
            
            # Show scanning panel
            show_scanning_panel(org_name)
            
            # Store workspace data for history
            workspaces_data = []
            
            # Fetch workspaces first (outside of Progress context)
            logger.info(f"Fetching workspaces for org: {org_name}")
            workspaces = get_workspaces(headers)
            
            if not workspaces:
                logger.warning("No workspaces found or error occurred")
                console.print("[bold red]No workspaces found or error occurred[/bold red]")
                action = show_post_scan_menu(org_name, None)
                if action == "quit":
                    break  # Exit the main loop
                elif action == "run_again":
                    clear_screen()
                    continue
            
            logger.info(f"Found {len(workspaces)} workspaces to process")
            console.print(f"[green]Found {len(workspaces)} workspaces[/green]\n")
            
            # Create table
            table = Table(
                title=f"📊 Deployed Resources by Workspace ({org_name})",
                show_header=True,
                header_style="bold magenta"
            )
            table.add_column("Workspace", style="cyan", no_wrap=True)
            table.add_column("Resources", style="green")
            table.add_column("Status", style="yellow")
            
            # Process workspaces with progress bar
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                
                # Process each workspace in parallel
                processed_count = 0
                error_count = 0
                
                logger.info(f"Starting parallel processing with {MAX_WORKERS} workers")
                
                # Progress bar for processing workspaces
                process_task = progress.add_task(
                    f"Processing {len(workspaces)} workspaces in parallel ({MAX_WORKERS} workers)...", 
                    total=len(workspaces)
                )
                
                # Use ThreadPoolExecutor for parallel processing
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    # Submit all workspace processing tasks
                    future_to_workspace = {
                        executor.submit(process_single_workspace, ws, headers): ws 
                        for ws in workspaces
                    }
                    
                    # Process completed tasks as they finish
                    for future in as_completed(future_to_workspace):
                        try:
                            result = future.result()
                            
                            # Add row to table
                            table.add_row(*result["row_data"])
                            
                            # Add to workspace data
                            workspaces_data.append({
                                "name": result["name"],
                                "resource_summary": result["resource_summary"],
                                "resource_count": result["resource_count"],
                                "resource_details": result.get("resource_details", {}),
                                "status": result["status"]
                            })
                            
                            # Update counters
                            if result["status"] == "success":
                                processed_count += 1
                            elif result["status"] == "error":
                                error_count += 1
                            
                            # Update progress
                            progress.update(process_task, advance=1)
                            
                        except Exception as e:
                            # Get workspace info for better error reporting
                            ws = future_to_workspace.get(future)
                            ws_name = ws["attributes"]["name"] if ws else "Unknown"
                            logger.error(f"Error processing workspace '{ws_name}': {str(e)}", exc_info=True)
                            console.print(f"[red]Error processing workspace '{ws_name}': {str(e)}[/red]")
                            
                            # Add error entry to table
                            table.add_row(ws_name, "[dim]Error[/dim]", "❌ Failed")
                            
                            # Add to workspace data as error
                            workspaces_data.append({
                                "name": ws_name,
                                "resource_summary": "Processing Error",
                                "resource_count": 0,
                                "status": "error"
                            })
                            
                            error_count += 1
                            progress.update(process_task, advance=1)
                
                progress.update(process_task, completed=True)
            
            # Display results
            console.print(table)
            print()
            
            # Show completion summary
            completion_text = Text()
            completion_text.append("✅ ", style="bold green")
            completion_text.append("Scan Complete!", style="bold white")
            completion_text.append(f"\n   Successfully processed: ", style="dim white")
            completion_text.append(f"{processed_count}", style="bold green")
            completion_text.append(f" workspaces", style="dim white")
            
            if error_count > 0:
                completion_text.append(f"\n   Empty/Error workspaces: ", style="dim white")
                completion_text.append(f"{error_count}", style="bold yellow")
            
            total_resources = sum(ws.get("resource_count", 0) for ws in workspaces_data)
            completion_text.append(f"\n   Total resources discovered: ", style="dim white")
            completion_text.append(f"{total_resources}", style="bold blue")
            completion_text.append(f"\n   ", style="dim white")
            completion_text.append(f"✓ Including nested modules", style="dim green")
            
            logger.info(f"Scan completed: {processed_count} successful, {error_count} errors, {total_resources} total resources")
            
            console.print(Panel(
                completion_text,
                border_style="green",
                padding=(1, 2),
                title="[bold green]📊 Results Summary[/bold green]",
                title_align="left"
            ))
            
            # Save scan results to history
            if save_scan_results(org_name, workspaces_data, processed_count, error_count):
                console.print("[dim]💾 Scan results saved to history[/dim]")
                logger.info("Scan results saved to history")
            
            # Show post-scan menu loop
            should_quit = False
            while not should_quit:
                action = show_post_scan_menu(org_name, workspaces_data)
                
                if action == "view_details":
                    logger.debug("User viewing detailed results")
                    view_detailed_results(org_name, workspaces_data)
                    # Continue showing the menu
                elif action == "quit":
                    logger.info("User chose to quit")
                    # Exit both loops
                    should_quit = True
                    break
                elif action == "run_again":
                    logger.info("User chose to run another scan")
                    # Break inner loop to run another scan
                    clear_screen()
                    break
            
            if should_quit:
                break  # Exit the main loop
    finally:
        logger.info("CatSCAN shutting down")
        cleanup()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        console.print("\n\n[yellow]⚠️ Scan interrupted by user[/yellow]")
        console.print("[bold cyan]🐾 Thanks for using CatSCAN! Meow![/bold cyan]")
        cleanup()
        exit(0)
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        console.print(f"\n[bold red]❌ Unexpected error: {e}[/bold red]")
        console.print("[dim]Please report this issue[/dim]")
        cleanup()
        exit(1)