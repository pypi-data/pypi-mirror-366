"""Console setup and basic UI components"""

import time
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print

from ..config import VERSION, MAX_WORKERS
from ..utils import get_logger

# Set up module logger
logger = get_logger('catscan.ui.console')

# Global console instance
console = Console()


def print_banner():
    """Print elaborate ASCII banner for CatSCAN tool"""
    logger.debug("Displaying CatSCAN banner")
    
    banner = rf"""
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                      ║
║   ░█████╗░░█████╗░████████╗░░░░░░░░██████╗░█████╗░░█████╗░███╗░██╗                   ║
║   ██╔══██╗██╔══██╗╚══██╔══╝░░░░░░██╔════╝██╔══██╗██╔══██╗████╗░██║                   ║
║   ██║░░╚═╝███████║░░░██║░░░█████╗╚█████╗░██║░░╚═╝███████║██╔██╗██║                   ║
║   ██║░░██╗██╔══██║░░░██║░░░╚════╝░╚═══██╗██║░░██╗██╔══██║██║╚████║                   ║
║   ╚█████╔╝██║░░██║░░░██║░░░░░░░░░██████╔╝╚█████╔╝██║░░██║██║░╚███║                   ║
║   ░╚════╝░╚═╝░░╚═╝░░░╚═╝░░░░░░░░░╚═════╝░░╚════╝░╚═╝░░╚═╝╚═╝░░╚══╝                   ║
║                                                                                      ║
║              /\_ _/\                Terraform Infrastructure Scanner v{VERSION}            ║
║             (  o.o  )    ╭─────╮                                                     ║
║              )==Y==(     │ ╭─╮ │    ┌─────────────────────────────────────────────┐  ║
║             /       \    │ │ │ │    │   Cloud Resource Discovery & Visualization  │  ║
║            /         \   │ ╰─╯ │    │   Multi-Workspace Terraform Analysis        │  ║
║           (   | || |  )  ╰─────╯    │   Infrastructure Observability Tool         │  ║
║            \__\_/\_/__/      |      └─────────────────────────────────────────────┘  ║
║                   ||         |                                                       ║
║                   ||      .--'                                                       ║
║             \\    //      /                                                          ║
║              \\__//      /            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     ║
║                        (              ░ Scanning Your Resources... Meow!    ░░░░     ║
║                        \              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░     ║
║                         '--.__                                                       ║
║                               )                                                      ║
║                              /                                                       ║
║                             /                                                        ║
║                                                        Built by Simon Farrell        ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)
    time.sleep(3)
    logger.info("Banner displayed")


def show_scanning_panel(org_name: str):
    """Display scanning announcement panel"""
    logger.debug(f"Showing scanning panel for organization: {org_name}")
    
    scanning_text = Text()
    scanning_text.append("🔍 ", style="bold cyan")
    scanning_text.append("Initializing Secure Infrastructure Scan", style="bold white")
    scanning_text.append(f"\n   Target Organization: ", style="dim white")
    scanning_text.append(f"{org_name}", style="bold cyan")
    scanning_text.append(f"\n   Authentication: ", style="dim white")
    scanning_text.append(f"Verified ✓", style="bold green")
    scanning_text.append(f"\n   Performance Mode: ", style="dim white")
    scanning_text.append(f"Parallel ({MAX_WORKERS} workers) + Connection Pooling", style="bold green")
    scanning_text.append(f"\n   Discovering Terraform workspaces and resources...", style="dim white")
    
    console.print(Panel(
        scanning_text,
        border_style="cyan",
        padding=(1, 2),
        title="[bold cyan]🐾 CatSCAN v2.0 Active[/bold cyan]",
        title_align="left"
    ))
    print()
    
    logger.info(f"Scanning panel displayed for org: {org_name}")