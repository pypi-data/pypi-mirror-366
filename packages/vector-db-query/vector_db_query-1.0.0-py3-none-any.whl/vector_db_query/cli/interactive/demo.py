"""Demo script for enhanced interactive menu system."""

import time
from rich.console import Console

from .menu import InteractiveMenu, MenuBuilder, MenuItem
from .base import ProgressTracker, LoadingSpinner, ErrorDisplay
from .styles import VECTOR_DB_HEADER, WELCOME_MESSAGE


def demo_progress():
    """Demo progress tracking."""
    console = Console()
    
    console.print("\n[bold]Progress Tracking Demo[/bold]\n")
    
    # Determinate progress
    with ProgressTracker("Processing files", total=100) as tracker:
        for i in range(100):
            tracker.update(1, f"Processing file {i+1}/100")
            time.sleep(0.02)
    
    console.print("[green]✓ Processing complete![/green]\n")
    
    # Indeterminate progress
    with LoadingSpinner("Connecting to database..."):
        time.sleep(2)
    
    console.print("[green]✓ Connected![/green]\n")


def demo_error_handling():
    """Demo error display."""
    console = Console()
    
    console.print("\n[bold]Error Handling Demo[/bold]\n")
    
    try:
        raise ValueError("This is a demo error")
    except ValueError as e:
        error_display = ErrorDisplay(
            e,
            title="Demo Error",
            suggestions=[
                "Check your input values",
                "Verify configuration settings",
                "Contact support if issue persists"
            ]
        )
        
        action = error_display.render()
        console.print(f"\nUser selected: {action}")


def demo_animations():
    """Demo menu animations."""
    console = Console()
    
    console.print("\n[bold]Menu Animations Demo[/bold]\n")
    
    # Create a simple menu with animations
    menu = InteractiveMenu(
        "Animation Demo Menu",
        items=[
            MenuItem("fade", "Fade In Effect", handler=lambda: "fade_demo"),
            MenuItem("slide", "Slide Effect", handler=lambda: "slide_demo"),
            MenuItem("pulse", "Pulse Effect", handler=lambda: "pulse_demo"),
            MenuItem("typewriter", "Typewriter Effect", handler=lambda: "typewriter_demo"),
        ],
        enable_animations=True,
        show_help=False
    )
    
    selection = menu.show()
    if selection:
        console.print(f"\nSelected: {selection}")


def demo_full_menu():
    """Demo full interactive menu system."""
    console = Console()
    
    # Show header
    console.print(VECTOR_DB_HEADER, style="bold cyan")
    console.print(WELCOME_MESSAGE)
    console.print()
    
    # Create menu builder
    builder = MenuBuilder(theme="default")
    
    # Create main menu
    main = builder.create_main_menu()
    
    # Add custom handlers
    def handle_process():
        console.print("\n[cyan]Processing documents...[/cyan]")
        with ProgressTracker("Indexing files", total=50) as tracker:
            for i in range(50):
                tracker.update(1)
                time.sleep(0.05)
        console.print("[green]✓ Processing complete![/green]")
        console.input("\nPress Enter to continue...")
        return "__back__"
    
    def handle_query():
        console.print("\n[cyan]Querying database...[/cyan]")
        with LoadingSpinner("Searching..."):
            time.sleep(1.5)
        console.print("[green]✓ Found 42 results![/green]")
        console.input("\nPress Enter to continue...")
        return "__back__"
    
    def handle_status():
        console.print("\n[bold]System Status[/bold]")
        console.print("├─ Vector DB: [green]Connected[/green]")
        console.print("├─ MCP Server: [yellow]Stopped[/yellow]")
        console.print("├─ Documents: 1,234 indexed")
        console.print("└─ Storage: 256 MB used")
        console.input("\nPress Enter to continue...")
        return "__back__"
    
    # Attach handlers
    process_item = main.get_item("process")
    if process_item:
        process_item.handler = handle_process
    
    query_item = main.get_item("query")
    if query_item:
        query_item.handler = handle_query
        
    status_item = main.get_item("status")
    if status_item:
        status_item.handler = handle_status
    
    # Run menu
    main.run_interactive()
    
    console.print("\n[dim]Thank you for using Vector DB Query System![/dim]")


def main():
    """Run all demos."""
    console = Console()
    
    demos = [
        ("Progress Tracking", demo_progress),
        ("Error Handling", demo_error_handling),
        ("Menu Animations", demo_animations),
        ("Full Interactive Menu", demo_full_menu),
    ]
    
    console.print("\n[bold cyan]Interactive CLI Demo Suite[/bold cyan]\n")
    console.print("Select a demo to run:\n")
    
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"{i}. {name}")
    
    console.print("\nPress Ctrl+C to exit")
    
    while True:
        try:
            choice = console.input("\nSelect demo (1-4): ")
            if choice.isdigit() and 1 <= int(choice) <= len(demos):
                _, demo_func = demos[int(choice) - 1]
                demo_func()
            else:
                console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()