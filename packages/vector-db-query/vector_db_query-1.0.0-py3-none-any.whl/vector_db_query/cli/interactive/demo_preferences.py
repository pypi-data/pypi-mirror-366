"""Demo script for user preferences system."""

from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from .preferences import (
    PreferencesManager, PreferenceType, PreferenceItem,
    get_preferences, get_preference, set_preference
)
from .preferences_ui import (
    PreferencesEditor, PreferencesQuickMenu, apply_preferences
)


def demo_preferences_basics():
    """Demo basic preferences operations."""
    console = Console()
    
    console.clear()
    console.print("[bold]Preferences System Demo[/bold]\n")
    
    # Create preferences manager
    prefs = PreferencesManager(Path("/tmp/demo_preferences.json"))
    
    console.print("1. [cyan]Getting preferences:[/cyan]")
    console.print(f"   Theme: {prefs.get('theme')}")
    console.print(f"   Show icons: {prefs.get('show_icons')}")
    console.print(f"   Page size: {prefs.get('page_size')}")
    
    console.print("\n2. [cyan]Setting preferences:[/cyan]")
    prefs.set("theme", "dracula")
    prefs.set("page_size", 25)
    prefs.set("show_icons", False)
    
    console.print(f"   Theme changed to: {prefs.get('theme')}")
    console.print(f"   Page size changed to: {prefs.get('page_size')}")
    console.print(f"   Show icons changed to: {prefs.get('show_icons')}")
    
    console.print("\n3. [cyan]Saving preferences:[/cyan]")
    if prefs.save():
        console.print("   [green]✓ Preferences saved to disk[/green]")
    
    console.print("\n4. [cyan]Loading preferences:[/cyan]")
    new_prefs = PreferencesManager(Path("/tmp/demo_preferences.json"))
    console.print(f"   Loaded theme: {new_prefs.get('theme')}")
    console.print(f"   Loaded page size: {new_prefs.get('page_size')}")
    
    console.print("\n5. [cyan]Resetting preferences:[/cyan]")
    prefs.reset("theme")
    console.print(f"   Theme reset to: {prefs.get('theme')}")
    
    console.input("\nPress Enter to continue...")


def demo_preference_types():
    """Demo different preference types."""
    console = Console()
    
    console.clear()
    console.print("[bold]Preference Types Demo[/bold]\n")
    
    prefs = PreferencesManager()
    
    # Add custom preferences for demo
    custom_prefs = [
        PreferenceItem(
            key="demo_bool",
            name="Demo Boolean",
            description="A boolean preference",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Demo"
        ),
        PreferenceItem(
            key="demo_int",
            name="Demo Integer",
            description="An integer preference (1-100)",
            type=PreferenceType.INTEGER,
            default=50,
            min_value=1,
            max_value=100,
            category="Demo"
        ),
        PreferenceItem(
            key="demo_choice",
            name="Demo Choice",
            description="A choice preference",
            type=PreferenceType.CHOICE,
            default="option2",
            choices=["option1", "option2", "option3"],
            category="Demo"
        ),
        PreferenceItem(
            key="demo_list",
            name="Demo List",
            description="A list preference",
            type=PreferenceType.LIST,
            default=["item1", "item2"],
            category="Demo"
        ),
        PreferenceItem(
            key="demo_path",
            name="Demo Path",
            description="A path preference",
            type=PreferenceType.PATH,
            default=Path.home(),
            category="Demo"
        ),
    ]
    
    for pref in custom_prefs:
        prefs.add_preference(pref)
    
    # Display all types
    console.print("[cyan]Available preference types:[/cyan]\n")
    
    for pref in custom_prefs:
        console.print(f"[yellow]{pref.name}:[/yellow]")
        console.print(f"  Type: {pref.type.value}")
        console.print(f"  Default: {pref.default}")
        console.print(f"  Current: {pref.get_value()}")
        
        # Validate some values
        if pref.type == PreferenceType.INTEGER:
            console.print(f"  Valid values: {pref.min_value}-{pref.max_value}")
            console.print(f"  Validate 150: {pref.validate(150)}")
            console.print(f"  Validate 50: {pref.validate(50)}")
        elif pref.type == PreferenceType.CHOICE:
            console.print(f"  Choices: {pref.choices}")
            console.print(f"  Validate 'option2': {pref.validate('option2')}")
            console.print(f"  Validate 'invalid': {pref.validate('invalid')}")
        
        console.print()
    
    console.input("Press Enter to continue...")


def demo_preferences_editor():
    """Demo the preferences editor UI."""
    console = Console()
    
    console.clear()
    console.print("[bold]Preferences Editor Demo[/bold]\n")
    console.print("The preferences editor provides a full-featured UI for editing all preferences.")
    console.print("\n[cyan]Features:[/cyan]")
    console.print("• Navigate with arrow keys")
    console.print("• Edit values with Enter")
    console.print("• Reset to defaults with 'r'")
    console.print("• Save changes with 's'")
    console.print("• Context-sensitive input based on type")
    
    if console.input("\n[bold]Launch editor? (y/n):[/bold] ").lower() == 'y':
        editor = PreferencesEditor()
        changes = editor.edit()
        
        if changes:
            console.print("\n[green]Preferences were modified![/green]")
        else:
            console.print("\n[yellow]No changes made[/yellow]")


def demo_quick_menu():
    """Demo the quick preferences menu."""
    console = Console()
    
    console.clear()
    console.print("[bold]Quick Preferences Menu Demo[/bold]\n")
    console.print("The quick menu provides fast access to commonly used preferences.")
    console.print("Boolean preferences can be toggled instantly.\n")
    
    if console.input("[bold]Launch quick menu? (y/n):[/bold] ").lower() == 'y':
        menu = PreferencesQuickMenu()
        changes = menu.show()
        
        if changes:
            console.print("\n[green]Preferences were modified![/green]")


def demo_global_preferences():
    """Demo global preferences access."""
    console = Console()
    
    console.clear()
    console.print("[bold]Global Preferences Access Demo[/bold]\n")
    
    console.print("1. [cyan]Using global getter:[/cyan]")
    console.print(f"   Theme: {get_preference('theme')}")
    console.print(f"   Icons: {get_preference('show_icons')}")
    console.print(f"   Unknown key: {get_preference('unknown', 'default_value')}")
    
    console.print("\n2. [cyan]Using global setter:[/cyan]")
    old_theme = get_preference('theme')
    set_preference('theme', 'github-dark')
    console.print(f"   Theme changed from '{old_theme}' to '{get_preference('theme')}'")
    
    console.print("\n3. [cyan]Getting preferences instance:[/cyan]")
    prefs = get_preferences()
    console.print(f"   Instance type: {type(prefs).__name__}")
    console.print(f"   Total preferences: {len(prefs.preference_items)}")
    
    # Restore
    set_preference('theme', old_theme)
    
    console.input("\nPress Enter to continue...")


def demo_preferences_display():
    """Demo preferences display."""
    console = Console()
    
    console.clear()
    console.print("[bold]Preferences Display Demo[/bold]\n")
    
    prefs = get_preferences()
    prefs.display()
    
    console.input("\nPress Enter to continue...")


def demo_preferences_export():
    """Demo exporting preferences."""
    console = Console()
    
    console.clear()
    console.print("[bold]Preferences Export Demo[/bold]\n")
    
    prefs = get_preferences()
    
    console.print("1. [cyan]Current preferences as dict:[/cyan]")
    prefs_dict = prefs.preferences.to_dict()
    
    # Show a few items
    for i, (key, value) in enumerate(prefs_dict.items()):
        if i >= 5:
            console.print("   ...")
            break
        console.print(f"   {key}: {value}")
    
    console.print(f"\n   Total settings: {len(prefs_dict)}")
    
    console.print("\n2. [cyan]Save to custom location:[/cyan]")
    custom_path = Path("/tmp/exported_preferences.json")
    prefs.preferences_path = custom_path
    if prefs.save():
        console.print(f"   [green]✓ Saved to {custom_path}[/green]")
    
    console.print("\n3. [cyan]Create from dict:[/cyan]")
    from .preferences import UserPreferences
    new_prefs = UserPreferences.from_dict({
        "theme": "solarized-dark",
        "page_size": 30,
        "show_icons": True
    })
    console.print(f"   Loaded theme: {new_prefs.theme}")
    console.print(f"   Loaded page_size: {new_prefs.page_size}")
    
    console.input("\nPress Enter to continue...")


def demo_apply_preferences():
    """Demo applying preferences."""
    console = Console()
    
    console.clear()
    console.print("[bold]Apply Preferences Demo[/bold]\n")
    
    console.print("Preferences can be applied to change application behavior:\n")
    
    # Show current theme
    current_theme = get_preference('theme')
    console.print(f"Current theme: {current_theme}")
    
    # Apply different themes
    themes = ["monokai", "dracula", "github-dark", "solarized-dark"]
    
    for theme in themes:
        if console.input(f"\nApply '{theme}' theme? (y/n): ").lower() == 'y':
            set_preference('theme', theme)
            apply_preferences()
            
            # Show sample with new theme
            console.print(Panel.fit(
                f"[bold]This is how the {theme} theme looks![/bold]\n"
                "[cyan]Colors[/cyan] and [yellow]syntax[/yellow] will change.",
                border_style="green"
            ))
    
    # Restore original
    set_preference('theme', current_theme)
    apply_preferences()


def main():
    """Run preferences demos."""
    console = Console()
    
    demos = [
        ("Basic Preferences Operations", demo_preferences_basics),
        ("Preference Types", demo_preference_types),
        ("Preferences Editor UI", demo_preferences_editor),
        ("Quick Preferences Menu", demo_quick_menu),
        ("Global Preferences Access", demo_global_preferences),
        ("Display All Preferences", demo_preferences_display),
        ("Export/Import Preferences", demo_preferences_export),
        ("Apply Preferences", demo_apply_preferences),
    ]
    
    while True:
        console.clear()
        console.print("[bold cyan]User Preferences Demo Suite[/bold cyan]\n")
        
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
            console.input("Press Enter to continue...")
    
    console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()