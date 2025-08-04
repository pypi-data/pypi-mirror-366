"""Demo script for keyboard navigation features."""

import time
from typing import List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .keyboard import KeyboardHandler, Key
from .shortcuts import ShortcutContext, shortcut_manager, show_shortcuts
from .hotkeys import HotkeyHandler, get_hotkey_handler


def demo_basic_navigation():
    """Demo basic keyboard navigation."""
    console = Console()
    keyboard = KeyboardHandler(console)
    
    console.clear()
    console.print("[bold]Basic Keyboard Navigation Demo[/bold]\n")
    
    items = [
        "Option 1: Process Documents",
        "Option 2: Query Database",
        "Option 3: Browse Files",
        "Option 4: Settings",
        "Option 5: Help"
    ]
    
    console.print("Navigate with arrow keys, Enter to select, Esc to cancel:\n")
    
    def on_select(item):
        console.print(f"\n[green]Selected: {item}[/green]")
        return item
    
    def on_cancel():
        console.print("\n[yellow]Cancelled[/yellow]")
        return None
    
    handler = keyboard.create_navigation_handler(items, on_select, on_cancel)
    result = handler()
    
    console.input("\nPress Enter to continue...")


def demo_key_reading():
    """Demo direct key reading."""
    console = Console()
    keyboard = KeyboardHandler(console)
    
    console.clear()
    console.print("[bold]Key Reading Demo[/bold]\n")
    console.print("Press keys to see their codes. Press 'q' to quit.\n")
    
    with keyboard.raw_mode():
        while True:
            key = keyboard.read_key()
            
            # Format key for display
            if key == '\x1b':
                display = "ESC"
            elif key == '\r':
                display = "ENTER"
            elif key == ' ':
                display = "SPACE"
            elif key == '\t':
                display = "TAB"
            elif ord(key[0]) < 32:
                display = f"CTRL+{chr(ord(key[0]) + 64)}"
            else:
                display = repr(key)
            
            console.print(f"Key pressed: {display} (raw: {repr(key)})")
            
            if key == 'q':
                break
    
    console.print("\n[dim]Demo complete[/dim]")


def demo_shortcuts():
    """Demo shortcut system."""
    console = Console()
    
    console.clear()
    console.print("[bold]Keyboard Shortcuts Demo[/bold]\n")
    
    # Show shortcuts for different contexts
    contexts = [
        (ShortcutContext.GLOBAL, "Global shortcuts available everywhere"),
        (ShortcutContext.MENU, "Menu navigation shortcuts"),
        (ShortcutContext.FILE_BROWSER, "File browser shortcuts"),
        (ShortcutContext.QUERY_BUILDER, "Query builder shortcuts"),
        (ShortcutContext.RESULTS, "Result viewer shortcuts"),
    ]
    
    for context, description in contexts:
        console.print(f"\n[cyan]{context.value.replace('_', ' ').title()}:[/cyan]")
        console.print(f"[dim]{description}[/dim]\n")
        
        shortcuts = shortcut_manager.get_shortcuts(context)
        if shortcuts:
            # Group by category
            categories = {}
            for shortcut in shortcuts:
                if shortcut.category not in categories:
                    categories[shortcut.category] = []
                categories[shortcut.category].append(shortcut)
            
            for category, items in categories.items():
                console.print(f"  [yellow]{category}:[/yellow]")
                for shortcut in items:
                    console.print(f"    {shortcut.key:<15} {shortcut.description}")
        
        console.input("\nPress Enter for next context...")


def demo_hotkey_handler():
    """Demo global hotkey handler."""
    console = Console()
    handler = HotkeyHandler(console)
    
    console.clear()
    console.print("[bold]Hotkey Handler Demo[/bold]\n")
    console.print("This demo shows global hotkey handling.\n")
    
    # Register some demo hotkeys
    def show_time():
        console.print(f"\n[cyan]Current time: {time.strftime('%H:%M:%S')}[/cyan]")
    
    def show_status():
        console.print("\n[green]✓ System status: All good![/green]")
    
    def toggle_feature():
        console.print("\n[yellow]Feature toggled![/yellow]")
    
    handler.register(Key.T, show_time, ShortcutContext.GLOBAL, "Show current time")
    handler.register(Key.S, show_status, ShortcutContext.GLOBAL, "Show status")
    handler.register(Key.F, toggle_feature, ShortcutContext.GLOBAL, "Toggle feature")
    
    # Show active hotkeys
    handler.show_active_hotkeys()
    
    console.print("\n[dim]Press keys to trigger actions, 'q' to quit[/dim]\n")
    
    # Start handler
    handler.start()
    
    # Manual key processing loop
    keyboard = KeyboardHandler(console)
    with keyboard.raw_mode():
        while True:
            key = keyboard.read_key()
            
            # Convert to Key enum if possible
            key_enum = None
            for k in Key:
                if k.value == key:
                    key_enum = k
                    break
            
            if key_enum:
                if handler.process_key(key_enum):
                    time.sleep(0.1)  # Give handler time to process
            
            if key == 'q':
                break
    
    handler.stop()
    console.print("\n[dim]Demo complete[/dim]")


def demo_context_switching():
    """Demo context-aware shortcuts."""
    console = Console()
    
    console.clear()
    console.print("[bold]Context Switching Demo[/bold]\n")
    console.print("Shortcuts change based on the active context.\n")
    
    # Create a simple context switcher
    contexts = [
        ShortcutContext.MENU,
        ShortcutContext.FILE_BROWSER,
        ShortcutContext.QUERY_BUILDER,
        ShortcutContext.RESULTS,
    ]
    
    current_context = 0
    keyboard = KeyboardHandler(console)
    
    while True:
        console.clear()
        console.print(f"[bold]Current Context: {contexts[current_context].value}[/bold]\n")
        
        # Show shortcuts for current context
        shortcuts = shortcut_manager.get_shortcuts(contexts[current_context])
        
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Action", style="white")
        
        for shortcut in shortcuts[:5]:  # Show first 5
            table.add_row(shortcut.key, shortcut.description)
        
        console.print(table)
        
        console.print("\n[dim]← → to switch contexts, q to quit[/dim]")
        
        with keyboard.raw_mode():
            key = keyboard.read_key()
            
            if key == Key.LEFT.value:
                current_context = (current_context - 1) % len(contexts)
            elif key == Key.RIGHT.value:
                current_context = (current_context + 1) % len(contexts)
            elif key == 'q':
                break


def demo_shortcut_export():
    """Demo shortcut export functionality."""
    console = Console()
    
    console.clear()
    console.print("[bold]Shortcut Export Demo[/bold]\n")
    
    formats = ["markdown", "html", "json"]
    
    for format_type in formats:
        console.print(f"\n[cyan]Export format: {format_type.upper()}[/cyan]")
        console.print("─" * 60)
        
        output = shortcut_manager.export_shortcuts(format_type)
        
        # Show preview
        if format_type == "markdown":
            console.print(output[:500] + "...")
        elif format_type == "html":
            console.print("[dim]HTML output generated (preview):[/dim]")
            console.print(output[:300] + "...")
        elif format_type == "json":
            console.print("[dim]JSON output:[/dim]")
            console.print(output[:400] + "...")
        
        console.input("\nPress Enter to see next format...")
    
    console.print("\n[green]Exports can be saved to files for documentation[/green]")


def demo_custom_bindings():
    """Demo custom key bindings."""
    console = Console()
    keyboard = KeyboardHandler(console)
    
    console.clear()
    console.print("[bold]Custom Key Bindings Demo[/bold]\n")
    
    # Register custom bindings
    custom_actions = []
    
    def action_factory(name):
        def action():
            custom_actions.append(name)
            console.print(f"[green]✓ {name}[/green]")
            return name
        return action
    
    keyboard.register("save", "s", "Save file", 
                     action_factory("Save"), "File Operations")
    keyboard.register("open", "o", "Open file",
                     action_factory("Open"), "File Operations")
    keyboard.register("new", "n", "New file",
                     action_factory("New"), "File Operations")
    keyboard.register("find", "/", "Find in file",
                     action_factory("Find"), "Search")
    keyboard.register("replace", "r", "Replace",
                     action_factory("Replace"), "Search")
    
    # Show custom bindings
    keyboard.show_help()
    
    console.print("\nPress keys to trigger actions, 'q' to quit:")
    
    with keyboard.raw_mode():
        while True:
            key = keyboard.read_key()
            result = keyboard.handle_key(key)
            
            if key == 'q':
                break
    
    console.print(f"\n[dim]Actions performed: {', '.join(custom_actions)}[/dim]")


def main():
    """Run keyboard demos."""
    console = Console()
    
    demos = [
        ("Basic Navigation", demo_basic_navigation),
        ("Direct Key Reading", demo_key_reading),
        ("Shortcut System", demo_shortcuts),
        ("Hotkey Handler", demo_hotkey_handler),
        ("Context Switching", demo_context_switching),
        ("Export Shortcuts", demo_shortcut_export),
        ("Custom Bindings", demo_custom_bindings),
    ]
    
    while True:
        console.clear()
        console.print("[bold cyan]Keyboard Navigation Demo Suite[/bold cyan]\n")
        
        for i, (name, _) in enumerate(demos, 1):
            console.print(f"{i}. {name}")
        
        console.print("\nPress number to run demo, 'q' to quit")
        
        choice = console.input("\nSelect demo: ")
        
        if choice == 'q':
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            _, demo_func = demos[int(choice) - 1]
            demo_func()
        else:
            console.print("[red]Invalid choice![/red]")
            time.sleep(1)
    
    console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()