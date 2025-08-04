"""CLI commands for Google Drive integration."""

import click
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...data_sources.googledrive import (
    GoogleDriveConfig,
    GoogleDriveClient,
    GoogleDriveDataSource
)
from ...utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def googledrive():
    """Manage Google Drive integration for Gemini transcripts."""
    pass


@googledrive.command()
@click.option("--credentials-file", type=click.Path(exists=True), required=True, help="OAuth2 credentials JSON file")
@click.option("--token-file", default=".gdrive_token.json", help="Token storage file")
@click.option("--output-dir", type=click.Path(), help="Output directory for transcripts")
def configure(credentials_file: str, token_file: str, output_dir: str):
    """Configure Google Drive integration."""
    try:
        # Create configuration
        config = GoogleDriveConfig(
            oauth_credentials_file=credentials_file,
            oauth_token_file=token_file
        )
        
        if output_dir:
            config.knowledge_base_folder = output_dir
        
        # Validate configuration
        errors = config.validate()
        if errors:
            for error in errors:
                console.print(f"[red]Error: {error}[/red]")
            return
        
        # Test connection
        console.print("[yellow]Testing Google Drive connection...[/yellow]")
        
        async def test():
            client = GoogleDriveClient(config)
            success = await client.connect()
            
            if success:
                user_info = await client.get_user_info()
                user = user_info.get('user', {})
                return True, user
            return False, None
        
        success, user = asyncio.run(test())
        
        if success:
            console.print("[green]✓ Successfully connected to Google Drive![/green]")
            if user:
                console.print(f"Connected as: {user.get('emailAddress', 'Unknown')}")
            
            # Save configuration
            # TODO: Implement config saving
            console.print("\n[yellow]Configuration saved (feature coming soon)[/yellow]")
            
            # Show search patterns
            console.print("\n[bold]Search Configuration:[/bold]")
            console.print("Patterns: " + ", ".join(config.search_patterns))
            console.print(f"Output: {config.knowledge_base_folder}")
            
        else:
            console.print("[red]✗ Failed to connect to Google Drive[/red]")
            console.print("Please check your credentials file")
            
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
@click.option("--days", default=30, help="Search files modified in last N days")
@click.option("--limit", default=20, help="Maximum number of files")
def search(days: int, limit: int):
    """Search for Gemini transcripts in Google Drive."""
    try:
        async def search_transcripts():
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            
            # Validate
            errors = config.validate()
            if errors:
                console.print("[red]Configuration not valid. Run 'vdq googledrive configure' first.[/red]")
                return
            
            client = GoogleDriveClient(config)
            
            # Connect
            if not await client.connect():
                console.print("[red]Failed to connect to Google Drive[/red]")
                return
            
            # Search
            since = datetime.utcnow() - timedelta(days=days)
            files = await client.search_gemini_transcripts(since=since, limit=limit)
            
            if not files:
                console.print("[yellow]No Gemini transcripts found[/yellow]")
                return
            
            # Display results
            table = Table(title=f"Gemini Transcripts (Last {days} days)")
            table.add_column("Modified", style="cyan")
            table.add_column("Name", style="yellow")
            table.add_column("Size", style="green")
            table.add_column("ID", style="dim")
            
            for file_info in files:
                modified = datetime.fromisoformat(file_info['modifiedTime'].replace('Z', '+00:00'))
                size = int(file_info.get('size', 0))
                size_mb = size / (1024 * 1024)
                
                table.add_row(
                    modified.strftime("%Y-%m-%d %H:%M"),
                    file_info['name'][:50],
                    f"{size_mb:.1f} MB",
                    file_info['id'][:12]
                )
            
            console.print(table)
        
        asyncio.run(search_transcripts())
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
@click.option("--days", default=30, help="Sync files modified in last N days")
@click.option("--limit", default=100, help="Maximum number of files")
def sync(days: int, limit: int):
    """Sync Gemini transcripts to knowledge base."""
    try:
        async def run_sync():
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            source = GoogleDriveDataSource(config)
            
            # Authenticate
            console.print("[yellow]Authenticating with Google Drive...[/yellow]")
            if not await source.authenticate():
                console.print("[red]Authentication failed[/red]")
                return
            
            console.print("[green]✓ Authenticated[/green]")
            
            # Run sync
            since = datetime.utcnow() - timedelta(days=days)
            console.print(f"\n[yellow]Syncing transcripts since {since.strftime('%Y-%m-%d')}...[/yellow]")
            
            with console.status("[bold green]Syncing...") as status:
                result = await source.sync(since=since, limit=limit)
            
            # Display results
            console.print("\n[bold]Sync Results:[/bold]")
            console.print(f"Files found: {result.items_fetched}")
            console.print(f"Files processed: {result.items_processed}")
            
            if result.errors:
                console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
                for error in result.errors[:5]:  # Show first 5 errors
                    console.print(f"  - {error}")
            
            if result.success:
                console.print("\n[green]✓ Sync completed successfully![/green]")
                console.print(f"Transcripts saved to: {config.knowledge_base_folder}")
            else:
                console.print("\n[red]✗ Sync failed[/red]")
        
        asyncio.run(run_sync())
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
@click.argument("file_id")
def fetch(file_id: str):
    """Fetch and display a specific file."""
    try:
        async def fetch_file():
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            client = GoogleDriveClient(config)
            
            # Connect
            console.print(f"[yellow]Fetching file {file_id}...[/yellow]")
            if not await client.connect():
                console.print("[red]Failed to connect to Google Drive[/red]")
                return
            
            # Search for the file
            files = await client.search_files(f"'{file_id}' in id", limit=1)
            
            if not files:
                console.print(f"[red]File not found: {file_id}[/red]")
                return
            
            file_info = files[0]
            
            # Get content
            content = await client.get_file_content(file_id, file_info['mimeType'])
            
            # Display file info
            panel = Panel.fit(
                f"[bold]{file_info['name']}[/bold]\n"
                f"Modified: {file_info['modifiedTime']}\n"
                f"Size: {int(file_info.get('size', 0)) / 1024:.1f} KB\n"
                f"Link: {file_info.get('webViewLink', 'N/A')}",
                title="File Details",
                border_style="green"
            )
            console.print(panel)
            
            # Show content preview
            console.print("\n[bold]Content Preview:[/bold]")
            preview = content[:1000]
            if len(content) > 1000:
                preview += "\n...(truncated)"
            console.print(preview)
            
            # Check if it's a Gemini transcript
            if any(pattern in content for pattern in ["Notes by Gemini", "Tab 1", "\t"]):
                console.print("\n[green]✓ This appears to be a Gemini transcript[/green]")
        
        asyncio.run(fetch_file())
        
    except Exception as e:
        logger.error(f"Failed to fetch file: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
@click.argument("file_id")
def analyze(file_id: str):
    """Analyze a file to check if it's a Gemini transcript."""
    try:
        async def analyze_file():
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            client = GoogleDriveClient(config)
            
            # Connect
            console.print(f"[yellow]Analyzing file {file_id}...[/yellow]")
            if not await client.connect():
                console.print("[red]Failed to connect to Google Drive[/red]")
                return
            
            # Analyze
            result = await client.analyze_transcript(file_id)
            
            if 'error' in result:
                console.print(f"[red]Error: {result['error']}[/red]")
                return
            
            # Display results
            panel = Panel.fit(
                f"[bold]Analysis Results[/bold]\n"
                f"Valid Gemini Transcript: {'✅ Yes' if result['is_valid'] else '❌ No'}\n"
                f"Confidence: {result['confidence']:.0%}",
                border_style="green" if result['is_valid'] else "red"
            )
            console.print(panel)
            
            # File info
            if 'file_info' in result:
                info = result['file_info']
                console.print("\n[bold]File Information:[/bold]")
                console.print(f"  Name: {info['name']}")
                console.print(f"  Modified: {info['modified_time']}")
                console.print(f"  Size: {info['size'] / 1024:.1f} KB")
            
            # Tabs found
            if result['tabs']:
                console.print(f"\n[bold]Tabs Found ({len(result['tabs'])}):[/bold]")
                for tab in result['tabs']:
                    console.print(f"  Tab {tab['tab_number']}: {tab['name']}")
                    console.print(f"    Content length: {len(tab['content'])} chars")
            
            # Metadata
            if result['metadata']:
                console.print("\n[bold]Extracted Metadata:[/bold]")
                for key, value in result['metadata'].items():
                    if key not in ['warnings']:
                        console.print(f"  {key}: {value}")
            
            # Warnings
            if result.get('warnings'):
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in result['warnings']:
                    console.print(f"  ⚠️  {warning}")
        
        asyncio.run(analyze_file())
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
@click.argument("file_id")
@click.option("--output-dir", type=click.Path(), help="Output directory for processed files")
def process(file_id: str, output_dir: str):
    """Process a Gemini transcript with full pipeline."""
    try:
        async def process_transcript():
            from ...data_sources.googledrive import GeminiProcessingPipeline
            
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            client = GoogleDriveClient(config)
            
            # Connect
            console.print(f"[yellow]Processing transcript {file_id}...[/yellow]")
            if not await client.connect():
                console.print("[red]Failed to connect to Google Drive[/red]")
                return
            
            # Get file
            files = await client.search_files(f"'{file_id}' in id", limit=1)
            if not files:
                console.print(f"[red]File not found: {file_id}[/red]")
                return
            
            file_info = files[0]
            
            # Get content
            content = await client.get_file_content(file_id, file_info['mimeType'])
            file_info['content'] = content
            
            # Process with pipeline
            output_path = Path(output_dir) if output_dir else Path("data/processed/gemini")
            pipeline = GeminiProcessingPipeline(output_path)
            
            with console.status("[bold green]Processing...") as status:
                result = await pipeline.process_transcript(file_info, save_structured=True)
            
            if result['success']:
                console.print("[green]✓ Processing complete![/green]")
                
                # Display results
                structured = result.get('structured_content', {})
                metadata = result.get('metadata', {})
                
                # Summary panel
                if structured.get('summary'):
                    summary_panel = Panel.fit(
                        structured['summary'][:300] + "..." if len(structured.get('summary', '')) > 300 else structured.get('summary', 'No summary'),
                        title="Summary",
                        border_style="cyan"
                    )
                    console.print(summary_panel)
                
                # Key info table
                table = Table(title="Extracted Information")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="yellow")
                
                table.add_row("Meeting Title", structured.get('meeting_title', 'N/A'))
                table.add_row("Date", structured.get('meeting_date', 'N/A'))
                table.add_row("Duration", structured.get('duration', 'N/A'))
                table.add_row("Participants", str(len(structured.get('participants', []))))
                table.add_row("Tabs", str(len(structured.get('tabs', {}))))
                table.add_row("Action Items", str(len(structured.get('action_items', []))))
                table.add_row("Key Topics", str(len(structured.get('key_topics', []))))
                table.add_row("Confidence", f"{metadata.get('confidence', 0):.0%}")
                
                console.print(table)
                
                # Action items
                if structured.get('action_items'):
                    console.print("\n[bold]Action Items:[/bold]")
                    for item in structured['action_items'][:5]:
                        if 'assignee' in item:
                            console.print(f"  • [{item['assignee']}] {item['task']}")
                        else:
                            console.print(f"  • {item['task']}")
                    if len(structured['action_items']) > 5:
                        console.print(f"  ... and {len(structured['action_items']) - 5} more")
                
                # Output location
                console.print(f"\n[green]Output saved to: {output_path}[/green]")
                
            else:
                console.print(f"[red]✗ Processing failed: {result.get('error', 'Unknown error')}[/red]")
        
        asyncio.run(process_transcript())
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@googledrive.command()
def status():
    """Check Google Drive integration status."""
    try:
        async def check_status():
            # Load config
            config = GoogleDriveConfig()  # TODO: Load from saved config
            source = GoogleDriveDataSource(config)
            
            # Get status
            status_info = await source.get_status()
            
            # Display status
            table = Table(title="Google Drive Integration Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("Connected", "✓" if status_info.get("connected") else "✗")
            table.add_row("Search Patterns", ", ".join(status_info.get("search_patterns", [])))
            table.add_row("Output Directory", status_info.get("output_dir", "Not set"))
            table.add_row("Items Processed", str(status_info.get("items_processed", 0)))
            table.add_row("Last Sync", status_info.get("last_sync_time", "Never"))
            
            if "storage_quota" in status_info:
                quota = status_info["storage_quota"]
                table.add_row(
                    "Storage Usage",
                    f"{quota['used_gb']} / {quota['limit_gb']} GB ({quota['percent_used']}%)"
                )
            
            console.print(table)
            
            # Show folder filters if configured
            folder_ids = status_info.get("folder_ids", [])
            if folder_ids:
                console.print("\n[bold]Folder Filters:[/bold]")
                for folder_id in folder_ids:
                    console.print(f"  • {folder_id}")
        
        asyncio.run(check_status())
        
    except Exception as e:
        logger.error(f"Failed to check status: {e}")
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    googledrive()