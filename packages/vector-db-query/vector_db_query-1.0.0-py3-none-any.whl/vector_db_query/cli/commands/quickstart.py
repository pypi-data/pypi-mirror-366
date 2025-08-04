"""Quick start guide for data sources."""

import click
from pathlib import Path
import webbrowser
import json
import yaml

from ..utils import console, create_panel, format_success, format_error, format_warning
from ...utils.logger import get_logger

logger = get_logger(__name__)


@click.command()
@click.option('--show-credentials', is_flag=True, help='Show where to get credentials')
@click.option('--example', is_flag=True, help='Create example configuration')
def quickstart(show_credentials: bool, example: bool):
    """Interactive quick start guide for data sources."""
    
    if show_credentials:
        show_credential_guide()
    elif example:
        create_example_config()
    else:
        show_quickstart_guide()


def show_quickstart_guide():
    """Show the main quick start guide."""
    console.print(create_panel(
        "[bold blue]🚀 Data Sources Quick Start Guide[/bold blue]\n\n"
        "Follow these steps to get started with data source integrations.",
        title="Quick Start"
    ))
    
    # Step 1: Prerequisites
    console.print("\n[bold cyan]Step 1: Prerequisites[/bold cyan]")
    console.print("  ✓ Python 3.8+ installed")
    console.print("  ✓ Vector DB Query system installed")
    console.print("  ✓ Access to at least one data source (Gmail, Fireflies, Google Drive)")
    
    # Step 2: Run Setup Wizard
    console.print("\n[bold cyan]Step 2: Run Setup Wizard[/bold cyan]")
    console.print("  Run the interactive setup wizard:")
    console.print("  [green]vdq setup[/green]")
    console.print("\n  The wizard will guide you through:")
    console.print("  • Selecting data sources to configure")
    console.print("  • Entering authentication credentials")
    console.print("  • Configuring sync settings")
    console.print("  • Testing connections")
    
    # Step 3: Obtain Credentials
    console.print("\n[bold cyan]Step 3: Obtain Credentials[/bold cyan]")
    console.print("  Each data source requires specific credentials:")
    console.print("\n  [yellow]Gmail:[/yellow]")
    console.print("  • Google Cloud OAuth2 credentials")
    console.print("  • Enable Gmail API in Google Cloud Console")
    console.print("\n  [yellow]Fireflies:[/yellow]")
    console.print("  • API key from Fireflies.ai account")
    console.print("  • Optional: Webhook secret for real-time updates")
    console.print("\n  [yellow]Google Drive:[/yellow]")
    console.print("  • Google Cloud OAuth2 credentials")
    console.print("  • Enable Drive API in Google Cloud Console")
    console.print("\n  Run [green]vdq quickstart --show-credentials[/green] for detailed instructions")
    
    # Step 4: Initial Sync
    console.print("\n[bold cyan]Step 4: Run Initial Sync[/bold cyan]")
    console.print("  After setup, sync your data:")
    console.print("  [green]vdq datasources sync[/green]")
    console.print("\n  Monitor progress:")
    console.print("  [green]vdq monitor[/green]")
    
    # Step 5: Configure Processing
    console.print("\n[bold cyan]Step 5: Configure Processing (Optional)[/bold cyan]")
    console.print("  Fine-tune processing settings:")
    console.print("  • [green]vdq datasources configure[/green] - Interactive configuration")
    console.print("  • Edit config/default.yaml for advanced settings")
    
    # Common Commands
    console.print("\n[bold cyan]Common Commands:[/bold cyan]")
    commands = [
        ("vdq setup", "Run setup wizard"),
        ("vdq datasources status", "Check source status"),
        ("vdq datasources sync", "Sync all sources"),
        ("vdq datasources sync --source gmail", "Sync specific source"),
        ("vdq datasources test", "Test connections"),
        ("vdq monitor", "Open monitoring dashboard"),
        ("vdq reset", "Reset configuration")
    ]
    
    for cmd, desc in commands:
        console.print(f"  [green]{cmd}[/green] - {desc}")
    
    # Tips
    console.print("\n[bold cyan]💡 Tips:[/bold cyan]")
    console.print("  • Start with one data source to test the setup")
    console.print("  • Use the monitoring dashboard to track sync progress")
    console.print("  • Enable deduplication to avoid duplicate content")
    console.print("  • Configure selective processing to filter unwanted items")
    console.print("  • Check logs in .logs/data_sources/ for troubleshooting")
    
    console.print("\n[bold green]Ready to start? Run 'vdq setup' to begin![/bold green]")


def show_credential_guide():
    """Show detailed credential obtaining guide."""
    console.print(create_panel(
        "[bold blue]🔑 Obtaining Credentials[/bold blue]\n\n"
        "Detailed instructions for obtaining credentials for each data source.",
        title="Credentials Guide"
    ))
    
    # Gmail Credentials
    console.print("\n[bold cyan]Gmail OAuth2 Credentials:[/bold cyan]")
    console.print("\n1. Go to Google Cloud Console:")
    console.print("   [link]https://console.cloud.google.com/[/link]")
    console.print("\n2. Create a new project or select existing")
    console.print("\n3. Enable Gmail API:")
    console.print("   • Go to 'APIs & Services' > 'Library'")
    console.print("   • Search for 'Gmail API'")
    console.print("   • Click 'Enable'")
    console.print("\n4. Create OAuth2 credentials:")
    console.print("   • Go to 'APIs & Services' > 'Credentials'")
    console.print("   • Click 'Create Credentials' > 'OAuth client ID'")
    console.print("   • Application type: 'Desktop app'")
    console.print("   • Download the JSON file")
    console.print("\n5. Configure OAuth consent screen:")
    console.print("   • Add your email as a test user")
    console.print("   • Add required scopes: gmail.readonly, gmail.modify")
    
    # Fireflies Credentials
    console.print("\n\n[bold cyan]Fireflies API Key:[/bold cyan]")
    console.print("\n1. Log in to Fireflies.ai:")
    console.print("   [link]https://app.fireflies.ai/[/link]")
    console.print("\n2. Go to Integrations:")
    console.print("   • Click on your profile picture")
    console.print("   • Select 'Integrations'")
    console.print("\n3. Find API section:")
    console.print("   • Scroll to 'Custom API'")
    console.print("   • Click 'Generate API Key'")
    console.print("\n4. Copy the API key and store securely")
    console.print("\n5. (Optional) Set up webhook:")
    console.print("   • Add webhook URL: https://your-domain.com/api/webhooks/fireflies")
    console.print("   • Generate or set webhook secret")
    
    # Google Drive Credentials
    console.print("\n\n[bold cyan]Google Drive OAuth2 Credentials:[/bold cyan]")
    console.print("\n1. Use the same Google Cloud project as Gmail")
    console.print("\n2. Enable Google Drive API:")
    console.print("   • Go to 'APIs & Services' > 'Library'")
    console.print("   • Search for 'Google Drive API'")
    console.print("   • Click 'Enable'")
    console.print("\n3. Use the same OAuth2 credentials as Gmail")
    console.print("   • Or create separate credentials if needed")
    console.print("\n4. Required scopes:")
    console.print("   • drive.readonly")
    console.print("   • drive.metadata.readonly")
    
    # Security Notes
    console.print("\n\n[bold red]⚠️ Security Notes:[/bold red]")
    console.print("  • Never commit credentials to version control")
    console.print("  • Store API keys in environment variables or secure vaults")
    console.print("  • Use separate credentials for production")
    console.print("  • Regularly rotate API keys")
    console.print("  • Limit OAuth scopes to minimum required")
    
    if click.confirm("\n\nOpen Google Cloud Console in browser?"):
        webbrowser.open("https://console.cloud.google.com/")


def create_example_config():
    """Create an example configuration file."""
    example_config = {
        'data_sources': {
            'gmail': {
                'enabled': False,
                'email': 'your.email@gmail.com',
                'oauth_credentials_file': 'path/to/gmail_credentials.json',
                'oauth_token_file': '.gmail_token.json',
                'folders': ['INBOX', '[Gmail]/Sent Mail'],
                'initial_history_days': 30,
                'knowledge_base_folder': 'knowledge_base/emails/gmail',
                'filters': {
                    'include_patterns': [],
                    'exclude_patterns': ['*spam*', '*newsletter*']
                },
                'sender_whitelist': [],
                'sender_blacklist': ['noreply@*', 'no-reply@*']
            },
            'fireflies': {
                'enabled': False,
                'api_key': 'your_fireflies_api_key_here',
                'webhook_secret': 'your_webhook_secret_here',
                'webhook_enabled': True,
                'initial_history_days': 30,
                'min_duration_seconds': 300,
                'max_duration_seconds': 14400,
                'platform_filters': [],
                'included_users': [],
                'excluded_users': [],
                'output_dir': 'knowledge_base/meetings/fireflies'
            },
            'google_drive': {
                'enabled': False,
                'oauth_credentials_file': 'path/to/gdrive_credentials.json',
                'oauth_token_file': '.gdrive_token.json',
                'search_patterns': ['Notes by Gemini', 'Meeting Notes'],
                'folder_ids': [],
                'initial_history_days': 30,
                'knowledge_base_folder': 'knowledge_base/meetings/gemini',
                'include_shared_drives': True,
                'follow_shortcuts': True,
                'max_results_per_query': 100
            },
            'processing': {
                'parallel_sources': True,
                'max_concurrent_items': 10,
                'retry_attempts': 3,
                'retry_delay': 60,
                'nlp': {
                    'extract_entities': True,
                    'analyze_sentiment': True,
                    'extract_key_phrases': True
                }
            },
            'deduplication': {
                'enabled': True,
                'similarity_threshold': 0.95,
                'cross_source_check': True,
                'skip_duplicates': True,
                'cache_dir': '.cache/deduplication',
                'cleanup_days': 90
            },
            'selective_processing': {
                'enabled': True,
                'filter_rules': [
                    {
                        'name': 'Exclude Automated Emails',
                        'type': 'custom',
                        'action': 'exclude',
                        'metadata': {'filter_name': 'is_automated'},
                        'priority': 10,
                        'enabled': True
                    },
                    {
                        'name': 'Skip Short Meetings',
                        'type': 'custom',
                        'action': 'exclude',
                        'metadata': {
                            'filter_name': 'meeting_duration',
                            'max_duration': 300
                        },
                        'priority': 5,
                        'enabled': True
                    }
                ],
                'manual_exclusions': {
                    'gmail': [],
                    'fireflies': [],
                    'google_drive': []
                }
            }
        }
    }
    
    # Save as YAML
    example_path = Path("config/datasources.example.yaml")
    example_path.parent.mkdir(exist_ok=True)
    
    with open(example_path, 'w') as f:
        yaml.dump(example_config, f, default_flow_style=False, sort_keys=False)
    
    console.print(format_success(f"✅ Created example configuration: {example_path}"))
    console.print("\nTo use this configuration:")
    console.print("1. Copy to config/default.yaml")
    console.print("2. Update with your actual credentials")
    console.print("3. Enable the sources you want to use")
    console.print("4. Run 'vdq datasources test' to verify")
    
    # Also create a minimal .env.example
    env_example = Path(".env.example")
    env_content = """# Data Sources Configuration
# Copy to .env and fill in your values

# Fireflies API Key (if not using keyring)
FIREFLIES_API_KEY=your_api_key_here

# Google API Key (for embeddings)
GOOGLE_API_KEY=your_google_api_key

# Logging
LOG_LEVEL=INFO
"""
    
    env_example.write_text(env_content)
    console.print(format_success(f"✅ Created example environment file: {env_example}"))


@click.group()
def quickstart_group():
    """Quick start commands."""
    pass


quickstart_group.add_command(quickstart)


if __name__ == "__main__":
    quickstart()