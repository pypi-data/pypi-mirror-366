"""UI components for preferences management."""

from typing import Optional, Dict, List, Any
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.columns import Columns
import questionary

from .base import BaseUIComponent
from .preferences import (
    PreferencesManager, PreferenceItem, PreferenceType,
    get_preferences
)
from .keyboard import KeyboardHandler, Key
from .styles import get_rich_theme


class PreferencesEditor(BaseUIComponent):
    """Interactive preferences editor with live preview."""
    
    def __init__(self, preferences_manager: Optional[PreferencesManager] = None):
        """Initialize preferences editor.
        
        Args:
            preferences_manager: Preferences manager instance
        """
        super().__init__()
        self.manager = preferences_manager or get_preferences()
        self.keyboard = KeyboardHandler(self.console)
        self.current_category = 0
        self.current_item = 0
        self.categories: List[str] = []
        self.items_by_category: Dict[str, List[PreferenceItem]] = {}
        self._organize_preferences()
    
    def _organize_preferences(self) -> None:
        """Organize preferences by category."""
        self.items_by_category.clear()
        
        for item in self.manager.preference_items.values():
            if item.category not in self.items_by_category:
                self.items_by_category[item.category] = []
            self.items_by_category[item.category].append(item)
        
        self.categories = sorted(self.items_by_category.keys())
    
    def edit(self) -> bool:
        """Edit preferences with live preview.
        
        Returns:
            True if changes were made
        """
        changes_made = False
        
        with Live(self._create_layout(), refresh_per_second=10) as live:
            while True:
                key = self._get_key()
                
                if key == Key.ESCAPE.value or key == 'q':
                    break
                elif key == Key.UP.value:
                    self._navigate_up()
                elif key == Key.DOWN.value:
                    self._navigate_down()
                elif key == Key.LEFT.value:
                    self._navigate_category(-1)
                elif key == Key.RIGHT.value:
                    self._navigate_category(1)
                elif key == Key.ENTER.value or key == ' ':
                    if self._edit_current_item():
                        changes_made = True
                elif key == 'r':
                    if self._reset_current_item():
                        changes_made = True
                elif key == 'R':
                    if self._reset_all():
                        changes_made = True
                elif key == 's':
                    if self.manager.save():
                        self.console.print("\n[green]Preferences saved![/green]")
                        break
                elif key == '?':
                    self._show_help()
                
                live.update(self._create_layout())
        
        return changes_made
    
    def _create_layout(self) -> Layout:
        """Create the editor layout."""
        layout = Layout()
        
        # Header
        header = Panel(
            "[bold cyan]Preferences Editor[/bold cyan]\n"
            "[dim]↑↓ Navigate • ←→ Switch Category • Enter Edit • r Reset • s Save • q Exit[/dim]",
            border_style="cyan"
        )
        
        # Categories
        category_list = []
        for i, cat in enumerate(self.categories):
            if i == self.current_category:
                category_list.append(f"[bold cyan]▶ {cat}[/bold cyan]")
            else:
                category_list.append(f"  {cat}")
        
        categories_panel = Panel(
            "\n".join(category_list),
            title="Categories",
            border_style="blue"
        )
        
        # Current category items
        current_cat = self.categories[self.current_category]
        items = self.items_by_category[current_cat]
        
        items_table = Table(show_header=True, header_style="bold magenta")
        items_table.add_column("Setting", style="cyan")
        items_table.add_column("Value", style="yellow")
        items_table.add_column("Description", style="dim")
        
        for i, item in enumerate(items):
            # Format value
            value_str = self._format_value(item)
            
            # Highlight current item
            if i == self.current_item:
                items_table.add_row(
                    f"[bold]▶ {item.name}[/bold]",
                    f"[bold]{value_str}[/bold]",
                    item.description
                )
            else:
                items_table.add_row(
                    f"  {item.name}",
                    value_str,
                    item.description
                )
        
        items_panel = Panel(
            items_table,
            title=f"{current_cat} Settings",
            border_style="green"
        )
        
        # Layout structure
        layout.split_column(
            Layout(header, size=4),
            Layout().split_row(
                Layout(categories_panel, ratio=1),
                Layout(items_panel, ratio=3)
            )
        )
        
        return layout
    
    def _format_value(self, item: PreferenceItem) -> str:
        """Format preference value for display.
        
        Args:
            item: Preference item
            
        Returns:
            Formatted value
        """
        value = item.get_value()
        
        if item.type == PreferenceType.BOOLEAN:
            return "[green]✓[/green]" if value else "[red]✗[/red]"
        elif item.type == PreferenceType.LIST:
            return ", ".join(value) if value else "[dim]empty[/dim]"
        elif item.type == PreferenceType.PATH:
            return str(Path(value).name) if value else "[dim]not set[/dim]"
        else:
            return str(value)
    
    def _get_key(self) -> str:
        """Get keyboard input."""
        with self.keyboard.raw_mode():
            return self.keyboard.read_key()
    
    def _navigate_up(self) -> None:
        """Navigate up in current category."""
        current_cat = self.categories[self.current_category]
        items = self.items_by_category[current_cat]
        self.current_item = (self.current_item - 1) % len(items)
    
    def _navigate_down(self) -> None:
        """Navigate down in current category."""
        current_cat = self.categories[self.current_category]
        items = self.items_by_category[current_cat]
        self.current_item = (self.current_item + 1) % len(items)
    
    def _navigate_category(self, direction: int) -> None:
        """Navigate between categories.
        
        Args:
            direction: -1 for left, 1 for right
        """
        self.current_category = (self.current_category + direction) % len(self.categories)
        self.current_item = 0
    
    def _edit_current_item(self) -> bool:
        """Edit the currently selected item.
        
        Returns:
            True if value changed
        """
        current_cat = self.categories[self.current_category]
        items = self.items_by_category[current_cat]
        item = items[self.current_item]
        
        # Clear live display temporarily
        self.console.clear()
        
        # Edit item
        new_value = self._edit_preference_value(item)
        
        if new_value is not None and new_value != item.get_value():
            if self.manager.set(item.key, new_value):
                return True
        
        return False
    
    def _edit_preference_value(self, item: PreferenceItem) -> Optional[Any]:
        """Edit a preference value with appropriate input.
        
        Args:
            item: Preference item
            
        Returns:
            New value or None
        """
        self.console.print(f"\n[bold]Edit: {item.name}[/bold]")
        self.console.print(f"[dim]{item.description}[/dim]\n")
        
        if item.type == PreferenceType.BOOLEAN:
            # Toggle boolean
            current = item.get_value()
            return not current
        
        elif item.type == PreferenceType.INTEGER:
            prompt = "Enter new value"
            if item.min_value is not None or item.max_value is not None:
                prompt += f" ({item.min_value or ''}-{item.max_value or ''})"
            
            value = questionary.text(
                prompt + ":",
                default=str(item.get_value())
            ).ask()
            
            try:
                return int(value) if value else None
            except ValueError:
                self.console.print("[red]Invalid integer value[/red]")
                return None
        
        elif item.type == PreferenceType.CHOICE:
            return questionary.select(
                "Select value:",
                choices=item.choices or [],
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.STRING:
            return questionary.text(
                "Enter new value:",
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.LIST:
            current = ", ".join(item.get_value() or [])
            new_value = questionary.text(
                "Enter values (comma-separated):",
                default=current
            ).ask()
            
            if new_value is not None:
                return [v.strip() for v in new_value.split(",") if v.strip()]
            return None
        
        elif item.type == PreferenceType.THEME:
            from .styles import THEME_STYLES
            return questionary.select(
                "Select theme:",
                choices=list(THEME_STYLES.keys()),
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.PATH:
            return questionary.path(
                "Enter path:",
                default=str(item.get_value() or "")
            ).ask()
        
        return None
    
    def _reset_current_item(self) -> bool:
        """Reset current item to default.
        
        Returns:
            True if reset
        """
        current_cat = self.categories[self.current_category]
        items = self.items_by_category[current_cat]
        item = items[self.current_item]
        
        if item.get_value() != item.default:
            self.manager.set(item.key, item.default)
            return True
        
        return False
    
    def _reset_all(self) -> bool:
        """Reset all preferences to defaults.
        
        Returns:
            True if reset
        """
        self.console.clear()
        if questionary.confirm("Reset ALL preferences to defaults?").ask():
            self.manager.reset()
            return True
        return False
    
    def _show_help(self) -> None:
        """Show help screen."""
        self.console.clear()
        help_text = """
[bold cyan]Preferences Editor Help[/bold cyan]

[yellow]Navigation:[/yellow]
  ↑/↓         Navigate items in category
  ←/→         Switch between categories
  Tab         Jump to search

[yellow]Editing:[/yellow]
  Enter/Space Edit selected preference
  r           Reset current item to default
  R           Reset ALL to defaults
  
[yellow]File:[/yellow]
  s           Save preferences
  Ctrl+S      Save without exiting
  
[yellow]General:[/yellow]
  ?           Show this help
  q/Esc       Exit editor

[yellow]Value Types:[/yellow]
  • Boolean:  Toggle with Enter
  • Number:   Enter numeric value
  • Choice:   Select from list
  • String:   Enter text value
  • List:     Comma-separated values
  • Path:     File/directory path
"""
        self.console.print(help_text)
        self.console.input("\nPress Enter to continue...")


class PreferencesQuickMenu(BaseUIComponent):
    """Quick access menu for common preferences."""
    
    def __init__(self, preferences_manager: Optional[PreferencesManager] = None):
        """Initialize quick menu.
        
        Args:
            preferences_manager: Preferences manager
        """
        super().__init__()
        self.manager = preferences_manager or get_preferences()
        
        # Define quick access items
        self.quick_items = [
            "theme",
            "show_icons",
            "use_animations",
            "page_size",
            "show_hidden_files",
            "highlight_matches",
            "show_keyboard_hints",
            "confirm_exit",
        ]
    
    def show(self) -> bool:
        """Show quick preferences menu.
        
        Returns:
            True if any changes made
        """
        changes_made = False
        
        while True:
            self.console.clear()
            self.console.print(Panel.fit(
                "[bold cyan]Quick Preferences[/bold cyan]",
                border_style="cyan"
            ))
            
            # Build menu
            choices = []
            for key in self.quick_items:
                if key in self.manager.preference_items:
                    item = self.manager.preference_items[key]
                    value_str = self._format_value(item)
                    choices.append(f"{item.name}: {value_str}")
            
            choices.extend(["", "Open Full Editor", "Save Changes", "Exit"])
            
            choice = questionary.select(
                "Select preference to toggle/edit:",
                choices=choices
            ).ask()
            
            if choice == "Exit":
                break
            elif choice == "Save Changes":
                if self.manager.save():
                    self.console.print("[green]Preferences saved![/green]")
                break
            elif choice == "Open Full Editor":
                editor = PreferencesEditor(self.manager)
                if editor.edit():
                    changes_made = True
            elif choice and choice != "":
                # Find and edit item
                name = choice.split(":")[0]
                item = next((i for i in self.manager.preference_items.values()
                            if i.name == name), None)
                
                if item:
                    if item.type == PreferenceType.BOOLEAN:
                        # Quick toggle
                        new_value = not item.get_value()
                        if self.manager.set(item.key, new_value):
                            changes_made = True
                    else:
                        # Full edit
                        new_value = self._edit_preference_value(item)
                        if new_value is not None and new_value != item.get_value():
                            if self.manager.set(item.key, new_value):
                                changes_made = True
        
        return changes_made
    
    def _format_value(self, item: PreferenceItem) -> str:
        """Format value for display."""
        value = item.get_value()
        
        if item.type == PreferenceType.BOOLEAN:
            return "[green]ON[/green]" if value else "[red]OFF[/red]"
        else:
            return str(value)
    
    def _edit_preference_value(self, item: PreferenceItem) -> Optional[Any]:
        """Edit a preference value."""
        editor = PreferencesEditor(self.manager)
        return editor._edit_preference_value(item)


def apply_preferences(preferences: Optional[PreferencesManager] = None) -> None:
    """Apply current preferences to the application.
    
    Args:
        preferences: Preferences manager
    """
    prefs = preferences or get_preferences()
    console = Console()
    
    # Apply theme
    theme = prefs.get("theme", "monokai")
    console.theme = get_rich_theme(theme)
    
    # Apply other preferences as needed
    # This would be called by components that need to react to preference changes
    
    console.print(f"[dim]Applied preferences (theme: {theme})[/dim]")