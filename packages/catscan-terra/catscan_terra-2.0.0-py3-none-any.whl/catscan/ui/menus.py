"""Menu systems for CatSCAN"""

from typing import List, Dict, Optional
from rich.prompt import Prompt

from .console import console
from ..utils import get_logger

# Set up module logger
logger = get_logger('catscan.ui.menus')


def show_post_scan_menu(org_name: str, workspaces_data: Optional[List[Dict]] = None) -> str:
    """Show interactive menu after scan completion
    
    Returns:
        str: Action to take ('view_details', 'run_again', 'quit')
    """
    logger.debug(f"Showing post-scan menu for org: {org_name}, has_data: {workspaces_data is not None}")
    
    while True:
        console.print()
        
        # Enhanced menu with detailed view option
        console.print("""
╭────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                │
│   What would you like to do?                                                                                   │
│                                                                                                                │
│   ╭─────────────────────────────╮         ░█████╗░░█████╗░████████╗░░░░░░░░██████╗░█████╗░░█████╗░███╗░██╗     │
│   │ [D] View detailed results   │         ██╔══██╗██╔══██╗╚══██╔══╝░░░░░░██╔════╝██╔══██╗██╔══██╗████╗░██║     │
│   │ [H] View scan history       │         ██║░░╚═╝███████║░░░██║░░░█████╗╚█████╗░██║░░╚═╝███████║██╔██╗██║     │
│   │ [R] Run another scan        │         ██║░░██╗██╔══██║░░░██║░░░╚════╝░╚═══██╗██║░░██╗██╔══██║██║╚████║     │
│   │ [S] Security settings       │         ╚█████╔╝██║░░██║░░░██║░░░░░░░░░██████╔╝╚█████╔╝██║░░██║██║░╚███║     │
│   │ [P] Platform info (debug)   │         ░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░░░░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝     │
│   │ [Q] Quit                    │                                                  Built by Simon Farrell      │
│   ╰─────────────────────────────╯                                                                              │
│                                                                                                                │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
""")
        
        # Only show detailed results option if we have workspace data
        if workspaces_data:
            valid_choices = ["d", "h", "r", "s", "p", "q", "D", "H", "R", "S", "P", "Q"]
            default = "d"
        else:
            valid_choices = ["h", "r", "s", "p", "q", "H", "R", "S", "P", "Q"]
            default = "q"
        
        choice = Prompt.ask("Choose an option", choices=valid_choices, default=default).lower()
        logger.info(f"User selected menu option: {choice}")
        
        if choice == "d" and workspaces_data:
            return "view_details"
        elif choice == "h":
            # Import here to avoid circular imports
            from .rich_ui import show_scan_history
            show_scan_history()
        elif choice == "r":
            return "run_again"
        elif choice == "s":
            # Import here to avoid circular imports
            from .rich_ui import manage_stored_credentials
            manage_stored_credentials()
        elif choice == "p":
            # Import here to avoid circular imports
            from ..utils import debug_platform_info
            debug_platform_info()
        elif choice == "q":
            console.print("\n[bold cyan]🐾 Thanks for using CatSCAN! Meow![/bold cyan]")
            return "quit"