"""Setup wizard for data sources configuration."""

import click
import asyncio
from pathlib import Path
import json
import yaml
from typing import Dict, Any, Optional
import keyring
from getpass import getpass
import webbrowser

from ...utils.logger import get_logger
from ...utils.config import get_config, update_config
from ...data_sources.models import SourceType
from ...data_sources.orchestrator import DataSourceOrchestrator
from ..utils import console, create_panel, format_success, format_error, format_warning

logger = get_logger(__name__)


class SetupWizard:
    """Interactive setup wizard for data sources."""
    
    def __init__(self):
        """Initialize setup wizard."""
        self.config = get_config()
        self.changes = {}
        self.orchestrator = None
        
    def run(self):
        """Run the setup wizard."""
        console.print(create_panel(
            "[bold blue]🧙 Data Sources Setup Wizard[/bold blue]\n\n"
            "This wizard will help you configure data sources for the Vector DB Query system.\n"
            "You'll be guided through setting up Gmail, Fireflies.ai, and Google Drive integrations.",
            title="Welcome"
        ))
        
        # Step 1: Choose sources
        sources_to_setup = self._choose_sources()
        
        if not sources_to_setup:
            console.print(format_warning("No sources selected. Exiting setup."))
            return
        
        # Step 2: Configure each source
        for source in sources_to_setup:
            self._configure_source(source)
        
        # Step 3: Configure processing options
        self._configure_processing_options()
        
        # Step 4: Test connections
        if click.confirm("\nWould you like to test the connections now?", default=True):
            self._test_connections(sources_to_setup)
        
        # Step 5: Save configuration
        if self.changes:
            self._save_configuration()
        
        console.print(format_success("\n✨ Setup complete! You can now use 'vdq datasources sync' to start syncing."))
    
    def _choose_sources(self) -> list:
        """Let user choose which sources to set up."""
        console.print("\n[bold]Select Data Sources to Configure[/bold]")
        console.print("Choose which data sources you want to set up:\n")
        
        sources = []
        
        if click.confirm("📧 Gmail - Sync emails via IMAP/OAuth2?", default=True):
            sources.append(SourceType.GMAIL)
        
        if click.confirm("🎙️ Fireflies.ai - Sync meeting transcripts?", default=True):
            sources.append(SourceType.FIREFLIES)
        
        if click.confirm("📁 Google Drive - Sync Gemini transcripts?", default=True):
            sources.append(SourceType.GOOGLE_DRIVE)
        
        return sources
    
    def _configure_source(self, source_type: SourceType):
        """Configure a specific data source."""
        console.print(f"\n[bold]Configuring {source_type.value.title()}[/bold]")
        
        if source_type == SourceType.GMAIL:
            self._configure_gmail()
        elif source_type == SourceType.FIREFLIES:
            self._configure_fireflies()
        elif source_type == SourceType.GOOGLE_DRIVE:
            self._configure_google_drive()
    
    def _configure_gmail(self):
        """Configure Gmail settings."""
        console.print("\n[cyan]Gmail Configuration[/cyan]")
        
        # Email address
        email = click.prompt("Gmail address", type=str)
        
        # OAuth setup
        console.print("\n[dim]Gmail requires OAuth2 authentication.[/dim]")
        console.print("You'll need to:")
        console.print("1. Create a Google Cloud project")
        console.print("2. Enable Gmail API")
        console.print("3. Create OAuth2 credentials")
        console.print("4. Download the credentials JSON file")
        
        if click.confirm("\nDo you have the OAuth2 credentials file?", default=False):
            creds_path = click.prompt("Path to credentials JSON file", type=click.Path(exists=True))
        else:
            console.print(format_warning("You'll need to obtain OAuth2 credentials before using Gmail."))
            console.print("Visit: https://console.cloud.google.com/")
            creds_path = None
        
        # Folders to sync
        console.print("\n[cyan]Select folders to sync:[/cyan]")
        folders = []
        
        if click.confirm("INBOX?", default=True):
            folders.append("INBOX")
        if click.confirm("[Gmail]/Sent Mail?", default=True):
            folders.append("[Gmail]/Sent Mail")
        if click.confirm("[Gmail]/Drafts?", default=False):
            folders.append("[Gmail]/Drafts")
        if click.confirm("[Gmail]/Starred?", default=False):
            folders.append("[Gmail]/Starred")
        
        custom = click.prompt("Additional folders (comma-separated, or press Enter to skip)", default="", show_default=False)
        if custom:
            folders.extend([f.strip() for f in custom.split(',')])
        
        # History days
        history_days = click.prompt("Initial history days to sync", type=int, default=30)
        
        # Knowledge base folder
        kb_folder = click.prompt("Knowledge base folder", default="knowledge_base/emails/gmail")
        
        # Save config
        self.changes['data_sources'] = self.changes.get('data_sources', {})
        self.changes['data_sources']['gmail'] = {
            'enabled': True,
            'email': email,
            'oauth_credentials_file': creds_path,
            'oauth_token_file': '.gmail_token.json',
            'folders': folders,
            'initial_history_days': history_days,
            'knowledge_base_folder': kb_folder
        }
        
        console.print(format_success("✅ Gmail configured"))
    
    def _configure_fireflies(self):
        """Configure Fireflies settings."""
        console.print("\n[cyan]Fireflies.ai Configuration[/cyan]")
        
        # API Key
        console.print("\n[dim]Fireflies requires an API key from your account.[/dim]")
        console.print("Get your API key from: https://app.fireflies.ai/integrations/custom/api")
        
        api_key = getpass("Fireflies API key: ")
        
        # Store in keyring for security
        try:
            keyring.set_password("vector-db-query", "fireflies-api-key", api_key)
            stored_securely = True
        except Exception as e:
            logger.warning(f"Could not store API key in keyring: {e}")
            stored_securely = False
        
        # Webhook setup (optional)
        if click.confirm("\nEnable webhook for real-time updates?", default=True):
            webhook_secret = click.prompt("Webhook secret (or press Enter to generate)", default="", show_default=False)
            if not webhook_secret:
                import secrets
                webhook_secret = secrets.token_urlsafe(32)
                console.print(f"Generated webhook secret: [yellow]{webhook_secret}[/yellow]")
        else:
            webhook_secret = None
        
        # Duration filters
        console.print("\n[cyan]Meeting duration filters:[/cyan]")
        min_duration = click.prompt("Minimum meeting duration (minutes)", type=int, default=5)
        max_duration = click.prompt("Maximum meeting duration (hours)", type=float, default=4)
        
        # Platform filters
        platforms = click.prompt(
            "Platform filters (comma-separated: zoom,teams,meet,webex or 'all')", 
            default="all"
        )
        platform_filters = [] if platforms == "all" else [p.strip() for p in platforms.split(',')]
        
        # History days
        history_days = click.prompt("Initial history days to sync", type=int, default=30)
        
        # Output directory
        output_dir = click.prompt("Output directory", default="knowledge_base/meetings/fireflies")
        
        # Save config
        self.changes['data_sources'] = self.changes.get('data_sources', {})
        self.changes['data_sources']['fireflies'] = {
            'enabled': True,
            'api_key': api_key if not stored_securely else None,
            'webhook_secret': webhook_secret,
            'webhook_enabled': webhook_secret is not None,
            'initial_history_days': history_days,
            'min_duration_seconds': min_duration * 60,
            'max_duration_seconds': int(max_duration * 3600),
            'platform_filters': platform_filters,
            'output_dir': output_dir
        }
        
        if stored_securely:
            console.print(format_success("✅ Fireflies configured (API key stored securely)"))
        else:
            console.print(format_success("✅ Fireflies configured"))
    
    def _configure_google_drive(self):
        """Configure Google Drive settings."""
        console.print("\n[cyan]Google Drive Configuration[/cyan]")
        
        # OAuth setup
        console.print("\n[dim]Google Drive requires OAuth2 authentication.[/dim]")
        console.print("You can use the same Google Cloud project as Gmail.")
        
        if click.confirm("\nDo you have the OAuth2 credentials file?", default=False):
            creds_path = click.prompt("Path to credentials JSON file", type=click.Path(exists=True))
        else:
            console.print(format_warning("You'll need to obtain OAuth2 credentials before using Google Drive."))
            creds_path = None
        
        # Search patterns
        console.print("\n[cyan]Configure search patterns:[/cyan]")
        patterns = []
        
        if click.confirm("Search for 'Notes by Gemini' files?", default=True):
            patterns.append("Notes by Gemini")
        
        custom = click.prompt("Additional search patterns (comma-separated, or press Enter)", default="", show_default=False)
        if custom:
            patterns.extend([p.strip() for p in custom.split(',')])
        
        # Folder IDs (optional)
        folder_ids = []
        if click.confirm("\nLimit search to specific folders?", default=False):
            console.print("[dim]You can find folder IDs in the Google Drive URL[/dim]")
            while True:
                folder_id = click.prompt("Folder ID (or press Enter to finish)", default="", show_default=False)
                if not folder_id:
                    break
                folder_ids.append(folder_id)
        
        # Other settings
        history_days = click.prompt("Initial history days to sync", type=int, default=30)
        kb_folder = click.prompt("Knowledge base folder", default="knowledge_base/meetings/gemini")
        
        # Advanced options
        include_shared = click.confirm("Include shared drives?", default=True)
        follow_shortcuts = click.confirm("Follow shortcuts?", default=True)
        
        # Save config
        self.changes['data_sources'] = self.changes.get('data_sources', {})
        self.changes['data_sources']['google_drive'] = {
            'enabled': True,
            'oauth_credentials_file': creds_path,
            'oauth_token_file': '.gdrive_token.json',
            'search_patterns': patterns,
            'folder_ids': folder_ids,
            'initial_history_days': history_days,
            'knowledge_base_folder': kb_folder,
            'include_shared_drives': include_shared,
            'follow_shortcuts': follow_shortcuts
        }
        
        console.print(format_success("✅ Google Drive configured"))
    
    def _configure_processing_options(self):
        """Configure general processing options."""
        console.print("\n[bold]Processing Options[/bold]")
        
        # Deduplication
        console.print("\n[cyan]Deduplication Settings:[/cyan]")
        dedup_enabled = click.confirm("Enable content deduplication?", default=True)
        
        if dedup_enabled:
            threshold = click.prompt(
                "Similarity threshold (0.0-1.0, higher = stricter)", 
                type=click.FloatRange(0.0, 1.0), 
                default=0.95
            )
            cross_source = click.confirm("Check for duplicates across all sources?", default=True)
            skip_duplicates = click.confirm("Skip duplicate documents?", default=True)
        else:
            threshold = 0.95
            cross_source = True
            skip_duplicates = True
        
        self.changes['data_sources'] = self.changes.get('data_sources', {})
        self.changes['data_sources']['deduplication'] = {
            'enabled': dedup_enabled,
            'similarity_threshold': threshold,
            'cross_source_check': cross_source,
            'skip_duplicates': skip_duplicates
        }
        
        # Parallel processing
        console.print("\n[cyan]Performance Settings:[/cyan]")
        parallel = click.confirm("Process sources in parallel?", default=True)
        max_concurrent = click.prompt("Max concurrent items", type=int, default=10)
        
        self.changes['data_sources']['processing'] = {
            'parallel_sources': parallel,
            'max_concurrent_items': max_concurrent,
            'retry_attempts': 3,
            'retry_delay': 60
        }
        
        # NLP processing
        console.print("\n[cyan]NLP Processing:[/cyan]")
        extract_entities = click.confirm("Extract named entities?", default=True)
        analyze_sentiment = click.confirm("Analyze sentiment?", default=True)
        extract_phrases = click.confirm("Extract key phrases?", default=True)
        
        self.changes['data_sources']['processing']['nlp'] = {
            'extract_entities': extract_entities,
            'analyze_sentiment': analyze_sentiment,
            'extract_key_phrases': extract_phrases
        }
        
        console.print(format_success("✅ Processing options configured"))
    
    def _test_connections(self, sources: list):
        """Test connections to configured sources."""
        console.print("\n[bold]Testing Connections[/bold]")
        
        async def test_all():
            # Create orchestrator with new config
            test_config = self.config.copy()
            test_config.update(self.changes)
            
            orchestrator = DataSourceOrchestrator()
            
            # Initialize sources based on config
            for source_type in sources:
                source_config = test_config.get('data_sources', {}).get(source_type.value, {})
                
                if not source_config.get('enabled'):
                    continue
                
                # Import and create source
                if source_type == SourceType.GMAIL:
                    from ...data_sources.gmail import GmailDataSource, GmailConfig
                    config = GmailConfig.from_dict(source_config)
                    source = GmailDataSource(config)
                elif source_type == SourceType.FIREFLIES:
                    from ...data_sources.fireflies import FirefliesDataSource, FirefliesConfig
                    # Get API key from keyring if needed
                    if not source_config.get('api_key'):
                        try:
                            source_config['api_key'] = keyring.get_password("vector-db-query", "fireflies-api-key")
                        except:
                            pass
                    config = FirefliesConfig(**source_config)
                    source = FirefliesDataSource(config)
                elif source_type == SourceType.GOOGLE_DRIVE:
                    from ...data_sources.googledrive import GoogleDriveDataSource, GoogleDriveConfig
                    config = GoogleDriveConfig.from_config(source_config)
                    source = GoogleDriveDataSource(config)
                else:
                    continue
                
                orchestrator.register_source(source_type, source)
            
            # Test each source
            for source_type, source in orchestrator.sources.items():
                console.print(f"\nTesting {source_type.value}...", end="")
                
                try:
                    # Authenticate if needed
                    if hasattr(source, 'authenticate'):
                        auth_result = await source.authenticate()
                        if not auth_result:
                            console.print(format_error(" ❌ Authentication failed"))
                            continue
                    
                    # Test connection
                    result = await source.test_connection()
                    if result:
                        console.print(format_success(" ✅ Connected"))
                    else:
                        console.print(format_error(" ❌ Connection failed"))
                except Exception as e:
                    console.print(format_error(f" ❌ Error: {str(e)}"))
        
        # Run tests
        asyncio.run(test_all())
    
    def _save_configuration(self):
        """Save configuration changes."""
        console.print("\n[bold]Saving Configuration[/bold]")
        
        # Show changes
        console.print("\nConfiguration changes:")
        for key, value in self.changes.items():
            if isinstance(value, dict):
                console.print(f"  {key}:")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        console.print(f"    {subkey}: [configured]")
                    else:
                        console.print(f"    {subkey}: {subvalue}")
        
        if click.confirm("\nSave these changes?", default=True):
            try:
                # Update config
                updated_config = self.config.copy()
                updated_config.update(self.changes)
                
                # Write to file
                config_path = Path("config/default.yaml")
                config_path.parent.mkdir(exist_ok=True)
                
                with open(config_path, 'w') as f:
                    yaml.dump(updated_config, f, default_flow_style=False, sort_keys=False)
                
                console.print(format_success(f"✅ Configuration saved to {config_path}"))
                
                # Create .gitignore if needed
                gitignore_path = config_path.parent / ".gitignore"
                if not gitignore_path.exists():
                    gitignore_path.write_text("*.json\n*_token.json\n")
                    console.print(format_success("✅ Created .gitignore for sensitive files"))
                
            except Exception as e:
                console.print(format_error(f"Failed to save configuration: {e}"))


@click.command()
@click.option('--source', type=click.Choice(['gmail', 'fireflies', 'google_drive']), 
              help='Configure specific source only')
@click.option('--quick', is_flag=True, help='Quick setup with defaults')
def setup(source: Optional[str], quick: bool):
    """Interactive setup wizard for data sources."""
    wizard = SetupWizard()
    
    if source:
        # Configure specific source only
        source_type = SourceType(source)
        wizard._configure_source(source_type)
        wizard._save_configuration()
    elif quick:
        # Quick setup with defaults
        console.print(format_warning("Quick setup not implemented yet"))
    else:
        # Full wizard
        wizard.run()


@click.command()
def reset():
    """Reset data source configuration."""
    if click.confirm("This will reset all data source configurations. Continue?", default=False):
        config = get_config()
        
        # Reset data sources section
        if 'data_sources' in config:
            config['data_sources'] = {
                'gmail': {'enabled': False},
                'fireflies': {'enabled': False},
                'google_drive': {'enabled': False},
                'processing': {
                    'parallel_sources': True,
                    'max_concurrent_items': 10,
                    'retry_attempts': 3,
                    'retry_delay': 60
                },
                'deduplication': {
                    'enabled': True,
                    'similarity_threshold': 0.95,
                    'cross_source_check': True,
                    'skip_duplicates': True
                }
            }
            
            # Save reset config
            config_path = Path("config/default.yaml")
            with open(config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
            
            console.print(format_success("✅ Configuration reset to defaults"))
            
            # Clean up tokens
            for token_file in ['.gmail_token.json', '.gdrive_token.json']:
                token_path = Path(token_file)
                if token_path.exists():
                    token_path.unlink()
                    console.print(format_success(f"✅ Removed {token_file}"))
        else:
            console.print(format_warning("No data source configuration found"))


if __name__ == "__main__":
    setup()