"""
Configuration-based authentication for CatSCAN

This module handles getting configuration from various sources
including environment variables, stored credentials, and interactive input.
"""

import os
import getpass
from typing import Tuple

from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from catscan.api.client import make_api_request
from catscan.auth.keyring_auth import (
    check_keyring_availability,
    get_stored_credentials,
    store_credentials,
    delete_credentials
)
from catscan.auth.validators import sanitize_org_name, sanitize_token
from catscan.config import TFC_API_URL, SERVICE_NAME, MAX_WORKERS
from catscan.storage.config import load_config, save_config
# REMOVED TO FIX CIRCULAR IMPORT: from catscan.ui.console import console
from catscan.utils import get_logger
logger = get_logger('catscan.auth.config')


def verify_token(org_name: str, token: str) -> bool:
    """Verify that the token works by making a test API call"""
    logger.debug(f"Verifying token for org: {org_name}")
    
    try:
        url = f"{TFC_API_URL}/organizations/{org_name}"
        headers = {"Authorization": f"Bearer {token}"}
        response = make_api_request(url, headers, retry_count=2)
        
        if response is not None and response.status_code == 200:
            logger.info(f"Token verification successful for org: {org_name}")
            return True
        else:
            logger.warning(f"Token verification failed for org: {org_name} - Response: {response.status_code if response else 'None'}")
            return False
    except Exception as e:
        logger.error(f"Token verification error for org {org_name}: {type(e).__name__}: {str(e)}")
        return False


def get_interactive_config() -> Tuple[str, str]:
    """Get configuration through interactive prompts with security measures"""
    # Local import to avoid circular dependency
    from catscan.ui.console import console
    
    logger.debug("Starting interactive configuration")
    
    saved_config = load_config()
    
    # Show security-focused setup panel
    setup_text = Text()
    setup_text.append("🔒 ", style="bold blue")
    setup_text.append("Secure Configuration Setup", style="bold white")
    setup_text.append("\nPlease provide your Terraform Cloud credentials", style="dim white")
    
    if check_keyring_availability():
        setup_text.append("\n✅ Keyring available - credentials will be stored securely", style="bold green")
        setup_text.append("\n   Your token will be encrypted in the system credential store", style="dim green")
    else:
        setup_text.append("\n⚠️  Keyring not available - using environment variables only", style="bold yellow")
        setup_text.append("\n   Install keyring with: pip install keyring", style="dim yellow")
    
    console.print(Panel(
        setup_text,
        border_style="blue",
        padding=(1, 2),
        title="[bold blue]🛡️ Secure Setup[/bold blue]",
        title_align="left"
    ))
    print()
    
    # Get organization name with validation
    saved_org = saved_config.get('org_name')
    logger.debug(f"Found saved org in config: {saved_org}")
    
    while True:
        if saved_org:
            org_prompt = f"🏢 Organization name [{saved_org}]"
            org_name = Prompt.ask(org_prompt, default=saved_org)
        else:
            org_name = Prompt.ask("🏢 Organization name", console=console)
        
        try:
            org_name = sanitize_org_name(org_name)
            logger.debug(f"Organization name validated: {org_name}")
            break
        except ValueError as e:
            logger.warning(f"Invalid organization name '{org_name}': {str(e)}")
            console.print(f"[bold red]❌ {e}[/bold red]")
    
    # Check for existing stored token
    stored_token = get_stored_credentials(org_name)
    if stored_token:
        logger.info(f"Found existing stored token for org: {org_name}")
        console.print(f"[green]🔓 Found stored token for '{org_name}'[/green]")
        use_stored = Confirm.ask("Use stored token?", default=True)
        if use_stored:
            logger.info(f"Using stored token for org: {org_name}")
            # Save org name to config
            save_config({'org_name': org_name})
            return org_name, stored_token
        else:
            # Offer to delete old token
            if Confirm.ask("Delete the stored token?", default=False):
                if delete_credentials(org_name):
                    console.print("[green]✅ Old token deleted[/green]")
    
    # Get new token with validation
    logger.debug("Prompting for new token")
    console.print("🔐 Terraform Cloud API Token (input will be hidden)")
    while True:
        token = getpass.getpass("   Enter token: ")
        
        try:
            token = sanitize_token(token)
            logger.debug("Token format validated")
            break
        except ValueError as e:
            logger.warning(f"Invalid token format: {str(e)}")
            console.print(f"[bold red]❌ {e}[/bold red]")
    
    # Verify token works before storing
    console.print("[dim]🔍 Verifying token...[/dim]")
    if not verify_token(org_name, token):
        logger.error(f"Token verification failed for org: {org_name}")
        console.print("[bold red]❌ Token verification failed. Please check your credentials.[/bold red]")
        exit(1)
    
    console.print("[green]✅ Token verified successfully[/green]")
    
    # Offer to store securely
    if check_keyring_availability():
        if Confirm.ask("💾 Save token securely to system keyring?", default=True):
            if store_credentials(org_name, token):
                logger.info(f"Token stored securely for org: {org_name}")
                console.print(Panel(
                    "✅ [bold green]Token stored securely[/bold green]\n"
                    "   Your token is encrypted in the system credential store\n"
                    "   It will be automatically retrieved on future runs\n\n"
                    "🗑️  [bold yellow]To remove later:[/bold yellow]\n"
                    f"   Run: [cyan]keyring del {SERVICE_NAME} {org_name}[/cyan]",
                    border_style="green",
                    padding=(1, 2),
                    title="[bold green]Secure Storage Active[/bold green]",
                    title_align="left"
                ))
            else:
                console.print("[yellow]⚠️ Could not store token in keyring[/yellow]")
        else:
            logger.info("User declined to store token in keyring")
            console.print("[yellow]ℹ️ Token will be used for this session only[/yellow]")
    else:
        console.print(Panel(
            "⚠️ [bold yellow]Session-only storage[/bold yellow]\n"
            "   Install keyring for secure credential storage:\n"
            "   [cyan]pip install keyring[/cyan]",
            border_style="yellow",
            padding=(1, 2)
        ))
    
    # Save organization name to config
    save_config({'org_name': org_name})
    logger.info(f"Configuration completed for org: {org_name}")
    
    print()
    return org_name, token


def get_config() -> Tuple[str, str]:
    """Get configuration from various sources with security priority"""
    # Local import to avoid circular dependency
    from catscan.ui.console import console
    
    logger.debug("Getting configuration")
    
    # Priority 1: Check environment variables (for CI/CD compatibility)
    env_org = os.getenv("TFC_ORG_NAME")
    env_token = os.getenv("TFC_TOKEN")
    
    if env_org and env_token:
        logger.info("Found configuration in environment variables")
        try:
            # Validate even environment variables
            env_org = sanitize_org_name(env_org)
            env_token = sanitize_token(env_token)
            logger.info(f"Using environment variables for org: {env_org}")
            
            console.print(Panel(
                "🤖 [bold green]Environment variables detected[/bold green]\n"
                f"   Organization: [cyan]{env_org}[/cyan]\n"
                f"   Token: [dim]{'•' * 8}[/dim] (from TFC_TOKEN)\n"
                f"   Performance: [green]Connection pooling + {MAX_WORKERS} parallel workers[/green]",
                border_style="green",
                padding=(1, 2),
                title="[bold green]Environment Mode[/bold green]",
                title_align="left"
            ))
            print()
            return env_org, env_token
        except ValueError as e:
            logger.warning(f"Invalid environment variables: {str(e)}")
            console.print(f"[bold red]❌ Invalid environment variable: {e}[/bold red]")
            console.print("[yellow]Falling back to interactive mode...[/yellow]")
            print()
    
    # Priority 2: Check saved config + keyring
    saved_config = load_config()
    saved_org = saved_config.get('org_name')
    
    if saved_org and check_keyring_availability():
        logger.debug(f"Checking for stored token for saved org: {saved_org}")
        stored_token = get_stored_credentials(saved_org)
        if stored_token:
            try:
                # Validate stored credentials
                saved_org = sanitize_org_name(saved_org)
                stored_token = sanitize_token(stored_token)
                logger.info(f"Found valid stored credentials for org: {saved_org}")
                
                console.print(Panel(
                    "🔐 [bold green]Using stored credentials[/bold green]\n"
                    f"   Organization: [cyan]{saved_org}[/cyan]\n"
                    f"   Token: [dim]{'•' * 8}[/dim] (from secure storage)\n"
                    f"   Performance: [green]Connection pooling + {MAX_WORKERS} parallel workers[/green]",
                    border_style="green",
                    padding=(1, 2),
                    title="[bold green]Keyring Mode[/bold green]",
                    title_align="left"
                ))
                
                # Quick verification
                console.print("[dim]🔍 Verifying stored credentials...[/dim]")
                if verify_token(saved_org, stored_token):
                    console.print("[green]✅ Credentials valid[/green]")
                    print()
                    return saved_org, stored_token
                else:
                    logger.warning(f"Stored credentials invalid for org: {saved_org}")
                    console.print("[yellow]⚠️ Stored credentials invalid or expired[/yellow]")
                    if Confirm.ask("Delete invalid stored token?", default=True):
                        delete_credentials(saved_org)
            except ValueError as e:
                logger.error(f"Stored credentials corrupted for org {saved_org}: {str(e)}")
                console.print(f"[bold red]❌ Stored credentials corrupted: {e}[/bold red]")
                if Confirm.ask("Delete corrupted credentials?", default=True):
                    delete_credentials(saved_org)
    
    # Priority 3: Interactive mode
    logger.info("Falling back to interactive configuration")
    return get_interactive_config()