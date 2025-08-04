"""CLI commands for Fireflies.ai integration."""

import click
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...data_sources.fireflies import (
    FirefliesConfig,
    FirefliesClient,
    FirefliesDataSource
)
from ...utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def fireflies():
    """Manage Fireflies.ai integration."""
    pass


@fireflies.command()
@click.option("--api-key", prompt=True, hide_input=True, help="Fireflies API key")
@click.option("--webhook-secret", prompt=True, hide_input=True, help="Webhook secret")
@click.option("--output-dir", type=click.Path(), help="Output directory for transcripts")
def configure(api_key: str, webhook_secret: str, output_dir: str):
    """Configure Fireflies integration."""
    try:
        # Create configuration
        config = FirefliesConfig(
            api_key=api_key,
            webhook_secret=webhook_secret
        )
        
        if output_dir:
            config.output_dir = Path(output_dir)
        
        # Test connection
        console.print("[yellow]Testing Fireflies API connection...[/yellow]")
        
        async def test():
            client = FirefliesClient(config)
            return await client.test_connection()
        
        success = asyncio.run(test())
        
        if success:
            console.print("[green]✓ Successfully connected to Fireflies API![/green]")
            
            # Save configuration
            # TODO: Implement config saving
            console.print("\n[yellow]Configuration saved (feature coming soon)[/yellow]")
            
            # Show webhook URL
            console.print("\n[bold]Webhook Configuration:[/bold]")
            console.print(f"URL: https://your-domain.com/api/webhooks/fireflies")
            console.print(f"Secret: {webhook_secret}")
            console.print("\nConfigure this webhook in your Fireflies settings.")
            
        else:
            console.print("[red]✗ Failed to connect to Fireflies API[/red]")
            
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@fireflies.command()
@click.option("--days", default=7, help="Fetch transcripts from last N days")
@click.option("--limit", default=10, help="Maximum number of transcripts")
def list(days: int, limit: int):
    """List recent transcripts."""
    try:
        async def list_transcripts():
            # Load config
            config = FirefliesConfig()  # TODO: Load from saved config
            client = FirefliesClient(config)
            
            # Fetch transcripts
            since = datetime.utcnow() - timedelta(days=days)
            transcripts = await client.list_transcripts(since=since, limit=limit)
            
            if not transcripts:
                console.print("[yellow]No transcripts found[/yellow]")
                return
            
            # Display in table
            table = Table(title=f"Recent Transcripts (Last {days} days)")
            table.add_column("Date", style="cyan")
            table.add_column("Title", style="yellow")
            table.add_column("Duration", style="green")
            table.add_column("Participants", style="blue")
            table.add_column("Platform", style="magenta")
            
            for t in transcripts:
                date = datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                duration_min = t.get('duration', 0) // 60
                participants = len(t.get('participants', []))
                platform = t.get('organizer_platform', 'Unknown')
                
                table.add_row(
                    date.strftime("%Y-%m-%d %H:%M"),
                    t.get('title', 'Untitled')[:50],
                    f"{duration_min} min",
                    str(participants),
                    platform
                )
            
            console.print(table)
        
        asyncio.run(list_transcripts())
        
    except Exception as e:
        logger.error(f"Failed to list transcripts: {e}")
        console.print(f"[red]Error: {e}[/red]")


@fireflies.command()
@click.option("--days", default=30, help="Sync transcripts from last N days")
@click.option("--limit", default=100, help="Maximum number of transcripts")
def sync(days: int, limit: int):
    """Sync Fireflies transcripts to knowledge base."""
    try:
        async def run_sync():
            # Load config
            config = FirefliesConfig()  # TODO: Load from saved config
            source = FirefliesDataSource(config)
            
            # Authenticate
            console.print("[yellow]Authenticating with Fireflies...[/yellow]")
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
            console.print(f"Items fetched: {result.items_fetched}")
            console.print(f"Items processed: {result.items_processed}")
            
            if result.errors:
                console.print(f"\n[red]Errors ({len(result.errors)}):[/red]")
                for error in result.errors[:5]:  # Show first 5 errors
                    console.print(f"  - {error}")
            
            if result.success:
                console.print("\n[green]✓ Sync completed successfully![/green]")
            else:
                console.print("\n[red]✗ Sync failed[/red]")
        
        asyncio.run(run_sync())
        
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@fireflies.command()
@click.argument("transcript_id")
def fetch(transcript_id: str):
    """Fetch and display a specific transcript."""
    try:
        async def fetch_transcript():
            # Load config
            config = FirefliesConfig()  # TODO: Load from saved config
            client = FirefliesClient(config)
            
            # Fetch transcript
            console.print(f"[yellow]Fetching transcript {transcript_id}...[/yellow]")
            transcript = await client.get_transcript(transcript_id)
            
            # Display transcript
            panel = Panel.fit(
                f"[bold]{transcript.title}[/bold]\n"
                f"Date: {transcript.date.strftime('%Y-%m-%d %H:%M UTC')}\n"
                f"Duration: {transcript.duration // 60} minutes\n"
                f"Participants: {', '.join(transcript.participants)}",
                title="Transcript Details",
                border_style="green"
            )
            console.print(panel)
            
            if transcript.summary:
                console.print("\n[bold]Summary:[/bold]")
                console.print(transcript.summary)
            
            if transcript.action_items:
                console.print("\n[bold]Action Items:[/bold]")
                for item in transcript.action_items:
                    console.print(f"• {item}")
            
            console.print("\n[bold]Transcript Preview:[/bold]")
            preview = transcript.transcript_text[:500]
            if len(transcript.transcript_text) > 500:
                preview += "..."
            console.print(preview)
        
        asyncio.run(fetch_transcript())
        
    except Exception as e:
        logger.error(f"Failed to fetch transcript: {e}")
        console.print(f"[red]Error: {e}[/red]")


@fireflies.command()
def status():
    """Check Fireflies integration status."""
    try:
        async def check_status():
            # Load config
            config = FirefliesConfig()  # TODO: Load from saved config
            source = FirefliesDataSource(config)
            
            # Get status
            status_info = await source.get_status()
            
            # Display status
            table = Table(title="Fireflies Integration Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="yellow")
            
            table.add_row("API Connected", "✓" if status_info.get("api_connected") else "✗")
            table.add_row("Webhook Enabled", "✓" if status_info.get("webhook_enabled") else "✗")
            table.add_row("Webhook Events", str(status_info.get("webhook_events", 0)))
            table.add_row("Items Processed", str(status_info.get("items_processed", 0)))
            table.add_row("Last Sync", status_info.get("last_sync_time", "Never"))
            
            if "api_quota" in status_info:
                quota = status_info["api_quota"]
                table.add_row("API Usage", f"{quota['used']}/{quota['limit']} minutes")
            
            console.print(table)
            
            # Show filters
            if status_info.get("platform_filters"):
                console.print("\n[bold]Platform Filters:[/bold]")
                for platform in status_info["platform_filters"]:
                    console.print(f"  • {platform}")
            
            console.print(f"\n[bold]Duration Filter:[/bold] {status_info.get('min_duration_filter', 0)}s minimum")
        
        asyncio.run(check_status())
        
    except Exception as e:
        logger.error(f"Failed to check status: {e}")
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    fireflies()