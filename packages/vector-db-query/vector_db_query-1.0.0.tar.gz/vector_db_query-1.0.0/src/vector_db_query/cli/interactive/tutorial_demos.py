"""Demo implementations for tutorial steps."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import questionary

from .menu import MenuBuilder
from .file_browser import FileBrowser
from .query_builder import QueryBuilder
from .progress import ProgressManager, create_file_progress
from .config_ui import ConfigSection, ConfigField, ConfigType


def demo_main_menu():
    """Demo main menu navigation."""
    console = Console()
    
    console.print("[bold]Main Menu Demo[/bold]\n")
    console.print("This is a simplified version of the main menu.")
    console.print("Try navigating with arrow keys!\n")
    
    builder = MenuBuilder()
    menu = builder.create_menu("demo", "Demo Menu")
    
    builder.add_item("demo", "process", "Process Documents", 
                     description="Convert files to vectors")
    builder.add_item("demo", "query", "Query Database",
                     description="Search your documents")
    builder.add_item("demo", "settings", "Settings",
                     description="Configure application")
    
    selection = menu.show()
    
    if selection:
        console.print(f"\n[green]You selected: {selection}[/green]")
    else:
        console.print("\n[yellow]No selection made[/yellow]")


def demo_file_processing():
    """Demo file processing workflow."""
    console = Console()
    
    console.print("[bold]File Processing Demo[/bold]\n")
    
    # Create demo files
    demo_dir = Path("/tmp/demo_docs")
    demo_dir.mkdir(exist_ok=True)
    
    files = [
        ("readme.txt", "This is a sample readme file."),
        ("guide.md", "# User Guide\n\nThis is a markdown guide."),
        ("data.json", '{"name": "sample", "type": "demo"}'),
    ]
    
    for name, content in files:
        (demo_dir / name).write_text(content)
    
    console.print(f"Created demo files in {demo_dir}\n")
    
    # File browser
    browser = FileBrowser(start_path=demo_dir, allow_multiple=True)
    selected = browser.browse()
    
    if selected:
        console.print(f"\n[green]Selected {len(selected)} files[/green]")
        
        # Simulate processing
        console.print("\n[cyan]Processing files...[/cyan]")
        
        with create_file_progress(selected) as progress:
            import time
            time.sleep(2)  # Simulate processing
        
        console.print("\n[green]✓ Processing complete![/green]")
    else:
        console.print("\n[yellow]No files selected[/yellow]")


def demo_query_interface():
    """Demo query interface."""
    console = Console()
    
    console.print("[bold]Query Interface Demo[/bold]\n")
    
    builder = QueryBuilder()
    query = builder.build_query()
    
    if query:
        console.print(f"\n[green]Your query: {query}[/green]")
        
        # Simulate results
        console.print("\n[cyan]Searching...[/cyan]")
        
        results = [
            {
                "title": "Configuration Guide",
                "score": 0.92,
                "content": "To configure the database connection..."
            },
            {
                "title": "API Reference",
                "score": 0.87,
                "content": "The database configuration options include..."
            },
            {
                "title": "Troubleshooting",
                "score": 0.81,
                "content": "If database connection fails, check..."
            }
        ]
        
        # Display results
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan")
        table.add_column("Score", style="green")
        table.add_column("Preview", style="dim")
        
        for result in results:
            table.add_row(
                result["title"],
                f"{result['score']:.2f}",
                result["content"][:50] + "..."
            )
        
        console.print("\n[bold]Search Results:[/bold]")
        console.print(table)
    else:
        console.print("\n[yellow]No query entered[/yellow]")


def demo_chunking_config():
    """Demo chunking configuration."""
    console = Console()
    
    console.print("[bold]Chunking Configuration Demo[/bold]\n")
    
    # Show current config
    config = {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "chunking_strategy": "semantic"
    }
    
    console.print("[cyan]Current Configuration:[/cyan]")
    for key, value in config.items():
        console.print(f"  {key}: {value}")
    
    # Edit config
    if questionary.confirm("\nEdit configuration?").ask():
        config["chunk_size"] = questionary.text(
            "Chunk size (tokens):",
            default=str(config["chunk_size"])
        ).ask()
        
        config["chunk_overlap"] = questionary.text(
            "Chunk overlap (tokens):",
            default=str(config["chunk_overlap"])
        ).ask()
        
        config["chunking_strategy"] = questionary.select(
            "Chunking strategy:",
            choices=["semantic", "fixed-size", "sentence-based"],
            default=config["chunking_strategy"]
        ).ask()
        
        console.print("\n[green]Configuration updated![/green]")
        for key, value in config.items():
            console.print(f"  {key}: {value}")


def demo_batch_processing():
    """Demo batch file processing."""
    console = Console()
    
    console.print("[bold]Batch Processing Demo[/bold]\n")
    
    # Create demo directory structure
    base_dir = Path("/tmp/demo_batch")
    base_dir.mkdir(exist_ok=True)
    
    # Create subdirectories with files
    categories = ["docs", "code", "data"]
    file_count = 0
    
    for cat in categories:
        cat_dir = base_dir / cat
        cat_dir.mkdir(exist_ok=True)
        
        for i in range(3):
            file_path = cat_dir / f"{cat}_{i+1}.txt"
            file_path.write_text(f"Sample {cat} file {i+1}")
            file_count += 1
    
    console.print(f"Created {file_count} files in {base_dir}\n")
    
    # Browse directory
    browser = FileBrowser(
        start_path=base_dir,
        allow_multiple=True,
        show_tree=True
    )
    
    selected = browser.browse()
    
    if selected:
        console.print(f"\n[green]Selected {len(selected)} files for batch processing[/green]")
        
        # Show progress
        manager = ProgressManager()
        manager.start()
        
        try:
            task = manager.create_task("batch_process", "Processing files", len(selected))
            
            import time
            for i, file in enumerate(selected):
                manager.update_task(task, advance=1, description=f"Processing {file.name}")
                time.sleep(0.5)  # Simulate processing
            
            manager.complete_task(task)
            console.print("\n[green]✓ Batch processing complete![/green]")
            
        finally:
            manager.stop()
    else:
        console.print("\n[yellow]No files selected[/yellow]")


def demo_mcp_config():
    """Demo MCP configuration."""
    console = Console()
    
    console.print("[bold]MCP Configuration Demo[/bold]\n")
    
    # Show configuration sections
    sections = [
        ConfigSection(
            name="server",
            title="Server Settings",
            description="MCP server configuration",
            fields=[
                ConfigField(
                    key="port",
                    name="Server Port",
                    description="Port for MCP server",
                    type=ConfigType.INTEGER,
                    default=8080
                ),
                ConfigField(
                    key="auth_required",
                    name="Require Authentication",
                    description="Enable token authentication",
                    type=ConfigType.BOOLEAN,
                    default=True
                ),
            ]
        ),
        ConfigSection(
            name="security",
            title="Security Settings",
            description="Security configuration",
            fields=[
                ConfigField(
                    key="cors_enabled",
                    name="Enable CORS",
                    description="Allow cross-origin requests",
                    type=ConfigType.BOOLEAN,
                    default=False
                ),
                ConfigField(
                    key="rate_limit",
                    name="Rate Limit",
                    description="Requests per minute",
                    type=ConfigType.INTEGER,
                    default=60
                ),
            ]
        )
    ]
    
    # Display configuration
    for section in sections:
        panel = Panel(
            f"{section.description}\n\n" +
            "\n".join([f"• {field.name}: {field.default}" for field in section.fields]),
            title=f"[bold]{section.title}[/bold]",
            border_style="blue"
        )
        console.print(panel)
        console.print()


def demo_mcp_server():
    """Demo MCP server start."""
    console = Console()
    
    console.print("[bold]MCP Server Demo[/bold]\n")
    
    console.print("[cyan]Starting MCP server...[/cyan]\n")
    
    # Simulate server startup
    steps = [
        "Loading configuration...",
        "Initializing authentication...",
        "Starting HTTP server on port 8080...",
        "Server ready to accept connections!"
    ]
    
    import time
    for step in steps:
        console.print(f"  {step}")
        time.sleep(0.5)
    
    console.print("\n[green]✓ MCP server started successfully![/green]")
    console.print("\nServer endpoint: http://localhost:8080")
    console.print("Use Ctrl+C to stop the server")


def demo_client_creation():
    """Demo MCP client creation."""
    console = Console()
    
    console.print("[bold]Create MCP Client Demo[/bold]\n")
    
    client_name = questionary.text(
        "Client name:",
        default="claude-desktop"
    ).ask()
    
    if client_name:
        console.print(f"\n[cyan]Creating client '{client_name}'...[/cyan]")
        
        # Simulate client creation
        import secrets
        client_id = f"client_{secrets.token_hex(8)}"
        auth_token = secrets.token_urlsafe(32)
        
        console.print("\n[green]✓ Client created successfully![/green]\n")
        
        # Show credentials
        creds_panel = Panel(
            f"Client ID: {client_id}\n"
            f"Auth Token: {auth_token}\n\n"
            "[yellow]⚠️  Save these credentials securely![/yellow]",
            title="[bold]Client Credentials[/bold]",
            border_style="green"
        )
        
        console.print(creds_panel)
        
        # Show configuration
        console.print("\n[bold]Add to Claude Desktop configuration:[/bold]")
        console.print("""
{
  "vector-db-query": {
    "endpoint": "http://localhost:8080",
    "client_id": "%s",
    "auth_token": "%s"
  }
}
""" % (client_id, auth_token))


def demo_mcp_test():
    """Demo MCP connection test."""
    console = Console()
    
    console.print("[bold]MCP Connection Test Demo[/bold]\n")
    
    console.print("[cyan]Testing MCP connection...[/cyan]\n")
    
    # Simulate test steps
    tests = [
        ("Server reachability", True, "Server is running on port 8080"),
        ("Authentication", True, "Token validation successful"),
        ("Query endpoint", True, "Query endpoint responding"),
        ("Response format", True, "Valid JSON response"),
    ]
    
    import time
    for test_name, success, message in tests:
        console.print(f"  Testing {test_name}...", end="")
        time.sleep(0.5)
        
        if success:
            console.print(f" [green]✓[/green] {message}")
        else:
            console.print(f" [red]✗[/red] {message}")
    
    console.print("\n[green]All tests passed! MCP integration is working correctly.[/green]")


def demo_navigation_keys():
    """Demo keyboard navigation."""
    console = Console()
    
    console.print("[bold]Keyboard Navigation Demo[/bold]\n")
    
    console.print("Try these keys in the menu:\n")
    
    keys = [
        ("↑↓", "Navigate up/down"),
        ("Enter", "Select item"),
        ("Esc", "Go back"),
        ("1-9", "Quick select"),
        ("/", "Search items"),
    ]
    
    table = Table(show_header=False, box=None)
    table.add_column("Key", style="cyan", width=10)
    table.add_column("Action", style="white")
    
    for key, action in keys:
        table.add_row(key, action)
    
    console.print(table)
    
    # Interactive demo
    if questionary.confirm("\nTry it now?").ask():
        builder = MenuBuilder()
        menu = builder.create_menu("nav_demo", "Navigation Demo")
        
        for i in range(5):
            builder.add_item(
                "nav_demo", f"item_{i}", f"Item {i+1}",
                description=f"This is item number {i+1}"
            )
        
        selection = menu.show()
        
        if selection:
            console.print(f"\n[green]You selected: {selection}[/green]")


# Tutorial step demos mapping
TUTORIAL_DEMOS = {
    "main_menu": demo_main_menu,
    "file_processing": demo_file_processing,
    "query_interface": demo_query_interface,
    "chunking_config": demo_chunking_config,
    "batch_processing": demo_batch_processing,
    "mcp_config": demo_mcp_config,
    "mcp_server": demo_mcp_server,
    "client_creation": demo_client_creation,
    "mcp_test": demo_mcp_test,
    "navigation_keys": demo_navigation_keys,
}


def get_demo(name: str):
    """Get demo function by name.
    
    Args:
        name: Demo name
        
    Returns:
        Demo function or None
    """
    return TUTORIAL_DEMOS.get(name)