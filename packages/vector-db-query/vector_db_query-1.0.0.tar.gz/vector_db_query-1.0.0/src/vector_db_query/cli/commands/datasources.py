"""CLI commands for data sources configuration and management."""

import click
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
import yaml

from ...data_sources.orchestrator import DataSourceOrchestrator
from ...data_sources.models import SourceType
from ...utils.logger import get_logger
from ...utils.config import get_config, update_config

console = Console()
logger = get_logger(__name__)


@click.group()
def datasources():
    """Configure and manage data sources."""
    pass


@datasources.command()
def status():
    """Show status of all data sources."""
    async def _status():
        try:
            console.print(Panel("📊 Data Sources Status", style="bold blue"))
            
            # Initialize orchestrator
            orchestrator = DataSourceOrchestrator()
            await orchestrator.initialize_sources()
            
            # Get metrics for all sources
            metrics = await orchestrator.get_metrics()
            
            # Create status table
            table = Table(title="Data Source Status")
            table.add_column("Source", style="cyan")
            table.add_column("Enabled", style="green")
            table.add_column("Connected", style="yellow")
            table.add_column("Last Sync", style="blue")
            table.add_column("Items", style="magenta")
            table.add_column("Status", style="white")
            
            config = get_config()
            ds_config = config.get('data_sources', {})
            
            for source_type in SourceType:
                source_config = ds_config.get(source_type.value, {})
                enabled = source_config.get('enabled', False)
                
                if source_type.value in metrics:
                    source_metrics = metrics[source_type.value]
                    
                    if 'error' in source_metrics:
                        table.add_row(
                            source_type.value.title(),
                            "✅" if enabled else "❌",
                            "❌",
                            "N/A",
                            "N/A",
                            f"[red]Error: {source_metrics['error']}[/red]"
                        )
                    else:
                        sync_state = source_metrics.get('sync_state', {})
                        metrics_data = source_metrics.get('metrics', {})
                        
                        table.add_row(
                            source_type.value.title(),
                            "✅" if enabled else "❌",
                            "✅" if metrics_data.get('connected', False) else "❌",
                            sync_state.get('last_sync', 'Never'),
                            str(metrics_data.get('total_items', 0)),
                            "Active" if sync_state.get('is_active', False) else "Inactive"
                        )
                else:
                    table.add_row(
                        source_type.value.title(),
                        "✅" if enabled else "❌",
                        "N/A",
                        "N/A",
                        "N/A",
                        "Not initialized"
                    )
            
            console.print(table)
            
            # Show deduplication stats
            dedup_stats = orchestrator.get_deduplication_stats()
            if dedup_stats['total_documents'] > 0:
                console.print("\n[bold]Deduplication Statistics:[/bold]")
                console.print(f"  Total Documents: {dedup_stats['total_documents']:,}")
                console.print(f"  Unique Documents: {dedup_stats.get('unique_documents', 0):,}")
                
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_status())


@datasources.command()
def configure():
    """Interactive configuration wizard for data sources."""
    console.print(Panel("🔧 Data Sources Configuration Wizard", style="bold blue"))
    
    # Load current config
    config = get_config()
    ds_config = config.get('data_sources', {})
    
    # Configure each source
    for source_type in SourceType:
        console.print(f"\n[bold cyan]Configure {source_type.value.title()}:[/bold cyan]")
        
        source_config = ds_config.get(source_type.value, {})
        
        # Enable/disable source
        enabled = Confirm.ask(
            f"Enable {source_type.value}?",
            default=source_config.get('enabled', False)
        )
        
        source_config['enabled'] = enabled
        
        if enabled:
            if source_type == SourceType.GMAIL:
                _configure_gmail(source_config)
            elif source_type == SourceType.FIREFLIES:
                _configure_fireflies(source_config)
            elif source_type == SourceType.GOOGLE_DRIVE:
                _configure_google_drive(source_config)
        
        ds_config[source_type.value] = source_config
    
    # Configure deduplication
    console.print("\n[bold cyan]Configure Deduplication:[/bold cyan]")
    dedup_config = ds_config.get('deduplication', {})
    
    dedup_config['enabled'] = Confirm.ask(
        "Enable content deduplication?",
        default=dedup_config.get('enabled', True)
    )
    
    if dedup_config['enabled']:
        threshold = Prompt.ask(
            "Similarity threshold (0.0-1.0)",
            default=str(dedup_config.get('similarity_threshold', 0.95))
        )
        dedup_config['similarity_threshold'] = float(threshold)
        
        dedup_config['cross_source_check'] = Confirm.ask(
            "Check for duplicates across all sources?",
            default=dedup_config.get('cross_source_check', True)
        )
        
        dedup_config['skip_duplicates'] = Confirm.ask(
            "Skip duplicate documents?",
            default=dedup_config.get('skip_duplicates', True)
        )
    
    ds_config['deduplication'] = dedup_config
    
    # Save configuration
    config['data_sources'] = ds_config
    
    # Write to config file
    config_path = Path("config/default.yaml")
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    console.print("\n[green]✅ Configuration saved![/green]")
    console.print(f"Configuration file: {config_path}")


def _configure_gmail(config: Dict[str, Any]):
    """Configure Gmail settings."""
    config['email'] = Prompt.ask(
        "Gmail address",
        default=config.get('email', '')
    )
    
    # OAuth credentials
    creds_file = Prompt.ask(
        "Path to OAuth credentials JSON file",
        default=config.get('oauth_credentials_file', '')
    )
    if creds_file:
        config['oauth_credentials_file'] = creds_file
    
    # Folders to sync
    folders_str = Prompt.ask(
        "Folders to sync (comma-separated)",
        default=','.join(config.get('folders', ['INBOX', '[Gmail]/Sent Mail']))
    )
    config['folders'] = [f.strip() for f in folders_str.split(',')]
    
    # History
    config['initial_history_days'] = IntPrompt.ask(
        "Initial history days to sync",
        default=config.get('initial_history_days', 30)
    )
    
    # Knowledge base folder
    config['knowledge_base_folder'] = Prompt.ask(
        "Knowledge base folder",
        default=config.get('knowledge_base_folder', 'knowledge_base/emails/gmail')
    )


def _configure_fireflies(config: Dict[str, Any]):
    """Configure Fireflies settings."""
    config['api_key'] = Prompt.ask(
        "Fireflies API key",
        default=config.get('api_key', ''),
        password=True
    )
    
    config['webhook_enabled'] = Confirm.ask(
        "Enable webhook for real-time updates?",
        default=config.get('webhook_enabled', True)
    )
    
    if config['webhook_enabled']:
        config['webhook_secret'] = Prompt.ask(
            "Webhook secret",
            default=config.get('webhook_secret', ''),
            password=True
        )
    
    # History
    config['initial_history_days'] = IntPrompt.ask(
        "Initial history days to sync",
        default=config.get('initial_history_days', 30)
    )
    
    # Duration filters
    config['min_duration_seconds'] = IntPrompt.ask(
        "Minimum meeting duration (seconds)",
        default=config.get('min_duration_seconds', 300)
    )
    
    config['max_duration_seconds'] = IntPrompt.ask(
        "Maximum meeting duration (seconds)",
        default=config.get('max_duration_seconds', 14400)
    )
    
    # Output directory
    config['output_dir'] = Prompt.ask(
        "Output directory",
        default=config.get('output_dir', 'knowledge_base/meetings/fireflies')
    )


def _configure_google_drive(config: Dict[str, Any]):
    """Configure Google Drive settings."""
    # OAuth credentials
    creds_file = Prompt.ask(
        "Path to OAuth credentials JSON file",
        default=config.get('oauth_credentials_file', '')
    )
    if creds_file:
        config['oauth_credentials_file'] = creds_file
    
    # Search patterns
    patterns_str = Prompt.ask(
        "Search patterns (comma-separated)",
        default=','.join(config.get('search_patterns', ['Notes by Gemini']))
    )
    config['search_patterns'] = [p.strip() for p in patterns_str.split(',')]
    
    # Folder IDs
    folder_ids_str = Prompt.ask(
        "Specific folder IDs to search (comma-separated, leave empty for all)",
        default=','.join(config.get('folder_ids', []))
    )
    if folder_ids_str:
        config['folder_ids'] = [f.strip() for f in folder_ids_str.split(',')]
    else:
        config['folder_ids'] = []
    
    # History
    config['initial_history_days'] = IntPrompt.ask(
        "Initial history days to sync",
        default=config.get('initial_history_days', 30)
    )
    
    # Knowledge base folder
    config['knowledge_base_folder'] = Prompt.ask(
        "Knowledge base folder",
        default=config.get('knowledge_base_folder', 'knowledge_base/meetings/gemini')
    )


@datasources.command()
@click.argument('source', type=click.Choice(['gmail', 'fireflies', 'google_drive', 'all']))
def sync(source: str):
    """Manually sync a data source."""
    async def _sync():
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"Syncing {source}...", total=None)
                
                # Initialize orchestrator
                orchestrator = DataSourceOrchestrator()
                await orchestrator.initialize_sources()
                
                # Perform sync
                if source == 'all':
                    results = await orchestrator.sync_all()
                    
                    # Display results
                    for source_type, result in results.items():
                        console.print(f"\n[bold]{source_type.value.title()}:[/bold]")
                        console.print(f"  Items processed: {result.items_processed}")
                        console.print(f"  Items failed: {result.items_failed}")
                        if result.errors:
                            console.print(f"  Errors: {len(result.errors)}")
                else:
                    source_type = SourceType(source)
                    result = await orchestrator.sync_source(source_type)
                    
                    console.print(f"\n[bold]{source.title()} Sync Results:[/bold]")
                    console.print(f"  Items processed: {result.items_processed}")
                    console.print(f"  Items failed: {result.items_failed}")
                    
                    if result.errors:
                        console.print(f"\n[yellow]Errors:[/yellow]")
                        for error in result.errors[:5]:  # Show first 5 errors
                            console.print(f"  - {error}")
                        if len(result.errors) > 5:
                            console.print(f"  ... and {len(result.errors) - 5} more")
                    
                    # Show deduplication stats if available
                    if hasattr(result, 'metadata') and 'deduplication' in result.metadata:
                        dedup_info = result.metadata['deduplication']
                        console.print(f"\n[bold]Deduplication:[/bold]")
                        console.print(f"  Duplicates found: {dedup_info['duplicates_found']}")
                        console.print(f"  Documents kept: {dedup_info['documents_kept']}")
                
                progress.update(task, completed=True)
                
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_sync())


@datasources.command()
@click.argument('source', type=click.Choice(['gmail', 'fireflies', 'google_drive']))
def auth(source: str):
    """Authenticate a data source."""
    async def _auth():
        try:
            console.print(f"[bold]Authenticating {source.title()}...[/bold]")
            
            # Initialize orchestrator
            orchestrator = DataSourceOrchestrator()
            await orchestrator.initialize_sources()
            
            # Get the source
            source_type = SourceType(source)
            if source_type not in orchestrator.sources:
                console.print(f"[red]{source.title()} is not enabled. Run 'vdq datasources configure' first.[/red]")
                return
            
            data_source = orchestrator.sources[source_type]
            
            # Perform authentication
            success = await data_source.authenticate()
            
            if success:
                console.print(f"[green]✅ {source.title()} authenticated successfully![/green]")
            else:
                console.print(f"[red]❌ {source.title()} authentication failed[/red]")
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_auth())


@datasources.command()
def test():
    """Test data source connections."""
    async def _test():
        try:
            console.print(Panel("🧪 Testing Data Source Connections", style="bold blue"))
            
            # Initialize orchestrator
            orchestrator = DataSourceOrchestrator()
            await orchestrator.initialize_sources()
            
            # Test each enabled source
            config = get_config()
            ds_config = config.get('data_sources', {})
            
            for source_type in SourceType:
                source_config = ds_config.get(source_type.value, {})
                if not source_config.get('enabled', False):
                    continue
                
                console.print(f"\n[bold]Testing {source_type.value.title()}...[/bold]")
                
                if source_type in orchestrator.sources:
                    data_source = orchestrator.sources[source_type]
                    
                    # Test authentication
                    auth_success = await data_source.test_connection()
                    
                    if auth_success:
                        console.print(f"  ✅ Connection successful")
                        
                        # Get some metrics
                        metrics = await data_source.get_metrics()
                        if 'total_items' in metrics:
                            console.print(f"  📊 Total items: {metrics['total_items']}")
                    else:
                        console.print(f"  ❌ Connection failed")
                else:
                    console.print(f"  ⚠️  Source not initialized")
                    
        except Exception as e:
            logger.error(f"Test failed: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_test())


@datasources.command()
@click.option('--days', default=90, help='Clean up entries older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned up')
def cleanup(days: int, dry_run: bool):
    """Clean up old data and cache."""
    async def _cleanup():
        try:
            console.print(f"[bold]Cleaning up data older than {days} days...[/bold]")
            
            if dry_run:
                console.print("[yellow]DRY RUN - No changes will be made[/yellow]")
            
            # Initialize orchestrator
            orchestrator = DataSourceOrchestrator()
            
            # Clean up deduplication cache
            if not dry_run:
                removed = orchestrator.cleanup_old_duplicates(days)
                console.print(f"✅ Removed {removed} old deduplication entries")
            else:
                console.print("Would clean up deduplication cache")
            
            # TODO: Add cleanup for processed files, logs, etc.
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(_cleanup())


if __name__ == "__main__":
    datasources()