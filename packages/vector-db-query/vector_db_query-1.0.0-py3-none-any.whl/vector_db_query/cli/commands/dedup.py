"""CLI commands for managing content deduplication."""

import click
import asyncio
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ...data_sources.deduplication import ContentDeduplicator
from ...data_sources.orchestrator import DataSourceOrchestrator
from ...utils.logger import get_logger
from ...utils.config import get_config

console = Console()
logger = get_logger(__name__)


@click.group()
def dedup():
    """Manage content deduplication for data sources."""
    pass


@dedup.command()
def status():
    """Show deduplication statistics and status."""
    try:
        # Initialize deduplicator
        config = get_config()
        cache_dir = Path(config.get('data_sources', {}).get('deduplication', {}).get('cache_dir', '.cache/deduplication'))
        deduplicator = ContentDeduplicator(cache_dir)
        
        # Get statistics
        stats = deduplicator.get_statistics()
        
        # Display overall statistics
        console.print(Panel.fit(
            f"[bold]Deduplication Status[/bold]\n"
            f"Total Documents: {stats['total_documents']:,}\n"
            f"Cache Directory: {stats['cache']['cache_directory']}",
            border_style="cyan"
        ))
        
        # Display per-source statistics
        if stats['sources']:
            table = Table(title="Documents by Source")
            table.add_column("Source", style="cyan")
            table.add_column("Unique Documents", style="green", justify="right")
            table.add_column("Total Registered", style="yellow", justify="right")
            
            for source, source_stats in stats['sources'].items():
                table.add_row(
                    source.title(),
                    f"{source_stats['unique_documents']:,}",
                    f"{source_stats['total_registered']:,}"
                )
            
            console.print(table)
        
        # Display configuration
        dedup_config = config.get('data_sources', {}).get('deduplication', {})
        console.print("\n[bold]Configuration:[/bold]")
        console.print(f"  Enabled: {'✅' if dedup_config.get('enabled', True) else '❌'}")
        console.print(f"  Similarity Threshold: {dedup_config.get('similarity_threshold', 0.95):.0%}")
        console.print(f"  Cross-Source Check: {'✅' if dedup_config.get('cross_source_check', True) else '❌'}")
        console.print(f"  Skip Duplicates: {'✅' if dedup_config.get('skip_duplicates', True) else '❌'}")
        
    except Exception as e:
        logger.error(f"Failed to get deduplication status: {e}")
        console.print(f"[red]Error: {e}[/red]")


@dedup.command()
@click.option('--days', default=90, help='Remove entries older than N days')
@click.option('--dry-run', is_flag=True, help='Show what would be removed without removing')
def cleanup(days: int, dry_run: bool):
    """Clean up old deduplication cache entries."""
    try:
        # Initialize deduplicator
        config = get_config()
        cache_dir = Path(config.get('data_sources', {}).get('deduplication', {}).get('cache_dir', '.cache/deduplication'))
        deduplicator = ContentDeduplicator(cache_dir)
        
        if dry_run:
            console.print(f"[yellow]DRY RUN: Would remove entries older than {days} days[/yellow]")
            # TODO: Add dry run functionality to deduplicator
            console.print("[yellow]Dry run not yet implemented[/yellow]")
        else:
            console.print(f"[yellow]Cleaning up entries older than {days} days...[/yellow]")
            removed_count = deduplicator.cleanup_old_entries(days)
            console.print(f"[green]✓ Removed {removed_count} old entries[/green]")
            
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@dedup.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--source', type=click.Choice(['gmail', 'fireflies', 'google_drive']), help='Source type')
@click.option('--threshold', type=float, default=0.95, help='Similarity threshold (0.0-1.0)')
def check(file_path: str, source: str, threshold: float):
    """Check if a file is a duplicate."""
    try:
        from ...data_sources.models import ProcessedDocument
        
        # Initialize deduplicator
        config = get_config()
        cache_dir = Path(config.get('data_sources', {}).get('deduplication', {}).get('cache_dir', '.cache/deduplication'))
        deduplicator = ContentDeduplicator(cache_dir)
        
        # Read file content
        file_path = Path(file_path)
        content = file_path.read_text(encoding='utf-8')
        
        # Create a ProcessedDocument
        doc = ProcessedDocument(
            source_id=f"test_{file_path.stem}",
            source_type=source or "unknown",
            title=file_path.name,
            content=content,
            metadata={'file_path': str(file_path)}
        )
        
        # Check for duplicates
        result = deduplicator.check_duplicate(doc, source_type=source, threshold=threshold)
        
        # Display result
        if result.is_duplicate:
            console.print(Panel.fit(
                f"[red]🔁 DUPLICATE FOUND[/red]\n"
                f"Similarity: {result.similarity:.0%}\n"
                f"Match Type: {result.match_type}\n"
                f"Duplicate Of: {result.duplicate_of}\n"
                f"Source: {result.duplicate_source}",
                border_style="red"
            ))
            
            if result.metadata:
                console.print("\n[bold]Original Document:[/bold]")
                console.print(f"  Title: {result.metadata.get('existing_title', 'N/A')}")
                console.print(f"  Date: {result.metadata.get('existing_date', 'N/A')}")
        else:
            console.print(Panel.fit(
                f"[green]✅ NOT A DUPLICATE[/green]\n"
                f"This document appears to be unique",
                border_style="green"
            ))
            
    except Exception as e:
        logger.error(f"Failed to check file: {e}")
        console.print(f"[red]Error: {e}[/red]")


@dedup.command()
def test():
    """Test deduplication with sample data."""
    try:
        from ...data_sources.models import ProcessedDocument
        
        # Initialize deduplicator
        config = get_config()
        cache_dir = Path(config.get('data_sources', {}).get('deduplication', {}).get('cache_dir', '.cache/deduplication'))
        deduplicator = ContentDeduplicator(cache_dir)
        
        # Create test documents
        test_docs = [
            ProcessedDocument(
                source_id="test1",
                source_type="gmail",
                title="Meeting Notes - Project X",
                content="This is a test meeting about Project X. We discussed timelines and deliverables.",
                metadata={'sender': 'test@example.com'}
            ),
            ProcessedDocument(
                source_id="test2",
                source_type="gmail",
                title="Re: Meeting Notes - Project X",
                content="This is a test meeting about Project X. We discussed timelines and deliverables.",
                metadata={'sender': 'test@example.com'}
            ),
            ProcessedDocument(
                source_id="test3",
                source_type="fireflies",
                title="Project X Meeting",
                content="Transcript: This is a test meeting about Project X. We discussed different timelines.",
                metadata={'meeting_id': '12345'}
            ),
            ProcessedDocument(
                source_id="test4",
                source_type="google_drive",
                title="Completely Different Document",
                content="This document is about something completely different - Project Y.",
                metadata={'file_id': 'abc123'}
            )
        ]
        
        # Test deduplication
        console.print("[bold]Testing Deduplication:[/bold]\n")
        
        for i, doc in enumerate(test_docs, 1):
            console.print(f"[cyan]Document {i}: {doc.title}[/cyan]")
            
            # Check for duplicates
            result = deduplicator.check_duplicate(doc, threshold=0.8)
            
            if result.is_duplicate:
                console.print(f"  [red]→ Duplicate of {result.duplicate_of} (similarity: {result.similarity:.0%})[/red]")
            else:
                console.print(f"  [green]→ Unique document[/green]")
                # Register it
                deduplicator.register_document(doc)
            
            console.print()
        
        # Show final statistics
        stats = deduplicator.get_statistics()
        console.print(f"\n[bold]Test Complete:[/bold]")
        console.print(f"Total Documents Registered: {stats['total_documents']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


@dedup.command()
@click.option('--enabled/--disabled', default=True, help='Enable or disable deduplication')
@click.option('--threshold', type=float, help='Similarity threshold (0.0-1.0)')
@click.option('--cross-source/--no-cross-source', default=True, help='Check across all sources')
@click.option('--skip/--no-skip', default=True, help='Skip duplicate documents')
def configure(enabled: bool, threshold: float, cross_source: bool, skip: bool):
    """Configure deduplication settings."""
    try:
        # This would normally update the configuration file
        console.print("[yellow]Configuration update not yet implemented[/yellow]")
        console.print("\nRequested settings:")
        console.print(f"  Enabled: {'✅' if enabled else '❌'}")
        if threshold is not None:
            console.print(f"  Threshold: {threshold:.0%}")
        console.print(f"  Cross-Source: {'✅' if cross_source else '❌'}")
        console.print(f"  Skip Duplicates: {'✅' if skip else '❌'}")
        
        console.print("\n[yellow]To apply these settings, manually update config/default.yaml[/yellow]")
        
    except Exception as e:
        logger.error(f"Configuration failed: {e}")
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    dedup()