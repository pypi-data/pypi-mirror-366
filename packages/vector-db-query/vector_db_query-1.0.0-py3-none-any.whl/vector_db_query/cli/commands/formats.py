"""File format detection and information commands."""

from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from vector_db_query.document_processor.reader import ReaderFactory
from vector_db_query.utils.logger import get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.option(
    "--path", "-p",
    type=click.Path(exists=True, path_type=Path),
    help="File or folder to analyze"
)
@click.option(
    "--supported", "-s",
    is_flag=True,
    help="Show all supported formats"
)
@click.option(
    "--ocr-status", "-o",
    is_flag=True,
    help="Check OCR availability"
)
def formats_command(path: Optional[Path], supported: bool, ocr_status: bool):
    """Detect and display file format information.
    
    This command helps you understand which file formats are supported
    and analyze files to determine their format.
    """
    console.print(Panel("[bold cyan]File Format Information[/bold cyan]", expand=False))
    
    if supported or (not path and not ocr_status):
        _show_supported_formats()
        
    if ocr_status:
        _check_ocr_status()
        
    if path:
        _analyze_path(path)


def _show_supported_formats():
    """Display all supported file formats."""
    console.print("\n[bold]Supported File Formats:[/bold]\n")
    
    # Get format categories from ReaderFactory
    formats = {
        "Documents": {
            "PDF": ["pdf"],
            "Word": ["docx", "doc"],
            "Text": ["txt", "text", "md", "markdown"],
            "Rich Text": ["rtf"],
            "OpenDocument": ["odt"]
        },
        "Spreadsheets": {
            "Excel": ["xlsx", "xls"],
            "CSV": ["csv", "tsv"]
        },
        "Presentations": {
            "PowerPoint": ["pptx", "ppt"]
        },
        "Email": {
            "Email Message": ["eml"],
            "Mailbox": ["mbox"]
        },
        "Web": {
            "HTML": ["html", "htm", "xhtml"]
        },
        "Configuration": {
            "JSON": ["json"],
            "XML": ["xml"],
            "YAML": ["yaml", "yml"],
            "INI": ["ini", "cfg", "conf"],
            "Log": ["log"]
        },
        "Images (OCR)": {
            "Common Images": ["png", "jpg", "jpeg"],
            "Documents": ["tiff", "tif"],
            "Other": ["bmp", "gif"]
        }
    }
    
    # Create tree view
    tree = Tree("[bold]File Formats[/bold]")
    
    for category, types in formats.items():
        category_branch = tree.add(f"[cyan]{category}[/cyan]")
        for format_name, extensions in types.items():
            ext_list = ", ".join(f".{ext}" for ext in extensions)
            category_branch.add(f"[yellow]{format_name}[/yellow]: {ext_list}")
    
    console.print(tree)
    
    # Show total count
    total_extensions = sum(len(exts) for types in formats.values() for exts in types.values())
    console.print(f"\n[green]Total supported extensions: {total_extensions}[/green]")


def _check_ocr_status():
    """Check OCR availability and configuration."""
    console.print("\n[bold]OCR Status:[/bold]\n")
    
    try:
        import pytesseract
        from PIL import Image
        
        # Check Tesseract installation
        try:
            version = pytesseract.get_tesseract_version()
            console.print(f"✅ Tesseract OCR installed: [green]v{version}[/green]")
            
            # Check available languages
            langs = pytesseract.get_languages()
            console.print(f"✅ Available languages: [cyan]{', '.join(langs)}[/cyan]")
            
        except Exception as e:
            console.print("❌ Tesseract not found: [red]Please install Tesseract OCR[/red]")
            console.print("   Install with: brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)")
            
    except ImportError:
        console.print("❌ Python dependencies missing: [red]pytesseract and/or Pillow not installed[/red]")
        console.print("   Install with: pip install pytesseract pillow pdf2image")


def _analyze_path(path: Path):
    """Analyze a file or directory for format information."""
    if path.is_file():
        _analyze_file(path)
    else:
        _analyze_directory(path)


def _analyze_file(file_path: Path):
    """Analyze a single file."""
    console.print(f"\n[bold]Analyzing file:[/bold] {file_path}\n")
    
    # Basic file info
    info_table = Table(show_header=False, box=None)
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="yellow")
    
    info_table.add_row("Name", file_path.name)
    info_table.add_row("Extension", file_path.suffix.lower())
    info_table.add_row("Size", f"{file_path.stat().st_size / 1024:.2f} KB")
    
    # Check if supported
    extension = file_path.suffix.lower().lstrip('.')
    reader = ReaderFactory.get_reader(extension)
    
    if reader:
        info_table.add_row("Supported", "✅ Yes")
        info_table.add_row("Reader", reader.__class__.__name__)
        
        # Check if it's an image that could use OCR
        if extension in ['png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'gif']:
            info_table.add_row("OCR Available", "Yes (if enabled)")
    else:
        info_table.add_row("Supported", "❌ No")
        
    console.print(Panel(info_table, title="File Information", border_style="green"))


def _analyze_directory(dir_path: Path):
    """Analyze all files in a directory."""
    console.print(f"\n[bold]Analyzing directory:[/bold] {dir_path}\n")
    
    # Scan directory
    file_stats = {}
    total_size = 0
    supported_count = 0
    unsupported_files = []
    
    for file_path in dir_path.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if not ext:
                ext = "no extension"
                
            if ext not in file_stats:
                file_stats[ext] = {"count": 0, "size": 0, "supported": False}
                
            file_stats[ext]["count"] += 1
            file_stats[ext]["size"] += file_path.stat().st_size
            total_size += file_path.stat().st_size
            
            # Check if supported
            if ext != "no extension":
                reader = ReaderFactory.get_reader(ext.lstrip('.'))
                if reader:
                    file_stats[ext]["supported"] = True
                    supported_count += 1
                else:
                    unsupported_files.append(file_path.name)
    
    # Display results
    if file_stats:
        table = Table(title="File Format Analysis", show_header=True, header_style="bold magenta")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", justify="right", style="yellow")
        table.add_column("Size (KB)", justify="right", style="green")
        table.add_column("Supported", justify="center")
        
        for ext, stats in sorted(file_stats.items()):
            supported = "✅" if stats["supported"] else "❌"
            table.add_row(
                ext,
                str(stats["count"]),
                f"{stats['size'] / 1024:.2f}",
                supported
            )
            
        console.print(table)
        
        # Summary
        total_files = sum(s["count"] for s in file_stats.values())
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Total files: [yellow]{total_files}[/yellow]")
        console.print(f"  Supported files: [green]{supported_count}[/green]")
        console.print(f"  Unsupported files: [red]{total_files - supported_count}[/red]")
        console.print(f"  Total size: [cyan]{total_size / 1024 / 1024:.2f} MB[/cyan]")
        
        # Show some unsupported files if any
        if unsupported_files:
            console.print(f"\n[yellow]Sample unsupported files:[/yellow]")
            for fname in unsupported_files[:5]:
                console.print(f"  • {fname}")
            if len(unsupported_files) > 5:
                console.print(f"  ... and {len(unsupported_files) - 5} more")
    else:
        console.print("[yellow]No files found in directory[/yellow]")


# Interactive format checking function for menu
def check_formats_interactive():
    """Interactive format checking interface."""
    from questionary import select, path
    
    console.print(Panel("[bold]File Format Information[/bold]", border_style="green"))
    
    # Choose action
    action = select(
        "What would you like to do?",
        choices=[
            "Show all supported formats",
            "Check OCR status",
            "Analyze a file or folder",
            "Back to main menu"
        ]
    ).ask()
    
    if action == "Back to main menu":
        return
        
    if action == "Show all supported formats":
        _show_supported_formats()
        
    elif action == "Check OCR status":
        _check_ocr_status()
        
    elif action == "Analyze a file or folder":
        target_path = path(
            "Enter file or folder path:",
            exists=True
        ).ask()
        
        if target_path:
            _analyze_path(Path(target_path))
    
    console.input("\nPress Enter to continue...")