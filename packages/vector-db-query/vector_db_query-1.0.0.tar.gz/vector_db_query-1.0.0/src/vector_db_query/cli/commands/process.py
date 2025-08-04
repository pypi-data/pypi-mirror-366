"""Document processing CLI commands."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table

from vector_db_query.document_processor import DocumentProcessor, ProcessingStats
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
    "--chunk-size", "-c",
    type=int,
    help="Size of text chunks (default: from config)"
)
@click.option(
    "--chunk-overlap", "-o",
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
@click.option(
    "--formats",
    type=str,
    help="Comma-separated list of file formats to process (e.g., pdf,docx,xlsx)"
)
@click.option(
    "--ocr", "-O",
    is_flag=True,
    help="Enable OCR for image files (requires Tesseract)"
)
@click.option(
    "--ocr-lang",
    type=str,
    default="eng",
    help="OCR language code (default: eng)"
)
def process_command(
    folder: Optional[Path],
    file: tuple,
    recursive: bool,
    chunk_size: Optional[int],
    chunk_overlap: Optional[int],
    strategy: Optional[str],
    dry_run: bool,
    verbose: bool,
    formats: Optional[str],
    ocr: bool,
    ocr_lang: str
):
    """Process documents and generate embeddings.
    
    Process documents from a folder or individual files, converting them
    into vector embeddings for storage in the database.
    
    Supported formats:
    - Documents: PDF, DOCX, TXT, RTF, ODT
    - Spreadsheets: XLSX, XLS, CSV
    - Presentations: PPTX, PPT
    - Email: EML, MBOX
    - Web: HTML, HTM, XHTML
    - Config: JSON, XML, YAML, INI, LOG
    - Images (with OCR): PNG, JPG, JPEG, TIFF, BMP
    """
    console.print(Panel("[bold cyan]Document Processing[/bold cyan]", expand=False))
    
    # Validate inputs
    if not folder and not file:
        console.print("[red]Error: Please specify either --folder or --file[/red]")
        raise click.Abort()
        
    # Parse formats if provided
    allowed_formats = None
    if formats:
        allowed_formats = [fmt.strip().lower() for fmt in formats.split(",")]
        console.print(f"[cyan]Processing only formats: {', '.join(allowed_formats)}[/cyan]")
    
    # Create processor
    try:
        processor = DocumentProcessor(
            chunking_strategy=strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            allowed_formats=allowed_formats,
            enable_ocr=ocr,
            ocr_language=ocr_lang
        )
    except Exception as e:
        console.print(f"[red]Error initializing processor: {e}[/red]")
        raise click.Abort()
        
    # Collect files to process
    if dry_run:
        if folder:
            console.print(f"\n[yellow]Would process files from: {folder}[/yellow]")
            console.print(f"Recursive: {recursive}")
            
            # Show scan summary
            summary = processor.scanner.get_scan_summary(folder, recursive)
            _show_scan_summary(summary)
            
        if file:
            console.print(f"\n[yellow]Would process {len(file)} individual files[/yellow]")
            for f in file:
                console.print(f"  • {f}")
                
        return
        
    # Process documents
    console.print("\n[bold]Starting document processing...[/bold]\n")
    
    documents = []
    errors = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        if folder:
            task = progress.add_task(
                f"Processing {folder.name}",
                total=None  # Will be updated
            )
            
            def update_progress(current, total, message):
                progress.update(task, completed=current, total=total, description=message)
                
            for doc in processor.process_directory(folder, recursive, update_progress):
                documents.append(doc)
                if doc.errors:
                    errors.extend(doc.errors)
                    
        if file:
            task = progress.add_task(
                "Processing files",
                total=len(file)
            )
            
            def update_progress(current, total, message):
                progress.update(task, completed=current, total=total, description=message)
                
            file_docs = processor.process_files(list(file), update_progress)
            documents.extend(file_docs)
            for doc in file_docs:
                if doc.errors:
                    errors.extend(doc.errors)
                    
    # Show results
    _show_processing_results(processor.get_stats(), documents, errors, verbose)
    
    
def _show_scan_summary(summary: dict):
    """Show scan summary in a table."""
    table = Table(title="Scan Summary", show_header=True, header_style="bold magenta")
    table.add_column("File Type", style="cyan")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Size (MB)", justify="right", style="green")
    
    for ext, info in summary.get("files_by_type", {}).items():
        table.add_row(
            ext,
            str(info["count"]),
            f"{info['size'] / 1024 / 1024:.2f}"
        )
        
    table.add_row(
        "[bold]Total[/bold]",
        f"[bold]{summary.get('supported_files', 0)}[/bold]",
        f"[bold]{summary.get('total_size_mb', 0):.2f}[/bold]",
        style="bold"
    )
    
    console.print(table)
    

def _show_processing_results(stats: ProcessingStats, documents: list, errors: list, verbose: bool):
    """Show processing results."""
    console.print("\n" + "="*50)
    console.print("[bold green]Processing Complete![/bold green]")
    console.print("="*50 + "\n")
    
    # Summary statistics
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="yellow")
    
    summary_table.add_row("Files Processed", f"{stats.processed_files}/{stats.total_files}")
    summary_table.add_row("Failed Files", str(stats.failed_files))
    summary_table.add_row("Total Chunks", str(stats.total_chunks))
    summary_table.add_row("Total Embeddings", str(stats.total_embeddings))
    summary_table.add_row("Processing Time", f"{stats.processing_time:.2f} seconds")
    
    console.print(Panel(summary_table, title="Summary", border_style="green"))
    
    # Show successful files if verbose
    if verbose and documents:
        console.print("\n[bold]Processed Documents:[/bold]")
        doc_table = Table(show_header=True, header_style="bold magenta")
        doc_table.add_column("File", style="cyan")
        doc_table.add_column("Chunks", justify="right")
        doc_table.add_column("Embeddings", justify="right")
        doc_table.add_column("Time (s)", justify="right")
        doc_table.add_column("Status", justify="center")
        
        for doc in documents:
            status = "✅" if doc.success else "⚠️" if doc.partial_success else "❌"
            doc_table.add_row(
                doc.metadata.filename,
                str(len(doc.chunks)),
                str(len(doc.embeddings)),
                f"{doc.processing_time:.2f}",
                status
            )
            
        console.print(doc_table)
        
    # Show errors if any
    if errors:
        console.print(f"\n[bold red]Errors ({len(errors)}):[/bold red]")
        for i, error in enumerate(errors[:10]):  # Show first 10 errors
            console.print(f"  {i+1}. {error}")
            
        if len(errors) > 10:
            console.print(f"  ... and {len(errors) - 10} more errors")
            
    # Next steps
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("• Review any errors above")
    console.print("• Use 'vector-db-query query' to search your documents")
    console.print("• Check logs for detailed information")


# Interactive processing function for menu
def process_documents_interactive():
    """Interactive document processing interface."""
    from questionary import select, path, confirm
    
    console.print(Panel("[bold]Document Processing[/bold]", border_style="green"))
    
    # Choose processing mode
    mode = select(
        "How would you like to process documents?",
        choices=[
            "Process a folder",
            "Process specific files",
            "Back to main menu"
        ]
    ).ask()
    
    if mode == "Back to main menu":
        return
        
    if mode == "Process a folder":
        # Get folder path
        folder_path = path(
            "Enter folder path:",
            only_directories=True,
            exists=True
        ).ask()
        
        if not folder_path:
            return
            
        recursive = confirm(
            "Process subfolders recursively?",
            default=True
        ).ask()
        
        # Create processor and process
        processor = DocumentProcessor()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Processing documents...", total=None)
            
            def update_progress(current, total, message):
                progress.update(task, completed=current, total=total, description=message)
                
            documents = list(processor.process_directory(
                Path(folder_path),
                recursive,
                update_progress
            ))
            
        # Show results
        _show_processing_results(
            processor.get_stats(),
            documents,
            [e for d in documents for e in d.errors],
            verbose=True
        )
        
    else:  # Process specific files
        console.print("[yellow]File selection interface coming soon![/yellow]")
        
    console.input("\nPress Enter to continue...")