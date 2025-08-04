"""Main CLI interface for Vector DB Query System."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from vector_db_query import VERSION
from vector_db_query.utils.config import get_config
from vector_db_query.utils.logger import get_logger, setup_logging

console = Console()
logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option("--log-level", "-l", type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]), help="Log level")
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], log_level: Optional[str], version: bool) -> None:
    """Vector DB Query System - Query your documents using LLMs via MCP."""
    # Show version and exit
    if version:
        click.echo(f"Vector DB Query System v{VERSION}")
        ctx.exit(0)
        
    # Setup logging with custom level if provided
    if log_level:
        setup_logging(log_level=log_level)
        
    # Store config path in context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    
    # If no command provided, show interactive menu
    if ctx.invoked_subcommand is None:
        # Check if enhanced interactive mode is available
        try:
            from vector_db_query.cli.interactive.app import InteractiveApp
            console.print("[cyan]Starting enhanced interactive mode...[/cyan]")
            import asyncio
            app = InteractiveApp(Path(config) if config else None)
            asyncio.run(app.run())
        except ImportError:
            # Fallback to basic menu
            show_interactive_menu()


def show_interactive_menu() -> None:
    """Show interactive main menu."""
    while True:
        console.clear()
        
        # Show header
        console.print(Panel.fit(
            f"[bold cyan]Vector DB Query System v{VERSION}[/bold cyan]\n"
            "[dim]Query your documents using LLMs via MCP[/dim]",
            border_style="blue"
        ))
        
        # Show menu options
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="bold yellow", width=3)
        table.add_column("Description")
        
        options = [
            ("1", "Process Documents - Convert documents to vector embeddings"),
            ("2", "Query Database - Search and query your documents"),
            ("3", "MCP Server - Manage MCP server for LLM integration"),
            ("4", "Configuration - Manage system settings"),
            ("5", "System Status - Check system health and statistics"),
            ("6", "Help - Show documentation and examples"),
            ("7", "Exit - Close the application"),
        ]
        
        for opt, desc in options:
            table.add_row(opt, desc)
            
        console.print("\n[bold]Main Menu:[/bold]")
        console.print(table)
        
        # Get user choice
        try:
            choice = console.input("\n[bold cyan]Select option (1-7):[/bold cyan] ")
            
            if choice == "1":
                process_documents_interactive()
            elif choice == "2":
                query_database_interactive()
            elif choice == "3":
                show_mcp_menu()
            elif choice == "4":
                show_configuration_menu()
            elif choice == "5":
                show_system_status()
            elif choice == "6":
                show_help()
            elif choice == "7":
                console.print("\n[bold green]Goodbye![/bold green]")
                sys.exit(0)
            else:
                console.print("[red]Invalid option. Please try again.[/red]")
                console.input("\nPress Enter to continue...")
                
        except KeyboardInterrupt:
            console.print("\n\n[bold yellow]Interrupted by user[/bold yellow]")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Error in interactive menu: {e}")
            console.print(f"\n[red]Error: {e}[/red]")
            console.input("\nPress Enter to continue...")


# Remove the placeholder - we'll use the one from process.py


def query_database_interactive() -> None:
    """Interactive database query menu."""
    console.clear()
    console.print(Panel("[bold]Query Database[/bold]", border_style="green"))
    
    # Placeholder for actual implementation
    console.print("\n[yellow]Query functionality coming soon![/yellow]")
    console.print("\nThis will allow you to:")
    console.print("• Search documents using natural language")
    console.print("• Configure query parameters")
    console.print("• Use different prompt templates")
    console.print("• Get structured responses via MCP")
    console.print("• Export results in various formats")
    
    console.input("\nPress Enter to return to main menu...")


def show_mcp_menu() -> None:
    """Show MCP server menu."""
    console.clear()
    console.print(Panel("[bold]MCP Server Management[/bold]", border_style="green"))
    
    console.print("\n[bold]Available Commands:[/bold]\n")
    
    table = Table(show_header=False, box=None)
    table.add_column("Command", style="cyan", width=30)
    table.add_column("Description")
    
    commands = [
        ("vector-db-query mcp init", "Initialize MCP configuration"),
        ("vector-db-query mcp start", "Start the MCP server"),
        ("vector-db-query mcp status", "Check server status"),
        ("vector-db-query mcp auth create-client", "Create new client"),
        ("vector-db-query mcp auth list-clients", "List all clients"),
        ("vector-db-query mcp test", "Test server with sample query"),
    ]
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
    
    console.print(table)
    
    console.print("\n[bold]Quick Start:[/bold]")
    console.print("1. Run 'vector-db-query mcp init' to create configuration")
    console.print("2. Save the client credentials securely")
    console.print("3. Start the server with 'vector-db-query mcp start'")
    console.print("4. Connect from Claude or other LLMs using MCP protocol")
    
    console.input("\nPress Enter to return to main menu...")


def show_configuration_menu() -> None:
    """Show configuration menu."""
    console.clear()
    console.print(Panel("[bold]Configuration[/bold]", border_style="green"))
    
    config = get_config()
    
    # Show current configuration
    console.print("\n[bold]Current Configuration:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="yellow")
    
    # Add key settings
    table.add_row("Embedding Model", config.get("embedding.model"))
    table.add_row("Embedding Dimensions", str(config.get("embedding.dimensions")))
    table.add_row("Qdrant Host", f"{config.get('vector_db.host')}:{config.get('vector_db.port')}")
    table.add_row("Collection Name", config.get("vector_db.collection_name"))
    table.add_row("Chunk Size", str(config.get("document_processing.chunk_size")))
    table.add_row("Log Level", config.get("app.log_level"))
    
    console.print(table)
    
    console.print("\n[yellow]Configuration editing coming soon![/yellow]")
    console.input("\nPress Enter to return to main menu...")


def show_system_status() -> None:
    """Show system status and health checks."""
    console.clear()
    console.print(Panel("[bold]System Status[/bold]", border_style="green"))
    
    # Placeholder for actual implementation
    console.print("\n[yellow]System status checks coming soon![/yellow]")
    console.print("\nThis will show:")
    console.print("• Qdrant database status")
    console.print("• MCP server status")
    console.print("• Google API connectivity")
    console.print("• Storage statistics")
    console.print("• Processing metrics")
    
    console.input("\nPress Enter to return to main menu...")


def show_help() -> None:
    """Show help and documentation."""
    console.clear()
    console.print(Panel("[bold]Help & Documentation[/bold]", border_style="green"))
    
    console.print("\n[bold]Quick Start:[/bold]")
    console.print("1. Ensure Docker is running")
    console.print("2. Start Qdrant: ./scripts/start-qdrant.sh")
    console.print("3. Add your API keys to .env file")
    console.print("4. Process documents using option 1")
    console.print("5. Query your data using option 2")
    
    console.print("\n[bold]Commands:[/bold]")
    console.print("• vector-db-query process - Process documents")
    console.print("• vector-db-query query - Query database")
    console.print("• vector-db-query vector - Manage vector database")
    console.print("• vector-db-query mcp - Manage MCP server")
    console.print("• vector-db-query config - Show configuration")
    console.print("• vector-db-query formats - Check supported file formats")
    console.print("• vector-db-query status - Check system status")
    
    console.print("\n[bold]Environment Variables:[/bold]")
    console.print("• GOOGLE_API_KEY - Required for embeddings")
    console.print("• MCP_AUTH_TOKEN - Required for MCP server")
    console.print("• LOG_LEVEL - Set logging verbosity")
    
    console.input("\nPress Enter to return to main menu...")


# Import and add commands - handle optional dependencies gracefully
try:
    from vector_db_query.cli.commands.process_enhanced import process_command, process_documents_interactive, detect_format
    cli.add_command(process_command, name="process")
    cli.add_command(detect_format, name="detect-format")
except ImportError:
    # Fallback to basic process command if enhanced not available
    try:
        from vector_db_query.cli.commands.process_fixed import process_command, process_documents_interactive
        cli.add_command(process_command, name="process")
    except ImportError:
        pass

try:
    from vector_db_query.cli.commands.vector import vector
    cli.add_command(vector)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.mcp import mcp_group
    cli.add_command(mcp_group)
except ImportError:
    pass
try:
    from vector_db_query.cli.commands.mcp_enhanced import mcp_enhanced_group
    cli.add_command(mcp_enhanced_group, name="mcp-enhanced")
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.interactive import interactive_group
    cli.add_command(interactive_group)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.read import read_command
    cli.add_command(read_command, name="read")
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.monitor import monitor, monitoring
    cli.add_command(monitor)
    cli.add_command(monitoring)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.logging import logging
    cli.add_command(logging)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.formats import formats_command
    cli.add_command(formats_command, name="formats")
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.auth import auth
    cli.add_command(auth)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.api import api
    cli.add_command(api)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.fireflies import fireflies
    cli.add_command(fireflies)
except ImportError:
    pass

try:
    from vector_db_query.cli.commands.googledrive import googledrive
    cli.add_command(googledrive)
except ImportError:
    pass

# Deduplication command
try:
    from vector_db_query.cli.commands.dedup import dedup
    cli.add_command(dedup)
except ImportError:
    pass

# Data sources command
try:
    from vector_db_query.cli.commands.datasources import datasources
    cli.add_command(datasources)
except ImportError:
    pass

# Setup commands
try:
    from vector_db_query.cli.commands.setup import setup, reset
    cli.add_command(setup)
    cli.add_command(reset)
except ImportError:
    pass

# Quick start command
try:
    from vector_db_query.cli.commands.quickstart import quickstart
    cli.add_command(quickstart)
except ImportError:
    pass

# Performance commands
try:
    from vector_db_query.cli.commands.performance import performance, perf
    cli.add_command(performance)
    cli.add_command(perf)
except ImportError:
    pass

# Migration commands
try:
    from vector_db_query.cli.commands.migrate import migrate
    cli.add_command(migrate)
except ImportError:
    pass


@cli.command()
@click.argument("query_text", required=False)
@click.option("--limit", "-n", type=int, default=10, help="Number of results")
def query(query_text: Optional[str], limit: int) -> None:
    """Query the vector database."""
    console.print("[yellow]Query command coming soon![/yellow]")


# Config command is now a group with subcommands
try:
    from vector_db_query.cli.commands.config import config_group
    cli.add_command(config_group, name="config")
except ImportError:
    # Fallback to simple config command
    @cli.command()
    def config() -> None:
        """Show current configuration."""
        show_configuration_menu()
    

@cli.command()
def status() -> None:
    """Check system status."""
    show_system_status()


if __name__ == "__main__":
    cli()