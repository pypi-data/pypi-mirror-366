"""Enhanced MCP server CLI commands."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ...mcp_integration.server_enhanced import create_enhanced_server
from ...utils.config import get_config
from ...utils.config_enhanced import FileFormatConfig


console = Console()
logger = logging.getLogger(__name__)


@click.group(name="mcp-enhanced")
def mcp_enhanced_group():
    """Enhanced MCP server commands with format awareness."""
    pass


@mcp_enhanced_group.command()
@click.option(
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
    default="INFO",
    help="Logging level"
)
@click.option(
    "--show-formats",
    is_flag=True,
    help="Show supported formats and exit"
)
def start(config: Optional[Path], log_level: str, show_formats: bool):
    """Start the enhanced MCP server with format support."""
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr  # Log to stderr to keep stdout for MCP
    )
    
    if show_formats:
        _show_supported_formats()
        return
    
    try:
        # Show startup banner
        _show_startup_banner()
        
        # Create server
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Initializing enhanced MCP server...", total=None)
            
            server = create_enhanced_server(config)
            
            progress.update(task, description="Server initialized successfully")
        
        # Show server info
        _show_server_info(server)
        
        console.print("\n[green]✓[/green] Enhanced MCP server ready")
        console.print("[dim]Server is running on stdio. Press Ctrl+C to stop.[/dim]\n")
        
        # Run server
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Server interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error starting server: {str(e)}[/red]")
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)


@mcp_enhanced_group.command()
def formats():
    """Show detailed format support information."""
    _show_supported_formats(detailed=True)


@mcp_enhanced_group.command()
@click.argument("file_path", type=click.Path(exists=True))
def check(file_path: str):
    """Check if a file format is supported."""
    path = Path(file_path)
    extension = path.suffix.lower()
    
    format_config = FileFormatConfig()
    is_supported = format_config.is_supported(extension)
    
    if is_supported:
        # Get reader info
        from ...document_processor.reader import ReaderFactory
        factory = ReaderFactory()
        
        try:
            reader = factory.get_reader(str(path))
            reader_name = reader.__class__.__name__
            category = _get_format_category(extension, format_config)
            
            console.print(Panel(
                f"[green]✓ Supported[/green]\n\n"
                f"File: {path.name}\n"
                f"Extension: {extension}\n"
                f"Category: {category}\n"
                f"Reader: {reader_name}",
                title="Format Check",
                border_style="green"
            ))
            
            # Check for special capabilities
            capabilities = []
            if hasattr(reader, 'extract_tables'):
                capabilities.append("Table extraction")
            if hasattr(reader, 'extract_images'):
                capabilities.append("Image extraction")
            if hasattr(reader, 'ocr_enabled'):
                capabilities.append("OCR support")
            if hasattr(reader, 'stream_content'):
                capabilities.append("Streaming")
            
            if capabilities:
                console.print(f"\n[bold]Capabilities:[/bold] {', '.join(capabilities)}")
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not instantiate reader: {e}[/yellow]")
    else:
        # Find similar formats
        similar = _find_similar_formats(extension, format_config)
        
        console.print(Panel(
            f"[red]✗ Not Supported[/red]\n\n"
            f"File: {path.name}\n"
            f"Extension: {extension}\n"
            f"Reason: No reader available for this format",
            title="Format Check",
            border_style="red"
        ))
        
        if similar:
            console.print(f"\n[yellow]Similar supported formats:[/yellow] {', '.join(similar)}")


@mcp_enhanced_group.command()
def capabilities():
    """Show MCP server capabilities and features."""
    # Create table
    table = Table(title="Enhanced MCP Server Capabilities", show_header=True)
    table.add_column("Feature", style="cyan", width=30)
    table.add_column("Status", style="green", width=15)
    table.add_column("Details", width=50)
    
    # Check various capabilities
    capabilities_list = [
        ("Format Support", "✓ Active", "39+ file formats across 10 categories"),
        ("OCR Processing", _check_ocr_status(), "Extract text from images (PNG, JPG, etc.)"),
        ("Archive Extraction", "✓ Active", "Process ZIP, TAR, and compressed archives"),
        ("Config Parsing", "✓ Active", "Parse JSON, YAML, XML, INI files"),
        ("Email Processing", "✓ Active", "Extract from EML and MBOX files"),
        ("Spreadsheet Support", "✓ Active", "Excel, CSV with table preservation"),
        ("Parallel Processing", "✓ Active", "Multi-threaded document processing"),
        ("Format Filtering", "✓ Active", "Search by specific file types"),
        ("Metadata Extraction", "✓ Active", "Extract document properties"),
        ("Streaming Support", "✓ Active", "Handle large files efficiently")
    ]
    
    for feature, status, details in capabilities_list:
        table.add_row(feature, status, details)
    
    console.print(table)
    
    # Show tools
    console.print("\n[bold]Available MCP Tools:[/bold]")
    tools = [
        ("query_vectors", "Search with format filtering"),
        ("search_similar", "Find similar documents"),
        ("get_context", "Get expanded context"),
        ("process_document", "Process files with format detection"),
        ("detect_format", "Check format support"),
        ("list_formats", "List all supported formats")
    ]
    
    for tool, desc in tools:
        console.print(f"  • [cyan]{tool}[/cyan]: {desc}")
    
    # Show resources
    console.print("\n[bold]Available MCP Resources:[/bold]")
    resources = [
        ("collections", "List vector collections"),
        ("server/status", "Server status with format stats"),
        ("formats/stats", "Format processing statistics"),
        ("readers/capabilities", "Detailed reader capabilities")
    ]
    
    for resource, desc in resources:
        console.print(f"  • [cyan]{resource}[/cyan]: {desc}")


def _show_startup_banner():
    """Show startup banner."""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     Enhanced Vector Query MCP Server v2.0.0               ║
║     Now with 39+ File Format Support!                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    console.print(banner, style="bright_blue")


def _show_server_info(server):
    """Show server information."""
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="dim")
    table.add_column("Value")
    
    table.add_row("Server Name:", server.server.name)
    table.add_row("Version:", server.server.version)
    table.add_row("Formats Supported:", str(len(server.format_config.all_supported)))
    table.add_row("OCR Available:", "Yes" if server._check_ocr_available() else "No")
    table.add_row("Max Connections:", str(server.config.max_connections))
    table.add_row("Auth Required:", "Yes" if server.config.auth_required else "No")
    
    console.print(table)


def _show_supported_formats(detailed: bool = False):
    """Show supported formats."""
    format_config = FileFormatConfig()
    
    console.print(Panel(
        "[bold]Supported File Formats[/bold]\n"
        f"Total: {len(format_config.all_supported)} formats",
        border_style="blue"
    ))
    
    # Categories with emojis
    categories = [
        ("📄 Documents", format_config.documents),
        ("📊 Spreadsheets", format_config.spreadsheets),
        ("🎯 Presentations", format_config.presentations),
        ("📧 Email", format_config.email),
        ("🌐 Web/Markup", format_config.web),
        ("⚙️ Config", format_config.config),
        ("🖼️ Images", format_config.images),
        ("📦 Archives", format_config.archives),
        ("📊 Data", format_config.data),
        ("📋 Logs", format_config.logs),
    ]
    
    if format_config.custom_extensions:
        categories.append(("🔧 Custom", format_config.custom_extensions))
    
    for category_name, extensions in categories:
        if extensions:
            console.print(f"\n[bold]{category_name}:[/bold]")
            
            if detailed:
                # Show with reader info
                from ...document_processor.reader import ReaderFactory
                factory = ReaderFactory()
                
                for ext in sorted(extensions):
                    try:
                        reader = factory.get_reader(f"test{ext}")
                        reader_name = reader.__class__.__name__
                        console.print(f"  {ext:<8} → {reader_name}")
                    except:
                        console.print(f"  {ext:<8} → [dim]Unknown[/dim]")
            else:
                # Simple list
                console.print(f"  {', '.join(sorted(extensions))}")


def _get_format_category(extension: str, format_config: FileFormatConfig) -> str:
    """Get category for an extension."""
    ext = extension.lower()
    if not ext.startswith('.'):
        ext = f'.{ext}'
    
    if ext in format_config.documents:
        return "Documents"
    elif ext in format_config.spreadsheets:
        return "Spreadsheets"
    elif ext in format_config.presentations:
        return "Presentations"
    elif ext in format_config.email:
        return "Email"
    elif ext in format_config.web:
        return "Web/Markup"
    elif ext in format_config.config:
        return "Config"
    elif ext in format_config.images:
        return "Images"
    elif ext in format_config.archives:
        return "Archives"
    elif ext in format_config.data:
        return "Data"
    elif ext in format_config.logs:
        return "Logs"
    elif ext in format_config.custom_extensions:
        return "Custom"
    else:
        return "Unknown"


def _find_similar_formats(extension: str, format_config: FileFormatConfig) -> list:
    """Find similar supported formats."""
    similar = []
    ext_lower = extension.lower().strip('.')
    
    for supported in format_config.all_supported:
        supported_lower = supported.strip('.').lower()
        if (ext_lower in supported_lower or 
            supported_lower in ext_lower or
            ext_lower[:3] == supported_lower[:3]):
            similar.append(supported)
    
    return similar[:5]


def _check_ocr_status() -> str:
    """Check OCR availability status."""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return "✓ Active"
    except:
        return "✗ Not Available"


if __name__ == "__main__":
    mcp_enhanced_group()