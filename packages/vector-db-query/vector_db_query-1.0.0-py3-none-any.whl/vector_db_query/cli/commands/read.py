"""Read command for Vector DB Query CLI."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from vector_db_query.universal_reader import UniversalVDBReader
from vector_db_query.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.option(
    "--collection", "-c",
    type=str,
    help="Collection name to read from"
)
@click.option(
    "--all", "-a",
    is_flag=True,
    help="Read from all collections"
)
@click.option(
    "--limit", "-l",
    type=int,
    default=50,
    help="Maximum documents to display (default: 50)"
)
@click.option(
    "--export", "-e",
    type=click.Path(path_type=Path),
    help="Export to file (supports .json, .jsonl, .csv)"
)
@click.option(
    "--search", "-s",
    type=str,
    help="Search query to filter results"
)
@click.option(
    "--stats",
    is_flag=True,
    help="Show collection statistics only"
)
def read_command(
    collection: Optional[str],
    all: bool,
    limit: int,
    export: Optional[Path],
    search: Optional[str],
    stats: bool
):
    """Read documents from vector database collections.
    
    Read and display documents stored in Qdrant collections,
    with support for searching and exporting.
    """
    console.print(Panel("[bold cyan]Vector Database Reader[/bold cyan]", expand=False))
    
    try:
        reader = UniversalVDBReader()
        
        # Show statistics
        if stats:
            show_statistics(reader)
            return
            
        # Handle search
        if search:
            search_collections(reader, search, collection, limit)
            return
            
        # Handle reading
        if all:
            read_all_collections(reader, limit, export)
        elif collection:
            read_single_collection(reader, collection, limit, export)
        else:
            # No collection specified, show available collections
            console.print("\n[yellow]No collection specified. Available collections:[/yellow]\n")
            show_statistics(reader)
            console.print("\n[dim]Use --collection <name> to read a specific collection[/dim]")
            console.print("[dim]Use --all to read from all collections[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        logger.error(f"Read command error: {e}")
        raise click.Abort()


def show_statistics(reader: UniversalVDBReader):
    """Show collection statistics."""
    stats = reader.get_statistics()
    
    table = Table(title="Vector Database Collections", show_header=True)
    table.add_column("Collection", style="cyan")
    table.add_column("Documents", justify="right", style="yellow")
    table.add_column("Dimension", justify="right", style="green")
    table.add_column("Status", style="blue")
    
    total_docs = 0
    for name, info in sorted(stats.items()):
        if 'error' not in info:
            count = info.get('points_count', 0)
            dimension = info.get('dimension', '-')
            status = info.get('status', 'unknown')
            
            table.add_row(name, f"{count:,}", str(dimension), status)
            total_docs += count
        else:
            table.add_row(name, "-", "-", f"[red]Error[/red]")
            
    console.print(table)
    console.print(f"\n[bold]Total documents: {total_docs:,}[/bold]")


def search_collections(
    reader: UniversalVDBReader,
    query: str,
    collection: Optional[str],
    limit: int
):
    """Search collections and display results."""
    console.print(f"\n[yellow]Searching for: '{query}'[/yellow]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Searching...", total=None)
        
        if collection:
            results = reader.search_unified(query, [collection], limit)
        else:
            results = reader.search_unified(query, None, limit)
            
        progress.update(task, completed=True)
    
    # Display results
    if not any(results.values()):
        console.print("[dim]No results found[/dim]")
        return
        
    for collection_name, collection_results in results.items():
        if collection_results:
            console.print(f"\n[bold cyan]{collection_name}[/bold cyan] ({len(collection_results)} results)")
            console.print("-" * 50)
            
            for i, result in enumerate(collection_results, 1):
                score = result.get('score', 0.0)
                source = Path(result.get('source', 'Unknown')).name
                content = result.get('content', '')
                
                # Clean and truncate
                content = ' '.join(content.split())
                if len(content) > 200:
                    content = content[:197] + "..."
                    
                console.print(f"\n[yellow]{i}.[/yellow] Score: {score:.4f} | Source: [cyan]{source}[/cyan]")
                console.print(f"   {content}")


def read_single_collection(
    reader: UniversalVDBReader,
    collection: str,
    limit: int,
    export: Optional[Path]
):
    """Read from a single collection."""
    console.print(f"\n[cyan]Reading from collection: {collection}[/cyan]\n")
    
    if export:
        # Export to file
        export_collection(reader, collection, export)
    else:
        # Display documents
        display_documents(reader, collection, limit)


def read_all_collections(
    reader: UniversalVDBReader,
    limit: int,
    export: Optional[Path]
):
    """Read from all collections."""
    stats = reader.get_statistics()
    collections = [name for name, info in stats.items() if 'error' not in info]
    
    if export:
        console.print("[red]Export all collections not supported yet[/red]")
        return
        
    console.print(f"\n[cyan]Reading from {len(collections)} collections[/cyan]\n")
    
    for collection in collections:
        console.print(f"\n[bold]Collection: {collection}[/bold]")
        console.print("-" * 40)
        display_documents(reader, collection, min(limit, 10))  # Limit per collection


def display_documents(
    reader: UniversalVDBReader,
    collection: str,
    limit: int
):
    """Display documents from a collection."""
    count = 0
    
    try:
        for doc in reader.read_all_documents(collection, batch_size=100):
            count += 1
            
            # Extract fields
            doc_id = doc.get('id', 'unknown')
            source = Path(doc.get('source', 'Unknown')).name
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            
            # Clean content
            content = ' '.join(content.split())
            if len(content) > 300:
                content = content[:297] + "..."
                
            # Display
            console.print(f"\n[yellow]Document {count}[/yellow] (ID: {doc_id})")
            console.print(f"Source: [cyan]{source}[/cyan]")
            
            if metadata:
                meta_str = ", ".join(f"{k}={v}" for k, v in metadata.items() 
                                   if k in ['file_type', 'chunk_index', 'created_at'])
                if meta_str:
                    console.print(f"Metadata: [dim]{meta_str}[/dim]")
                    
            console.print(f"\n{content}\n")
            console.print("-" * 70)
            
            if count >= limit:
                remaining = "unknown"
                try:
                    info = reader.query_system.get_collection_info(collection)
                    total = info.points_count
                    remaining = total - count
                except:
                    pass
                    
                console.print(f"\n[dim]Showing first {count} documents. "
                            f"Remaining: {remaining}[/dim]")
                break
                
    except Exception as e:
        console.print(f"\n[red]Error reading documents: {e}[/red]")
        logger.error(f"Error reading from {collection}: {e}")


def export_collection(
    reader: UniversalVDBReader,
    collection: str,
    export_path: Path
):
    """Export collection to file."""
    # Determine format from extension
    suffix = export_path.suffix.lower()
    format_map = {
        '.json': 'json',
        '.jsonl': 'jsonl',
        '.csv': 'csv'
    }
    
    format = format_map.get(suffix, 'jsonl')
    
    console.print(f"Exporting to: [cyan]{export_path}[/cyan]")
    console.print(f"Format: [yellow]{format}[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Exporting...", total=None)
        
        count = reader.export_collection(collection, export_path, format)
        
        progress.update(task, completed=True)
        
    console.print(f"\n[green]✓ Exported {count} documents to {export_path}[/green]")