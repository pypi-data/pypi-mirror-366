"""Vector database CLI commands."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from vector_db_query.vector_db import VectorDBService
from vector_db_query.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.group()
def vector():
    """Vector database management commands."""
    pass


@vector.command()
@click.option("--timeout", "-t", type=int, default=60, help="Initialization timeout in seconds")
def init(timeout: int):
    """Initialize the vector database system."""
    console.print(Panel("[bold cyan]Vector Database Initialization[/bold cyan]", expand=False))
    
    try:
        service = VectorDBService(auto_start=False)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing vector database...", total=None)
            
            if service.initialize(timeout=timeout):
                console.print("\n[bold green]✓ Vector database initialized successfully![/bold green]")
            else:
                console.print("\n[bold red]✗ Failed to initialize vector database[/bold red]")
                raise click.Abort()
                
    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        raise click.Abort()


@vector.command()
def status():
    """Check vector database status."""
    console.print(Panel("[bold cyan]Vector Database Status[/bold cyan]", expand=False))
    
    try:
        service = VectorDBService(auto_start=False)
        status_info = service.get_status()
        
        # General status
        general_table = Table(show_header=False, box=None)
        general_table.add_column("Property", style="cyan")
        general_table.add_column("Value", style="yellow")
        
        general_table.add_row("Service Initialized", "✓" if status_info["service_initialized"] else "✗")
        general_table.add_row("Docker Running", "✓" if status_info["docker_running"] else "✗")
        general_table.add_row("Client Connected", "✓" if status_info["client_connected"] else "✗")
        
        console.print("\n[bold]General Status:[/bold]")
        console.print(general_table)
        
        # Health status
        if status_info.get("health_status"):
            health = status_info["health_status"]
            if health["is_healthy"]:
                console.print(f"\n[bold green]Health: OK[/bold green] (Version: {health.get('version', 'unknown')})")
            else:
                console.print(f"\n[bold red]Health: ERROR[/bold red] - {health.get('error', 'Unknown error')}")
                
        # Storage stats
        if status_info.get("storage_stats"):
            stats = status_info["storage_stats"]
            console.print(f"\n[bold]Storage Statistics:[/bold]")
            console.print(f"  Total Collections: {stats['total_collections']}")
            console.print(f"  Total Vectors: {stats['total_vectors']}")
            
        # Collections
        if status_info.get("collections"):
            console.print("\n[bold]Collections:[/bold]")
            
            collections_table = Table(show_header=True, header_style="bold magenta")
            collections_table.add_column("Name", style="cyan")
            collections_table.add_column("Vectors", justify="right")
            collections_table.add_column("Vector Size", justify="right")
            collections_table.add_column("Status", justify="center")
            
            for col in status_info["collections"]:
                status_icon = "✓" if col["status"].lower() in ["green", "ready"] else "⚠"
                collections_table.add_row(
                    col["name"],
                    str(col["vectors"]),
                    str(col["vector_size"]),
                    status_icon
                )
                
            console.print(collections_table)
            
        # Docker info
        if status_info.get("docker_info") and status_info["docker_info"].get("status") != "not_found":
            docker = status_info["docker_info"]
            console.print(f"\n[bold]Docker Container:[/bold]")
            console.print(f"  ID: {docker.get('id', 'unknown')}")
            console.print(f"  Status: {docker.get('status', 'unknown')}")
            
    except Exception as e:
        console.print(f"[bold red]Error checking status: {e}[/bold red]")


@vector.command()
@click.option("--stop-docker", is_flag=True, help="Also stop the Docker container")
def stop(stop_docker: bool):
    """Stop the vector database service."""
    console.print(Panel("[bold cyan]Stopping Vector Database[/bold cyan]", expand=False))
    
    try:
        service = VectorDBService(auto_start=False)
        service.shutdown(stop_container=stop_docker)
        
        if stop_docker:
            console.print("[bold green]✓ Vector database and container stopped[/bold green]")
        else:
            console.print("[bold green]✓ Vector database service stopped[/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@vector.command()
@click.argument("collection_name")
@click.option("--vector-size", "-s", type=int, required=True, help="Vector dimensions")
@click.option("--distance", "-d", type=click.Choice(["cosine", "euclidean", "dot"]), default="cosine")
def create_collection(collection_name: str, vector_size: int, distance: str):
    """Create a new collection."""
    console.print(f"Creating collection '{collection_name}'...")
    
    try:
        service = VectorDBService()
        
        success = service.collections.create_collection(
            name=collection_name,
            vector_size=vector_size,
            distance=distance.capitalize()
        )
        
        if success:
            console.print(f"[bold green]✓ Collection '{collection_name}' created successfully[/bold green]")
        else:
            console.print(f"[bold red]✗ Failed to create collection[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@vector.command()
def list_collections():
    """List all collections."""
    try:
        service = VectorDBService()
        collections = service.collections.list_collections()
        
        if not collections:
            console.print("[yellow]No collections found[/yellow]")
            return
            
        table = Table(title="Vector Collections", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan")
        table.add_column("Vectors", justify="right")
        table.add_column("Vector Size", justify="right")
        table.add_column("Distance", style="green")
        table.add_column("Status", justify="center")
        
        for col in collections:
            status_icon = "✓" if col.is_ready else "⚠"
            table.add_row(
                col.name,
                str(col.vectors_count),
                str(col.vector_size),
                col.distance_metric,
                status_icon
            )
            
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@vector.command()
@click.argument("query")
@click.option("--collection", "-c", help="Collection to search (default: from config)")
@click.option("--limit", "-n", type=int, default=10, help="Number of results")
@click.option("--threshold", "-t", type=float, help="Minimum similarity score")
def search(query: str, collection: Optional[str], limit: int, threshold: Optional[float]):
    """Search for similar documents."""
    console.print(f"\n[bold]Searching for:[/bold] {query}\n")
    
    try:
        service = VectorDBService()
        
        # Perform search
        results = service.search_similar(
            query_text=query,
            collection_name=collection,
            limit=limit,
            score_threshold=threshold
        )
        
        if not results:
            console.print("[yellow]No results found[/yellow]")
            return
            
        # Display results
        console.print(f"[bold green]Found {len(results)} results:[/bold green]\n")
        
        for i, result in enumerate(results, 1):
            # Create result panel
            content = f"[bold]Score:[/bold] {result.score:.4f}\n"
            content += f"[bold]File:[/bold] {result.payload.get('file_name', 'Unknown')}\n"
            content += f"[bold]Chunk:[/bold] {result.payload.get('chunk_index', '?')}\n"
            
            # Add preview if available
            preview = result.payload.get('chunk_text', '')
            if preview:
                content += f"\n[dim]{preview[:150]}{'...' if len(preview) > 150 else ''}[/dim]"
                
            console.print(Panel(
                content,
                title=f"[cyan]Result {i}[/cyan]",
                border_style="blue"
            ))
            
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@vector.command()
@click.argument("file_paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option("--collection", "-c", help="Target collection (default: from config)")
def store(file_paths: tuple, collection: Optional[str]):
    """Process and store documents in vector database."""
    console.print(Panel("[bold cyan]Store Documents[/bold cyan]", expand=False))
    
    if not file_paths:
        console.print("[red]Please specify at least one file to process[/red]")
        return
        
    try:
        service = VectorDBService()
        
        # Convert to Path objects
        paths = [Path(p) for p in file_paths]
        
        console.print(f"\nProcessing {len(paths)} files...\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Processing and storing documents...", total=None)
            
            result = service.process_and_store(
                file_paths=paths,
                collection_name=collection,
                show_progress=False  # We're handling progress here
            )
            
        # Show results
        console.print("\n[bold green]Storage Complete![/bold green]\n")
        console.print(f"Documents processed: {result['documents_processed']}")
        console.print(f"Vectors stored: {result['vectors_stored']}")
        
        if result['errors']:
            console.print(f"\n[bold red]Errors:[/bold red]")
            for error in result['errors']:
                console.print(f"  • {error}")
                
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


# Add vector commands to main CLI


@vector.command(name='info')
@click.argument('collection_name')
def info(collection_name: str):
    """Show detailed information about a specific collection."""
    try:
        service = VectorDBService()
        
        # Check if collection exists
        collections = service.collections.list_collections()
        collection = next((c for c in collections if c.name == collection_name), None)
        
        if not collection:
            console.print(f"[red]Collection '{collection_name}' not found[/red]")
            return
        
        # Display collection info
        console.print(Panel(f"[bold cyan]Collection: {collection_name}[/bold cyan]", expand=False))
        
        # Basic info table
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value", style="yellow")
        
        info_table.add_row("Vector Count", str(collection.vectors_count))
        info_table.add_row("Vector Size", str(collection.vector_size))
        info_table.add_row("Distance Metric", collection.distance_metric)
        info_table.add_row("Status", "✓ Ready" if collection.is_ready else "⚠ Not Ready")
        
        console.print("\n[bold]Collection Details:[/bold]")
        console.print(info_table)
        
        # Get some sample vectors to show stats
        if collection.vectors_count > 0:
            console.print("\n[bold]Storage Statistics:[/bold]")
            console.print(f"  • Total vectors: {collection.vectors_count}")
            console.print(f"  • Dimensions: {collection.vector_size}")
            console.print(f"  • Distance metric: {collection.distance_metric}")
            
            # Try to get a sample point for metadata info
            try:
                sample_points, _ = service.client._client.scroll(
                    collection_name=collection_name,
                    limit=1,
                    with_payload=True,
                    with_vectors=False
                )
                
                if sample_points:
                    payload_keys = list(sample_points[0].payload.keys())
                    console.print(f"\n[bold]Metadata Fields:[/bold]")
                    for key in payload_keys:
                        console.print(f"  • {key}")
            except:
                pass
                
        console.print(f"\n[dim]Use 'vector-db-query query --collection {collection_name} \"your search\"' to search this collection[/dim]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


def register_vector_commands(cli):
    """Register vector commands with the main CLI."""
    cli.add_command(vector)