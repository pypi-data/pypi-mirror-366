"""Authentication setup commands."""

import click
import asyncio
import os
import json
from pathlib import Path
from typing import Dict, Any

from ...data_sources.gmail.gmail_auth import GmailOAuth2Provider
from ...data_sources.gmail.oauth_handler import OAuth2BrowserFlow, GmailOAuth2Setup
from ...data_sources.auth.storage import TokenStorage
from ...data_sources.models import SourceType
from ...utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
def auth():
    """Manage data source authentication."""
    pass


@auth.command()
@click.option('--source', type=click.Choice(['gmail', 'google_drive']), required=True,
              help='Data source to authenticate')
@click.option('--interactive/--no-interactive', default=True,
              help='Use interactive setup')
def setup(source: str, interactive: bool):
    """Set up authentication for a data source."""
    if source == 'gmail':
        asyncio.run(_setup_gmail(interactive))
    elif source == 'google_drive':
        click.echo("Google Drive authentication setup coming soon!")
    else:
        click.echo(f"Unknown source: {source}", err=True)


async def _setup_gmail(interactive: bool):
    """Set up Gmail OAuth2 authentication."""
    click.echo("Gmail OAuth2 Authentication Setup")
    click.echo("=" * 40)
    
    # Check if credentials already exist
    configured, message = GmailOAuth2Setup.check_credentials()
    
    if configured:
        click.echo(f"✓ {message}")
        if not click.confirm("Credentials already configured. Re-authenticate?"):
            return
    else:
        click.echo(f"✗ {message}")
        
        if interactive:
            # Interactive credential setup
            click.echo("\nTo set up Gmail access, you need OAuth2 credentials from Google.")
            click.echo("Follow these steps:\n")
            click.echo("1. Go to: https://console.cloud.google.com/")
            click.echo("2. Create a project (or select existing)")
            click.echo("3. Enable Gmail API")
            click.echo("4. Create OAuth2 credentials (Web application)")
            click.echo("5. Add redirect URI: http://localhost:8080/callback")
            click.echo("\nOnce you have the credentials...")
            
            client_id = click.prompt("Enter Client ID", hide_input=False)
            client_secret = click.prompt("Enter Client Secret", hide_input=True)
            
            # Set environment variables for this session
            os.environ['GOOGLE_CLIENT_ID'] = client_id
            os.environ['GOOGLE_CLIENT_SECRET'] = client_secret
            
            # Save to .env file if requested
            if click.confirm("\nSave credentials to .env file?"):
                _save_to_env_file({
                    'GOOGLE_CLIENT_ID': client_id,
                    'GOOGLE_CLIENT_SECRET': client_secret
                })
                click.echo("✓ Credentials saved to .env file")
        else:
            click.echo("Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables")
            return
    
    # Now perform authentication
    click.echo("\nInitiating Gmail authentication...")
    
    try:
        # Create OAuth2 provider
        provider = GmailOAuth2Provider()
        
        # Get authorization URL
        auth_url = provider.get_auth_url(state="gmail_setup")
        
        # Create browser flow handler
        flow = OAuth2BrowserFlow(port=8080)
        
        click.echo("Opening browser for authorization...")
        click.echo(f"If browser doesn't open, visit: {auth_url}")
        
        # Get authorization code
        code, error = await flow.get_authorization_code(auth_url)
        
        if error:
            click.echo(f"✗ Authentication failed: {error}", err=True)
            return
        
        if not code:
            click.echo("✗ No authorization code received", err=True)
            return
        
        # Exchange code for tokens
        click.echo("Exchanging authorization code for tokens...")
        token = await provider.exchange_code(code)
        
        # Store the token
        storage = TokenStorage()
        await storage.store(SourceType.GMAIL, token)
        
        click.echo(f"✓ Authentication successful!")
        click.echo(f"✓ Authorized email: {token.metadata.get('email', 'Unknown')}")
        click.echo(f"✓ Token stored securely")
        
        # Test the connection
        if click.confirm("\nTest Gmail connection?"):
            await _test_gmail_connection(token)
        
    except Exception as e:
        click.echo(f"✗ Setup failed: {str(e)}", err=True)
        logger.error(f"Gmail setup error: {e}", exc_info=True)


async def _test_gmail_connection(token):
    """Test Gmail connection with stored token."""
    click.echo("\nTesting Gmail connection...")
    
    try:
        # This will be implemented when we create the Gmail connector
        click.echo("✓ Connection test will be available after Gmail connector implementation")
    except Exception as e:
        click.echo(f"✗ Connection test failed: {str(e)}", err=True)


def _save_to_env_file(variables: Dict[str, str]):
    """Save environment variables to .env file."""
    env_path = Path('.env')
    
    # Read existing content
    existing = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    existing[key.strip()] = value.strip()
    
    # Update with new variables
    existing.update(variables)
    
    # Write back
    with open(env_path, 'w') as f:
        f.write("# Ansera Data Sources Configuration\n\n")
        
        # Group Google credentials
        google_vars = {k: v for k, v in existing.items() if k.startswith('GOOGLE_')}
        if google_vars:
            f.write("# Google OAuth2 Credentials\n")
            for key, value in sorted(google_vars.items()):
                f.write(f"{key}={value}\n")
            f.write("\n")
        
        # Write other variables
        other_vars = {k: v for k, v in existing.items() if not k.startswith('GOOGLE_')}
        if other_vars:
            f.write("# Other Configuration\n")
            for key, value in sorted(other_vars.items()):
                f.write(f"{key}={value}\n")


@auth.command()
@click.option('--source', type=click.Choice(['gmail', 'google_drive', 'all']), 
              default='all', help='Data source to check')
def status(source: str):
    """Check authentication status for data sources."""
    asyncio.run(_check_auth_status(source))


async def _check_auth_status(source: str):
    """Check authentication status."""
    storage = TokenStorage()
    
    sources_to_check = []
    if source == 'all':
        sources_to_check = [SourceType.GMAIL, SourceType.GOOGLE_DRIVE]
    elif source == 'gmail':
        sources_to_check = [SourceType.GMAIL]
    elif source == 'google_drive':
        sources_to_check = [SourceType.GOOGLE_DRIVE]
    
    click.echo("Authentication Status")
    click.echo("=" * 40)
    
    for src in sources_to_check:
        try:
            token = await storage.get(src)
            if token:
                status = "✓ Authenticated"
                if token.metadata:
                    email = token.metadata.get('email', 'Unknown')
                    status += f" ({email})"
                
                # Check if token is expired
                if token.is_expired():
                    status += " [EXPIRED]"
                
                click.echo(f"{src.value}: {status}")
            else:
                click.echo(f"{src.value}: ✗ Not authenticated")
        except Exception as e:
            click.echo(f"{src.value}: ✗ Error checking status: {str(e)}")


@auth.command()
@click.option('--source', type=click.Choice(['gmail', 'google_drive']), required=True,
              help='Data source to revoke')
@click.confirmation_option(prompt='Are you sure you want to revoke authentication?')
def revoke(source: str):
    """Revoke authentication for a data source."""
    asyncio.run(_revoke_auth(source))


async def _revoke_auth(source: str):
    """Revoke authentication."""
    storage = TokenStorage()
    
    source_type = SourceType(source)
    
    try:
        # Delete stored token
        await storage.delete(source_type)
        click.echo(f"✓ Authentication revoked for {source}")
    except Exception as e:
        click.echo(f"✗ Failed to revoke authentication: {str(e)}", err=True)