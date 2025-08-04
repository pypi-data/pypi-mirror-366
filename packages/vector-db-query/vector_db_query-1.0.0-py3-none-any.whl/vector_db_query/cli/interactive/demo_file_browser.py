"""Demo script for file browser component."""

from pathlib import Path
from rich.console import Console

from .file_browser import FileBrowser, FilePreview, FileSearch
from .styles import get_icon


def demo_file_browser():
    """Demo file browser functionality."""
    console = Console()
    
    console.print("\n[bold]File Browser Demo[/bold]\n")
    console.print("Browse and select files with preview support.\n")
    
    # Create file browser
    browser = FileBrowser(
        start_path=Path.home(),
        filters=[".txt", ".py", ".md", ".json"],
        show_hidden=False,
        allow_multiple=True,
        preview_enabled=True
    )
    
    # Browse files
    selected_files = browser.browse()
    
    if selected_files:
        console.print(f"\n[green]Selected {len(selected_files)} files:[/green]")
        for file in selected_files:
            console.print(f"  {get_icon('file')} {file}")
    else:
        console.print("\n[yellow]No files selected[/yellow]")


def demo_file_preview():
    """Demo file preview functionality."""
    console = Console()
    
    console.print("\n[bold]File Preview Demo[/bold]\n")
    
    # Get a file to preview
    file_path = console.input("Enter file path to preview (or press Enter for demo): ")
    
    if not file_path:
        # Use this script as demo
        file_path = Path(__file__)
    else:
        file_path = Path(file_path)
    
    # Create preview
    preview = FilePreview(
        file_path=file_path,
        max_lines=30,
        syntax_highlight=True
    )
    
    # Show preview
    preview.render()


def demo_file_search():
    """Demo file search functionality."""
    console = Console()
    
    console.print("\n[bold]File Search Demo[/bold]\n")
    
    # Create search component
    search = FileSearch(root_path=Path.cwd())
    
    # Perform search
    results = search.render()
    
    if results:
        console.print(f"\n[green]Selected {len(results)} files from search results[/green]")
    else:
        console.print("\n[yellow]No files selected from search[/yellow]")


def demo_directory_browser():
    """Demo directory browsing with tree view."""
    console = Console()
    
    console.print("\n[bold]Directory Browser Demo[/bold]\n")
    
    # Create browser for directories only
    browser = FileBrowser(
        start_path=Path.cwd(),
        show_hidden=False,
        allow_multiple=False,
        preview_enabled=True
    )
    
    console.print("Navigate directories and press Enter to explore.\n")
    
    # Browse
    selected = browser.browse()
    
    if selected and selected[0].is_dir():
        console.print(f"\n[green]Selected directory:[/green] {selected[0]}")
        
        # Show directory preview
        preview = FilePreview(selected[0])
        preview.render()


def main():
    """Run file browser demos."""
    console = Console()
    
    demos = [
        ("File Browser - Multi-select with preview", demo_file_browser),
        ("File Preview - View file contents", demo_file_preview),
        ("File Search - Find files by pattern", demo_file_search),
        ("Directory Browser - Navigate folders", demo_directory_browser),
    ]
    
    console.print("\n[bold cyan]File Browser Demo Suite[/bold cyan]\n")
    console.print("Explore file browsing capabilities:\n")
    
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"{i}. {name}")
    
    console.print("\nPress Ctrl+C to exit")
    
    while True:
        try:
            choice = console.input("\nSelect demo (1-4): ")
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