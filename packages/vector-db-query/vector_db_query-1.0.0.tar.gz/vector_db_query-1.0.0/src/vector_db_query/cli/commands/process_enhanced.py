"""Enhanced document processing CLI commands with format support."""

from pathlib import Path
from typing import Optional, List
import os

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from vector_db_query.document_processor import DocumentProcessor, ProcessingStats
from vector_db_query.document_processor.reader import ReaderFactory
from vector_db_query.document_processor.image_ocr_reader import check_ocr_available
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
    "--formats",
    is_flag=True,
    help="Show supported file formats and exit"
)
@click.option(
    "--extensions", "-e",
    multiple=True,
    help="Only process files with these extensions (e.g., -e .pdf -e .docx)"
)
@click.option(
    "--exclude", "-x",
    multiple=True,
    help="Exclude files with these extensions"
)
@click.option(
    "--ocr-lang", 
    default="eng",
    help="OCR language(s) for images (default: eng)"
)
@click.option(
    "--ocr-confidence",
    type=float,
    default=60.0,
    help="Minimum OCR confidence threshold (0-100)"
)
@click.option(
    "--no-ocr",
    is_flag=True,
    help="Disable OCR for image files"
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
    "--stats",
    is_flag=True,
    help="Show detailed statistics after processing"
)
def process_command(
    folder: Optional[Path],
    file: tuple,
    recursive: bool,
    chunk_size: Optional[int],
    chunk_overlap: Optional[int],
    strategy: Optional[str],
    formats: bool,
    extensions: tuple,
    exclude: tuple,
    ocr_lang: str,
    ocr_confidence: float,
    no_ocr: bool,
    dry_run: bool,
    verbose: bool,
    stats: bool
):
    """Process documents and generate embeddings.
    
    Process documents from a folder or individual files, converting them
    into vector embeddings for storage in the database.
    
    Supports multiple file formats including:
    - Documents: PDF, DOCX, TXT, MD
    - Spreadsheets: XLSX, XLS, CSV
    - Presentations: PPTX, PPT
    - Email: EML, MBOX
    - Web: HTML, HTM, XHTML
    - Config: JSON, XML, YAML, INI, CFG
    - Images: PNG, JPG, GIF, BMP, TIFF (with OCR)
    - Logs: LOG files with analysis
    """
    console.print(Panel("[bold cyan]Document Processing[/bold cyan]", expand=False))
    
    # Show formats if requested
    if formats:
        show_supported_formats()
        return
        
    # Validate inputs
    if not folder and not file:
        console.print("[red]Error: Please specify either --folder or --file[/red]")
        raise click.Abort()
        
    # Create processor with OCR configuration
    try:
        processor_kwargs = {
            "chunking_strategy": strategy,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        
        # Handle OCR configuration
        if not no_ocr and check_ocr_available():
            console.print(f"[green]OCR enabled[/green] (language: {ocr_lang}, confidence: {ocr_confidence}%)")
            processor_kwargs["enable_ocr"] = True
            processor_kwargs["ocr_language"] = ocr_lang
        elif no_ocr:
            console.print("[yellow]OCR disabled by user[/yellow]")
            processor_kwargs["enable_ocr"] = False
        else:
            console.print("[yellow]OCR not available - install pytesseract and Tesseract[/yellow]")
            processor_kwargs["enable_ocr"] = False
            
        # Add allowed formats from extensions
        if extensions:
            processor_kwargs["allowed_formats"] = list(extensions)
            
        processor = DocumentProcessor(**processor_kwargs)
        
    except Exception as e:
        console.print(f"[red]Error initializing processor: {e}[/red]")
        raise click.Abort()
        
    # Filter extensions if specified
    allowed_extensions = set(extensions) if extensions else None
    excluded_extensions = set(exclude) if exclude else None
    
    # Collect files to process
    if dry_run:
        if folder:
            console.print(f"\n[yellow]Would process files from: {folder}[/yellow]")
            console.print(f"Recursive: {recursive}")
            if allowed_extensions:
                console.print(f"Only extensions: {', '.join(allowed_extensions)}")
            if excluded_extensions:
                console.print(f"Excluding: {', '.join(excluded_extensions)}")
                
            # Show enhanced scan summary
            summary = processor.scanner.get_scan_summary(folder, recursive)
            _show_enhanced_scan_summary(summary, allowed_extensions, excluded_extensions)
            
        if file:
            console.print(f"\n[yellow]Would process {len(file)} individual files[/yellow]")
            for f in file:
                if _should_process_file(f, allowed_extensions, excluded_extensions):
                    console.print(f"  ✓ {f}")
                else:
                    console.print(f"  ✗ {f} [dim](filtered)[/dim]")
                    
        return
        
    # Process documents
    console.print("\n[bold]Starting document processing...[/bold]\n")
    
    documents = []
    errors = []
    format_stats = {}
    
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
                
            # Filter files during processing
            for doc in processor.process_directory(folder, recursive, update_progress):
                if _should_process_file(doc.metadata.file_path, allowed_extensions, excluded_extensions):
                    documents.append(doc)
                    if doc.errors:
                        errors.extend(doc.errors)
                    # Track format statistics
                    ext = Path(doc.metadata.file_path).suffix.lower()
                    format_stats[ext] = format_stats.get(ext, 0) + 1
                    
        if file:
            task = progress.add_task(
                "Processing files",
                total=len(file)
            )
            
            # Filter files before processing
            filtered_files = [f for f in file if _should_process_file(f, allowed_extensions, excluded_extensions)]
            
            def update_progress(current, total, message):
                progress.update(task, completed=current, total=total, description=message)
                
            file_docs = processor.process_files(filtered_files, update_progress)
            documents.extend(file_docs)
            for doc in file_docs:
                if doc.errors:
                    errors.extend(doc.errors)
                # Track format statistics
                ext = Path(doc.metadata.file_path).suffix.lower()
                format_stats[ext] = format_stats.get(ext, 0) + 1
                    
    # Show results
    _show_enhanced_processing_results(
        processor.get_stats(), 
        documents, 
        errors, 
        format_stats,
        verbose,
        stats
    )


def show_supported_formats():
    """Display all supported file formats."""
    console.print("\n[bold]Supported File Formats[/bold]\n")
    
    # Create reader factory to get actual supported formats
    factory = ReaderFactory()
    
    # Group formats by category
    categories = {
        "Documents": ['.pdf', '.doc', '.docx', '.txt', '.md', '.markdown'],
        "Spreadsheets": ['.xlsx', '.xls', '.csv'],
        "Presentations": ['.pptx', '.ppt'],
        "Email": ['.eml', '.mbox'],
        "Web": ['.html', '.htm', '.xhtml'],
        "Configuration": ['.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.config'],
        "Images (OCR)": ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.tif', '.webp'],
        "Logs": ['.log']
    }
    
    # Create tree view
    tree = Tree("[bold cyan]File Format Support[/bold cyan]")
    
    for category, extensions in categories.items():
        # Check which extensions are actually supported
        supported = [ext for ext in extensions if ext in factory.supported_extensions]
        
        if supported:
            branch = tree.add(f"[bold yellow]{category}[/bold yellow]")
            for ext in supported:
                if ext in factory.supported_extensions:
                    branch.add(f"[green]✓[/green] {ext}")
                    
    console.print(tree)
    
    # Show OCR status
    console.print("\n[bold]OCR Support:[/bold]")
    if check_ocr_available():
        console.print("  [green]✓[/green] OCR is available (Tesseract installed)")
        try:
            from vector_db_query.document_processor.image_ocr_reader import get_available_languages
            languages = get_available_languages()
            if languages:
                console.print(f"  [dim]Available languages: {', '.join(languages[:10])}{'...' if len(languages) > 10 else ''}[/dim]")
        except:
            pass
    else:
        console.print("  [yellow]✗[/yellow] OCR not available - install pytesseract and Tesseract for image text extraction")
        
    # Show total count
    console.print(f"\n[bold]Total supported extensions:[/bold] {len(factory.supported_extensions)}")


def _should_process_file(file_path: Path, allowed_extensions: Optional[set], excluded_extensions: Optional[set]) -> bool:
    """Check if a file should be processed based on extension filters."""
    ext = file_path.suffix.lower()
    
    if excluded_extensions and ext in excluded_extensions:
        return False
        
    if allowed_extensions and ext not in allowed_extensions:
        return False
        
    return True


def _show_enhanced_scan_summary(summary: dict, allowed_extensions: Optional[set], excluded_extensions: Optional[set]):
    """Show enhanced scan summary with format breakdown."""
    table = Table(title="Scan Summary", show_header=True, header_style="bold magenta")
    table.add_column("File Type", style="cyan")
    table.add_column("Count", justify="right", style="yellow")
    table.add_column("Size (MB)", justify="right", style="green")
    table.add_column("Status", justify="center")
    
    total_included = 0
    total_size_included = 0
    
    for ext, info in summary.get("files_by_type", {}).items():
        if _should_process_file(Path(f"dummy{ext}"), allowed_extensions, excluded_extensions):
            status = "[green]✓[/green]"
            total_included += info["count"]
            total_size_included += info["size"]
        else:
            status = "[red]✗[/red]"
            
        table.add_row(
            ext,
            str(info["count"]),
            f"{info['size'] / 1024 / 1024:.2f}",
            status
        )
        
    table.add_row(
        "[bold]Total Included[/bold]",
        f"[bold]{total_included}[/bold]",
        f"[bold]{total_size_included / 1024 / 1024:.2f}[/bold]",
        "[bold][green]✓[/green][/bold]",
        style="bold"
    )
    
    console.print(table)
    
    # Show unsupported files if any
    if "unsupported_files" in summary and summary["unsupported_files"]:
        console.print(f"\n[yellow]Unsupported files found: {summary['unsupported_files']}[/yellow]")


def _show_enhanced_processing_results(stats: ProcessingStats, documents: list, errors: list, 
                                     format_stats: dict, verbose: bool, show_stats: bool):
    """Show enhanced processing results with format breakdown."""
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
    
    if stats.processed_files > 0:
        summary_table.add_row("Avg Time/File", f"{stats.processing_time / stats.processed_files:.2f} seconds")
        summary_table.add_row("Avg Chunks/File", f"{stats.total_chunks / stats.processed_files:.1f}")
    
    console.print(Panel(summary_table, title="Summary", border_style="green"))
    
    # Format breakdown if show_stats
    if show_stats and format_stats:
        console.print("\n[bold]Format Breakdown:[/bold]")
        format_table = Table(show_header=True, header_style="bold magenta")
        format_table.add_column("Format", style="cyan")
        format_table.add_column("Files", justify="right")
        format_table.add_column("Percentage", justify="right")
        
        total_processed = sum(format_stats.values())
        for ext, count in sorted(format_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_processed) * 100
            format_table.add_row(ext, str(count), f"{percentage:.1f}%")
            
        console.print(format_table)
    
    # Show successful files if verbose
    if verbose and documents:
        console.print("\n[bold]Processed Documents:[/bold]")
        doc_table = Table(show_header=True, header_style="bold magenta")
        doc_table.add_column("File", style="cyan")
        doc_table.add_column("Format", justify="center")
        doc_table.add_column("Chunks", justify="right")
        doc_table.add_column("Embeddings", justify="right")
        doc_table.add_column("Time (s)", justify="right")
        doc_table.add_column("Status", justify="center")
        
        for doc in documents:
            status = "✅" if doc.success else "⚠️" if doc.partial_success else "❌"
            ext = Path(doc.metadata.filename).suffix.lower()
            doc_table.add_row(
                doc.metadata.filename,
                ext,
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
    console.print("• Use 'vector-db-query process --formats' to see all supported formats")
    console.print("• Check logs for detailed information")


# New format detection command
@click.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--detailed", "-d", is_flag=True, help="Show detailed format information")
def detect_format(path: Path, detailed: bool):
    """Detect and show information about file format support.
    
    Shows whether a file or files in a directory are supported and
    which reader would be used to process them.
    """
    console.print(Panel("[bold cyan]Format Detection[/bold cyan]", expand=False))
    
    factory = ReaderFactory()
    
    if path.is_file():
        # Single file detection
        _show_file_format_info(path, factory, detailed)
    else:
        # Directory scan
        files = list(path.rglob("*"))
        files = [f for f in files if f.is_file()]
        
        console.print(f"\nScanning {len(files)} files in {path}...\n")
        
        supported = []
        unsupported = []
        
        for file in files:
            try:
                reader = factory.get_reader(file)
                supported.append((file, reader))
            except:
                unsupported.append(file)
                
        # Show summary
        console.print(f"[green]Supported files:[/green] {len(supported)}")
        console.print(f"[red]Unsupported files:[/red] {len(unsupported)}")
        
        if detailed:
            # Group by reader type
            reader_groups = {}
            for file, reader in supported:
                reader_name = reader.__class__.__name__
                if reader_name not in reader_groups:
                    reader_groups[reader_name] = []
                reader_groups[reader_name].append(file)
                
            console.print("\n[bold]Files by Reader Type:[/bold]")
            for reader_name, files in sorted(reader_groups.items()):
                console.print(f"\n[yellow]{reader_name}[/yellow] ({len(files)} files):")
                for file in files[:5]:  # Show first 5
                    console.print(f"  • {file.relative_to(path)}")
                if len(files) > 5:
                    console.print(f"  ... and {len(files) - 5} more")


def _show_file_format_info(file_path: Path, factory: ReaderFactory, detailed: bool):
    """Show format information for a single file."""
    ext = file_path.suffix.lower()
    
    console.print(f"File: [cyan]{file_path.name}[/cyan]")
    console.print(f"Extension: [yellow]{ext}[/yellow]")
    console.print(f"Size: {file_path.stat().st_size / 1024:.1f} KB")
    
    try:
        reader = factory.get_reader(file_path)
        console.print(f"Status: [green]✓ Supported[/green]")
        console.print(f"Reader: [yellow]{reader.__class__.__name__}[/yellow]")
        
        if detailed:
            console.print(f"\n[bold]Reader Details:[/bold]")
            console.print(f"  Module: {reader.__class__.__module__}")
            console.print(f"  Supported extensions: {', '.join(reader.supported_extensions)}")
            
            # Show reader-specific info
            if hasattr(reader, 'language'):  # OCR reader
                console.print(f"  OCR Language: {reader.language}")
            if hasattr(reader, 'preserve_structure'):
                console.print(f"  Preserve Structure: {reader.preserve_structure}")
                
    except Exception as e:
        console.print(f"Status: [red]✗ Not Supported[/red]")
        console.print(f"Reason: {str(e)}")
        
        # Suggest similar supported formats
        if ext:
            similar = [e for e in factory.supported_extensions if ext[1:] in e or e[1:] in ext]
            if similar:
                console.print(f"\n[yellow]Similar supported formats:[/yellow] {', '.join(similar)}")


# Interactive processing function for menu with enhanced features
def process_documents_interactive():
    """Interactive document processing interface with format selection."""
    from questionary import select, path, confirm, checkbox
    
    console.print(Panel("[bold]Document Processing[/bold]", border_style="green"))
    
    # Show format support status
    factory = ReaderFactory()
    console.print(f"\n[cyan]Supporting {len(factory.supported_extensions)} file formats[/cyan]")
    if check_ocr_available():
        console.print("[green]✓[/green] OCR enabled for image files")
    else:
        console.print("[yellow]✗[/yellow] OCR not available")
    
    # Choose processing mode
    mode = select(
        "How would you like to process documents?",
        choices=[
            "Process a folder",
            "Process specific files",
            "Show supported formats",
            "Back to main menu"
        ]
    ).ask()
    
    if mode == "Back to main menu":
        return
        
    if mode == "Show supported formats":
        show_supported_formats()
        console.input("\nPress Enter to continue...")
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
        
        # Format filtering
        filter_formats = confirm(
            "Filter by specific formats?",
            default=False
        ).ask()
        
        allowed_extensions = None
        if filter_formats:
            # Show format categories
            categories = {
                "Documents (PDF, DOCX, TXT)": ['.pdf', '.docx', '.txt', '.md'],
                "Spreadsheets (XLSX, CSV)": ['.xlsx', '.xls', '.csv'],
                "Web/Config (HTML, JSON, XML)": ['.html', '.json', '.xml', '.yaml'],
                "Images (with OCR)": ['.png', '.jpg', '.jpeg', '.gif', '.bmp'],
                "All Supported Formats": []
            }
            
            selected_category = select(
                "Select format category:",
                choices=list(categories.keys())
            ).ask()
            
            if selected_category != "All Supported Formats":
                allowed_extensions = categories[selected_category]
        
        # Create processor and process
        processor = DocumentProcessor()
        
        documents = []
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
                
            for doc in processor.process_directory(
                Path(folder_path),
                recursive,
                update_progress
            ):
                if allowed_extensions is None or Path(doc.metadata.file_path).suffix.lower() in allowed_extensions:
                    documents.append(doc)
            
        # Show results
        _show_enhanced_processing_results(
            processor.get_stats(),
            documents,
            [e for d in documents for e in d.errors],
            {},  # Format stats would be calculated here
            verbose=True,
            show_stats=True
        )
        
    else:  # Process specific files
        console.print("[yellow]File selection interface coming soon![/yellow]")
        
    console.input("\nPress Enter to continue...")