"""Demo script for the complete interactive application."""

import asyncio
from pathlib import Path
from rich.console import Console

from .app import InteractiveApp
from .styles import VECTOR_DB_HEADER


def demo_interactive_app():
    """Demo the complete interactive application."""
    console = Console()
    
    console.clear()
    console.print(VECTOR_DB_HEADER, style="bold cyan", justify="center")
    console.print("\n[bold]Interactive Application Demo[/bold]\n")
    console.print("This demo shows the complete interactive application experience.")
    console.print("The app integrates all the interactive components into a cohesive workflow.\n")
    
    console.print("[cyan]Features:[/cyan]")
    console.print("• Auto-configuration wizard for first-time setup")
    console.print("• Enhanced menu system with keyboard navigation")
    console.print("• File browser for document selection")
    console.print("• Interactive query builder with suggestions")
    console.print("• Progress tracking for long operations")
    console.print("• Result viewer with multiple formats")
    console.print("• MCP server management")
    console.print("• Visual configuration editor")
    
    console.print("\n[cyan]Workflows:[/cyan]")
    console.print("1. Process Documents - Select files, process with progress tracking")
    console.print("2. Query Database - Build queries, view results interactively")
    console.print("3. Browse Documents - View indexed content")
    console.print("4. Manage Settings - Edit configuration visually")
    
    if console.input("\n[bold]Launch interactive app? (y/n):[/bold] ").lower() == 'y':
        # Create and run app
        config_path = Path.home() / ".vector_db_query" / "config.yaml"
        app = InteractiveApp(config_path)
        
        try:
            asyncio.run(app.run())
        except KeyboardInterrupt:
            console.print("\n[yellow]Demo interrupted[/yellow]")
    else:
        console.print("\n[dim]Demo cancelled[/dim]")


def demo_app_components():
    """Demo individual app components."""
    console = Console()
    
    console.print("\n[bold]Application Components Demo[/bold]\n")
    
    # Component list
    components = [
        ("Configuration Wizard", demo_config_wizard),
        ("Main Menu Navigation", demo_main_menu),
        ("Document Processing Workflow", demo_document_workflow),
        ("Query Workflow", demo_query_workflow),
        ("MCP Management", demo_mcp_management),
        ("System Status", demo_system_status),
    ]
    
    console.print("Available component demos:\n")
    for i, (name, _) in enumerate(components, 1):
        console.print(f"{i}. {name}")
    
    choice = console.input("\nSelect component (1-6): ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(components):
        _, demo_func = components[int(choice) - 1]
        demo_func()
    else:
        console.print("[red]Invalid choice[/red]")


def demo_config_wizard():
    """Demo configuration wizard."""
    console = Console()
    
    console.print("\n[bold]Configuration Wizard Demo[/bold]\n")
    console.print("The configuration wizard guides new users through initial setup.")
    console.print("It validates inputs and creates a working configuration file.\n")
    
    from .config_ui import ConfigWizard, ConfigSection, ConfigField, ConfigType
    
    # Create sample schema
    schema = [
        ConfigSection(
            name="database",
            title="Database Configuration",
            description="Configure your vector database",
            fields=[
                ConfigField(
                    key="host",
                    name="Database Host",
                    description="Hostname where Qdrant is running",
                    type=ConfigType.STRING,
                    default="localhost"
                ),
                ConfigField(
                    key="port",
                    name="Database Port",
                    description="Port number for Qdrant",
                    type=ConfigType.INTEGER,
                    default=6333,
                    validation=lambda x: 1 <= x <= 65535
                ),
            ]
        ),
        ConfigSection(
            name="api",
            title="API Configuration",
            description="Configure API keys",
            fields=[
                ConfigField(
                    key="google_api_key",
                    name="Google API Key",
                    description="Your Google AI API key for embeddings",
                    type=ConfigType.STRING,
                    required=True,
                    sensitive=True
                ),
            ]
        ),
    ]
    
    wizard = ConfigWizard(schema)
    config = wizard.run()
    
    if config:
        console.print("\n[green]Configuration complete![/green]")
        console.print("Config data:", config)


def demo_main_menu():
    """Demo main menu navigation."""
    console = Console()
    
    console.print("\n[bold]Main Menu Navigation Demo[/bold]\n")
    console.print("The main menu provides access to all application features.")
    console.print("It uses keyboard navigation and supports shortcuts.\n")
    
    from .menu import MenuBuilder
    
    builder = MenuBuilder()
    main = builder.create_menu("main", "Main Menu")
    
    # Add menu items
    builder.add_item("main", "process", "Process Documents", 
                     description="Index new documents", 
                     icon="📄")
    builder.add_item("main", "query", "Query Database",
                     description="Search indexed documents",
                     icon="🔍")
    builder.add_item("main", "browse", "Browse Documents",
                     description="View indexed content",
                     icon="📁")
    builder.add_separator("main")
    builder.add_item("main", "settings", "Settings",
                     description="Configure application",
                     icon="⚙️")
    builder.add_item("main", "help", "Help",
                     description="View documentation",
                     icon="❓")
    
    console.print("[dim]Note: This is a simplified demo menu[/dim]\n")
    
    selection = main.show()
    if selection:
        console.print(f"\nSelected: {selection}")


def demo_document_workflow():
    """Demo document processing workflow."""
    console = Console()
    
    console.print("\n[bold]Document Processing Workflow Demo[/bold]\n")
    console.print("This workflow shows how documents are processed interactively:\n")
    
    console.print("1. [cyan]File Selection[/cyan]")
    console.print("   • Browse and select files/folders")
    console.print("   • Preview file contents")
    console.print("   • Filter by file type")
    
    console.print("\n2. [cyan]Processing Options[/cyan]")
    console.print("   • Configure chunk size and overlap")
    console.print("   • Select embedding model")
    console.print("   • Set metadata extraction")
    
    console.print("\n3. [cyan]Progress Tracking[/cyan]")
    console.print("   • Real-time progress bars")
    console.print("   • Processing statistics")
    console.print("   • Error handling")
    
    console.print("\n4. [cyan]Results[/cyan]")
    console.print("   • Processing summary")
    console.print("   • Vector count")
    console.print("   • Error report")
    
    # Demo file browser
    if console.input("\n[bold]Demo file browser? (y/n):[/bold] ").lower() == 'y':
        from .file_browser import FileBrowser
        browser = FileBrowser(preview_enabled=True)
        selected = browser.browse()
        if selected:
            console.print(f"\nSelected {len(selected)} files")


def demo_query_workflow():
    """Demo query workflow."""
    console = Console()
    
    console.print("\n[bold]Query Workflow Demo[/bold]\n")
    console.print("The query workflow helps users search their documents:\n")
    
    console.print("1. [cyan]Query Building[/cyan]")
    console.print("   • Natural language input")
    console.print("   • Query templates")
    console.print("   • Advanced filters")
    console.print("   • Query history")
    
    console.print("\n2. [cyan]Search Execution[/cyan]")
    console.print("   • Vector similarity search")
    console.print("   • Result ranking")
    console.print("   • Metadata filtering")
    
    console.print("\n3. [cyan]Result Display[/cyan]")
    console.print("   • Multiple view formats")
    console.print("   • Pagination")
    console.print("   • Highlighting")
    console.print("   • Export options")
    
    # Demo query builder
    if console.input("\n[bold]Demo query builder? (y/n):[/bold] ").lower() == 'y':
        from .query_builder import QueryBuilder
        builder = QueryBuilder()
        query = builder.build_query()
        if query:
            console.print(f"\nBuilt query: {query}")


def demo_mcp_management():
    """Demo MCP server management."""
    console = Console()
    
    console.print("\n[bold]MCP Server Management Demo[/bold]\n")
    console.print("MCP (Model Context Protocol) enables LLM integration:\n")
    
    console.print("[cyan]Features:[/cyan]")
    console.print("• Server status monitoring")
    console.print("• Start/stop controls")
    console.print("• Client authentication")
    console.print("• Request logging")
    console.print("• Performance metrics")
    
    console.print("\n[cyan]Integration:[/cyan]")
    console.print("• Works with Claude Desktop")
    console.print("• Supports custom LLM clients")
    console.print("• Provides structured responses")
    console.print("• Handles concurrent requests")


def demo_system_status():
    """Demo system status display."""
    console = Console()
    
    console.print("\n[bold]System Status Demo[/bold]\n")
    console.print("System status provides health checks and metrics:\n")
    
    # Mock status data
    from rich.table import Table
    
    table = Table(title="System Status", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details")
    
    table.add_row("Vector Database", "✓ Connected", "1,234 vectors indexed")
    table.add_row("MCP Server", "✓ Running", "Port 8080, 2 clients")
    table.add_row("Document Processor", "✓ Ready", "5 file types supported")
    table.add_row("Embedding API", "✓ Active", "Google Gemini API")
    
    console.print(table)
    
    console.print("\n[cyan]Metrics:[/cyan]")
    console.print("• Documents processed: 156")
    console.print("• Total chunks: 1,234")
    console.print("• Average chunk size: 850 tokens")
    console.print("• Storage used: 45.2 MB")


def demo_keyboard_shortcuts():
    """Demo keyboard shortcuts."""
    console = Console()
    
    console.print("\n[bold]Keyboard Shortcuts Demo[/bold]\n")
    
    shortcuts = """
[cyan]Global Shortcuts:[/cyan]
  Ctrl+C    Exit application
  Ctrl+L    Clear screen
  ?         Show help
  /         Search menu
  
[cyan]Navigation:[/cyan]
  ↑/↓       Move selection
  ←/→       Navigate breadcrumbs
  Enter     Select item
  Esc       Go back
  Tab       Next field
  
[cyan]File Browser:[/cyan]
  Space     Toggle selection
  a         Select all
  d         Done selecting
  p         Toggle preview
  h         Toggle hidden files
  
[cyan]Query Builder:[/cyan]
  Ctrl+H    Show history
  Ctrl+T    Show templates
  Ctrl+S    Save query
  
[cyan]Results:[/cyan]
  v         Change view format
  n/p       Next/previous page
  e         Export results
  f         Filter results
"""
    
    console.print(shortcuts)


def main():
    """Run application demos."""
    console = Console()
    
    while True:
        console.clear()
        console.print(VECTOR_DB_HEADER, style="bold cyan", justify="center")
        console.print("\n[bold]Interactive Application Demo Suite[/bold]\n")
        
        demos = [
            ("Full Interactive Application", demo_interactive_app),
            ("Application Components", demo_app_components),
            ("Keyboard Shortcuts", demo_keyboard_shortcuts),
        ]
        
        for i, (name, _) in enumerate(demos, 1):
            console.print(f"{i}. {name}")
        
        console.print("\nPress Ctrl+C to exit")
        
        try:
            choice = console.input("\nSelect demo (1-3): ")
            if choice.isdigit() and 1 <= int(choice) <= len(demos):
                _, demo_func = demos[int(choice) - 1]
                demo_func()
                console.input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()