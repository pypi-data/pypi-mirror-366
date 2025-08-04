"""Document processing CLI commands with proper vector storage."""

from pathlib import Path
from typing import Optional, List

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from vector_db_query.vector_db.service import VectorDBService
from vector_db_query.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.option(
    "--folder", "-f",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Folder containing documents to process"
)
@click.option(
    "--file", "-i",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    multiple=True,
    help="Individual files to process (can be specified multiple times)"
)
@click.option(
    "--recursive", "-r",
    is_flag=True,
    default=True,
    help="Process folders recursively"
)
@click.option(
    "--collection", "-c",
    type=str,
    default="documents",
    help="Collection name to store documents in"
)
@click.option(
    "--chunk-size",
    type=int,
    help="Size of text chunks (default: from config)"
)
@click.option(
    "--chunk-overlap",
    type=int,
    help="Overlap between chunks (default: from config)"
)
@click.option(
    "--strategy", "-s",
    type=click.Choice(["sliding_window", "semantic"]),
    help="Chunking strategy to use"
)
@click.option(
    "--dry-run", "-d",
    is_flag=True,
    help="Show what would be processed without actually processing"
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Show detailed processing information"
)
def process_command(
    folder: Optional[Path],
    file: tuple,
    recursive: bool,
    collection: str,
    chunk_size: Optional[int],
    chunk_overlap: Optional[int],
    strategy: Optional[str],
    dry_run: bool,
    verbose: bool
):
    """Process documents and store them in the vector database.
    
    Process documents from a folder or individual files, converting them
    into vector embeddings and storing them in Qdrant.
    """
    console.print(Panel("[bold cyan]Document Processing & Storage[/bold cyan]", expand=False))
    
    # Validate inputs
    if not folder and not file:
        console.print("[red]Error: Please specify either --folder or --file[/red]")
        raise click.Abort()
    
    # Initialize vector DB service
    console.print("\n[yellow]Initializing vector database service...[/yellow]")
    try:
        service = VectorDBService(auto_start=True)
        
        # Ensure service is initialized
        if not hasattr(service, '_initialized') or not service._initialized:
            console.print("[yellow]Initializing service...[/yellow]")
            service.initialize(timeout=60)
            
        console.print("[green]✓ Vector database ready[/green]")
        
    except Exception as e:
        console.print(f"[red]Error initializing vector service: {e}[/red]")
        raise click.Abort()
    
    # Collect files to process
    file_paths: List[Path] = []
    
    if folder:
        console.print(f"\n[cyan]Scanning folder: {folder}[/cyan]")
        if recursive:
            # Get all supported files recursively
            from vector_db_query.document_processor.scanner import FileScanner
            scanner = FileScanner()
            
            for file_path in scanner.scan_directory(folder, recursive=recursive):
                file_paths.append(file_path)
        else:
            # Just files in the folder
            for item in folder.iterdir():
                if item.is_file():
                    file_paths.append(item)
    
    # Add individual files
    if file:
        file_paths.extend(file)
    
    # Remove duplicates
    file_paths = list(set(file_paths))
    
    if not file_paths:
        console.print("[yellow]No files found to process[/yellow]")
        return
    
    console.print(f"\n[cyan]Found {len(file_paths)} files to process[/cyan]")
    
    if dry_run:
        console.print("\n[yellow]DRY RUN - Would process:[/yellow]")
        for fp in file_paths[:10]:  # Show first 10
            console.print(f"  • {fp.name}")
        if len(file_paths) > 10:
            console.print(f"  ... and {len(file_paths) - 10} more")
        return
    
    # Process and store documents
    console.print(f"\n[bold]Processing and storing documents in collection '{collection}'...[/bold]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Create a single task for all processing
            task = progress.add_task(
                "Processing documents",
                total=len(file_paths)
            )
            
            # Process in batches for better performance
            batch_size = 10
            processed_count = 0
            total_stored = 0
            errors = []
            
            for i in range(0, len(file_paths), batch_size):
                batch = file_paths[i:i+batch_size]
                
                try:
                    # Process and store this batch
                    result = service.process_and_store(
                        file_paths=batch,
                        collection_name=collection,
                        show_progress=False  # We're handling progress
                    )
                    
                    # Update counts
                    total_stored += result.get('vectors_stored', 0)
                    if 'errors' in result:
                        errors.extend(result['errors'])
                    
                except Exception as e:
                    logger.error(f"Error processing batch: {e}")
                    errors.append(str(e))
                
                # Update progress
                processed_count += len(batch)
                progress.update(task, completed=processed_count)
    
    except Exception as e:
        console.print(f"\n[red]Processing error: {e}[/red]")
        raise click.Abort()
    
    # Show results
    console.print("\n" + "="*50)
    console.print("[bold green]Processing Complete![/bold green]")
    console.print("="*50 + "\n")
    
    # Summary statistics
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary_table.add_row("Files Processed", str(len(file_paths)))
    summary_table.add_row("Documents Stored", str(total_stored))
    summary_table.add_row("Errors", str(len(errors)))
    summary_table.add_row("Collection", collection)
    
    console.print(Panel(summary_table, title="Summary", expand=False))
    
    # Show errors if any
    if errors and verbose:
        console.print("\n[red]Errors encountered:[/red]")
        for error in errors[:5]:  # Show first 5 errors
            console.print(f"  • {error}")
        if len(errors) > 5:
            console.print(f"  ... and {len(errors) - 5} more errors")
    
    # Next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print(f"• Query your documents: [cyan]vdq query 'your search query'[/cyan]")
    console.print(f"• Use interactive mode: [cyan]vdq interactive[/cyan]")
    console.print(f"• Check collection info: [cyan]vector-db-query vector info {collection}[/cyan]")


# For backwards compatibility
process_documents_interactive = process_command