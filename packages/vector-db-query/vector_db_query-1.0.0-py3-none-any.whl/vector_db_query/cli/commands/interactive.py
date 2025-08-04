"""Interactive CLI commands."""

import asyncio
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from ...cli.interactive.app import create_app
from ...cli.interactive.menu import MenuBuilder
from ...cli.interactive.file_browser import FileBrowser, FilePreview
from ...cli.interactive.query_builder import QueryBuilder, QueryWizard
from ...cli.interactive.config_ui import ConfigEditor
from ...cli.interactive.styles import VECTOR_DB_HEADER


console = Console()


@click.group(name="interactive")
def interactive_group():
    """Interactive CLI commands."""
    pass


@interactive_group.command(name="start")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=False, path_type=Path),
    help="Configuration file path"
)
def start_interactive(config: Optional[Path]):
    """Start interactive mode."""
    console.print(VECTOR_DB_HEADER, style="bold cyan", justify="center")
    console.print("\n[cyan]Starting interactive mode...[/cyan]\n")
    
    try:
        app = create_app(config)
        asyncio.run(app.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interactive mode cancelled[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise click.ClickException(str(e))


@interactive_group.command(name="menu")
@click.option("--demo", is_flag=True, help="Run menu demo")
def interactive_menu(demo: bool):
    """Launch interactive menu system."""
    if demo:
        # Run demo
        from ...cli.interactive.demo import demo_full_menu
        demo_full_menu()
    else:
        # Create simple menu
        builder = MenuBuilder()
        menu = builder.create_main_menu()
        menu.run_interactive()


@interactive_group.command(name="browse")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, path_type=Path),
    help="Starting path"
)
@click.option(
    "--filter",
    "-f",
    multiple=True,
    help="File extension filters (e.g., .txt .pdf)"
)
@click.option("--preview/--no-preview", default=True, help="Enable file preview")
def browse_files(path: Optional[Path], filter: tuple, preview: bool):
    """Browse files interactively."""
    browser = FileBrowser(
        start_path=path,
        filters=list(filter) if filter else None,
        preview_enabled=preview
    )
    
    selected = browser.browse()
    
    if selected:
        console.print(f"\n[green]Selected {len(selected)} files:[/green]")
        for file in selected:
            console.print(f"  • {file}")
    else:
        console.print("\n[yellow]No files selected[/yellow]")


@interactive_group.command(name="preview")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
@click.option("--lines", "-n", type=int, default=50, help="Maximum lines to show")
def preview_file(file: Path, lines: int):
    """Preview file contents."""
    preview = FilePreview(
        file_path=file,
        max_lines=lines,
        syntax_highlight=True
    )
    preview.render()


@interactive_group.command(name="query")
@click.option("--wizard", is_flag=True, help="Use query wizard")
@click.option("--history", is_flag=True, help="Show query history")
def build_query(wizard: bool, history: bool):
    """Build query interactively."""
    if wizard:
        query_wizard = QueryWizard()
        query = query_wizard.guide_query_creation()
    else:
        builder = QueryBuilder()
        if history:
            # Show history first
            builder._show_history()
            console.input("\nPress Enter to continue...")
        query = builder.build_query()
    
    if query:
        console.print(f"\n[green]Query:[/green] {query}")
        
        # Save to clipboard if available
        try:
            import pyperclip
            pyperclip.copy(query)
            console.print("[dim]Query copied to clipboard[/dim]")
        except:
            pass


@interactive_group.command(name="config")
@click.option(
    "--path",
    "-p",
    type=click.Path(path_type=Path),
    help="Configuration file path"
)
@click.option("--wizard", is_flag=True, help="Run configuration wizard")
def edit_config(path: Optional[Path], wizard: bool):
    """Edit configuration interactively."""
    if not path:
        path = Path.home() / ".vector_db_query" / "config.yaml"
    
    if wizard or not path.exists():
        # Run wizard
        from ...cli.interactive.demo_config_ui import create_demo_schema
        from ...cli.interactive.config_ui import ConfigWizard
        
        schema = create_demo_schema()[:3]  # Use first 3 sections
        config_wizard = ConfigWizard(schema)
        config_data = config_wizard.run()
        
        if config_data:
            console.print("\n[green]Configuration complete![/green]")
            console.print(f"Would save to: {path}")
    else:
        # Edit existing
        from ...cli.interactive.demo_config_ui import create_demo_schema
        
        editor = ConfigEditor(
            config_path=path,
            schema=create_demo_schema(),
            format="yaml"
        )
        
        if editor.edit():
            console.print("\n[green]Configuration saved![/green]")


@interactive_group.command(name="demo")
@click.argument(
    "component",
    type=click.Choice([
        "menu", "file-browser", "query-builder", "progress",
        "config", "results", "all"
    ])
)
def run_demo(component: str):
    """Run interactive component demos."""
    console.print(f"\n[bold cyan]Running {component} demo...[/bold cyan]\n")
    
    if component == "menu":
        from ...cli.interactive.demo import main as menu_demo
        menu_demo()
    elif component == "file-browser":
        from ...cli.interactive.demo_file_browser import main as browser_demo
        browser_demo()
    elif component == "query-builder":
        from ...cli.interactive.demo_query_builder import main as query_demo
        query_demo()
    elif component == "progress":
        from ...cli.interactive.demo_progress import main as progress_demo
        progress_demo()
    elif component == "config":
        from ...cli.interactive.demo_config_ui import main as config_demo
        config_demo()
    elif component == "results":
        from ...cli.interactive.demo_results import main as results_demo
        results_demo()
    elif component == "all":
        # Run all demos
        demos = {
            "Menu System": ("...cli.interactive.demo", "main"),
            "File Browser": ("...cli.interactive.demo_file_browser", "main"),
            "Query Builder": ("...cli.interactive.demo_query_builder", "main"),
            "Progress Management": ("...cli.interactive.demo_progress", "main"),
            "Configuration UI": ("...cli.interactive.demo_config_ui", "main"),
            "Result Viewer": ("...cli.interactive.demo_results", "main"),
        }
        
        for name, (module_path, func_name) in demos.items():
            if click.confirm(f"\nRun {name} demo?", default=True):
                # Import and run
                import importlib
                module = importlib.import_module(module_path, package="vector_db_query")
                demo_func = getattr(module, func_name)
                demo_func()


@interactive_group.command(name="shortcuts")
def show_shortcuts():
    """Show keyboard shortcuts."""
    shortcuts_text = """
[bold cyan]Global Keyboard Shortcuts[/bold cyan]

[yellow]Navigation:[/yellow]
  ↑/↓       Navigate up/down
  ←/→       Navigate left/right  
  Enter     Select item
  Esc       Go back
  Tab       Next field
  
[yellow]Menu:[/yellow]
  1-9       Quick select (first 9 items)
  /         Search menu items
  h         Show help
  q         Quit
  
[yellow]File Browser:[/yellow]
  Space     Toggle selection
  d         Done selecting
  h         Toggle hidden files
  p         Toggle preview
  u         Go up directory
  
[yellow]Query Builder:[/yellow]
  Ctrl+H    Show history
  Ctrl+T    Show templates
  Ctrl+L    Clear query
  
[yellow]Results:[/yellow]
  n         Next page
  p         Previous page
  f         First page
  l         Last page
  v         Change view format
  
[yellow]General:[/yellow]
  ?         Show help/shortcuts
  Ctrl+C    Cancel/Exit
"""
    console.print(shortcuts_text)


# Register with main CLI
def register_commands(cli):
    """Register interactive commands with main CLI.
    
    Args:
        cli: Main CLI group
    """
    cli.add_command(interactive_group)