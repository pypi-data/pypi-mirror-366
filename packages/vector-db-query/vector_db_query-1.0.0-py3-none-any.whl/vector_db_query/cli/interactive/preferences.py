"""User preferences management for interactive CLI."""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import questionary

from .styles import THEME_STYLES
from .base import BaseUIComponent


class PreferenceType(Enum):
    """Preference value types."""
    BOOLEAN = "boolean"
    STRING = "string"
    INTEGER = "integer"
    CHOICE = "choice"
    LIST = "list"
    THEME = "theme"
    PATH = "path"


@dataclass
class PreferenceItem:
    """Individual preference definition."""
    key: str
    name: str
    description: str
    type: PreferenceType
    default: Any
    value: Optional[Any] = None
    choices: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    category: str = "General"
    
    def get_value(self) -> Any:
        """Get current value or default."""
        return self.value if self.value is not None else self.default
    
    def validate(self, value: Any) -> bool:
        """Validate a value for this preference.
        
        Args:
            value: Value to validate
            
        Returns:
            True if valid
        """
        if self.type == PreferenceType.BOOLEAN:
            return isinstance(value, bool)
        elif self.type == PreferenceType.STRING:
            return isinstance(value, str)
        elif self.type == PreferenceType.INTEGER:
            if not isinstance(value, int):
                return False
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False
            return True
        elif self.type == PreferenceType.CHOICE:
            return value in (self.choices or [])
        elif self.type == PreferenceType.LIST:
            return isinstance(value, list)
        elif self.type == PreferenceType.THEME:
            return value in THEME_STYLES
        elif self.type == PreferenceType.PATH:
            return isinstance(value, (str, Path))
        return False


@dataclass
class UserPreferences:
    """User preferences container."""
    # Display preferences
    theme: str = "monokai"
    show_icons: bool = True
    use_animations: bool = True
    animation_speed: float = 0.3
    page_size: int = 20
    
    # File browser preferences
    show_hidden_files: bool = False
    file_preview_lines: int = 50
    file_browser_sort: str = "name"
    default_file_filters: List[str] = field(default_factory=lambda: [".txt", ".md", ".pdf"])
    
    # Query preferences
    save_query_history: bool = True
    query_history_size: int = 100
    show_query_suggestions: bool = True
    default_query_limit: int = 10
    
    # Result preferences
    default_result_format: str = "cards"
    highlight_matches: bool = True
    export_include_metadata: bool = True
    
    # Progress preferences
    show_progress_stats: bool = True
    progress_update_interval: float = 0.1
    
    # Keyboard preferences
    enable_vim_bindings: bool = False
    show_keyboard_hints: bool = True
    
    # MCP preferences
    mcp_auto_start: bool = False
    mcp_log_requests: bool = False
    
    # System preferences
    auto_save_config: bool = True
    confirm_exit: bool = True
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if hasattr(cls, k)})


class PreferencesManager(BaseUIComponent):
    """Manage user preferences."""
    
    def __init__(self, preferences_path: Optional[Path] = None):
        """Initialize preferences manager.
        
        Args:
            preferences_path: Path to preferences file
        """
        super().__init__()
        self.preferences_path = preferences_path or (
            Path.home() / ".vector_db_query" / "preferences.json"
        )
        self.preferences = UserPreferences()
        self.preference_items: Dict[str, PreferenceItem] = {}
        self._define_preferences()
        self.load()
    
    def _define_preferences(self) -> None:
        """Define all preference items."""
        # Display preferences
        self.add_preference(PreferenceItem(
            key="theme",
            name="Color Theme",
            description="Syntax highlighting theme",
            type=PreferenceType.THEME,
            default="monokai",
            category="Display"
        ))
        self.add_preference(PreferenceItem(
            key="show_icons",
            name="Show Icons",
            description="Display icons in menus and lists",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Display"
        ))
        self.add_preference(PreferenceItem(
            key="use_animations",
            name="Enable Animations",
            description="Show menu and transition animations",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Display"
        ))
        self.add_preference(PreferenceItem(
            key="animation_speed",
            name="Animation Speed",
            description="Speed of animations (0.1-1.0)",
            type=PreferenceType.INTEGER,
            default=0.3,
            min_value=0.1,
            max_value=1.0,
            category="Display"
        ))
        self.add_preference(PreferenceItem(
            key="page_size",
            name="Page Size",
            description="Items per page in lists",
            type=PreferenceType.INTEGER,
            default=20,
            min_value=5,
            max_value=100,
            category="Display"
        ))
        
        # File browser preferences
        self.add_preference(PreferenceItem(
            key="show_hidden_files",
            name="Show Hidden Files",
            description="Display hidden files in browser",
            type=PreferenceType.BOOLEAN,
            default=False,
            category="File Browser"
        ))
        self.add_preference(PreferenceItem(
            key="file_preview_lines",
            name="Preview Lines",
            description="Number of lines in file preview",
            type=PreferenceType.INTEGER,
            default=50,
            min_value=10,
            max_value=500,
            category="File Browser"
        ))
        self.add_preference(PreferenceItem(
            key="file_browser_sort",
            name="Sort Order",
            description="Default file sort order",
            type=PreferenceType.CHOICE,
            default="name",
            choices=["name", "size", "modified", "type"],
            category="File Browser"
        ))
        
        # Query preferences
        self.add_preference(PreferenceItem(
            key="save_query_history",
            name="Save Query History",
            description="Remember previous queries",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Query"
        ))
        self.add_preference(PreferenceItem(
            key="query_history_size",
            name="History Size",
            description="Number of queries to remember",
            type=PreferenceType.INTEGER,
            default=100,
            min_value=10,
            max_value=1000,
            category="Query"
        ))
        self.add_preference(PreferenceItem(
            key="show_query_suggestions",
            name="Show Suggestions",
            description="Display query suggestions",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Query"
        ))
        
        # Result preferences
        self.add_preference(PreferenceItem(
            key="default_result_format",
            name="Result Format",
            description="Default result display format",
            type=PreferenceType.CHOICE,
            default="cards",
            choices=["cards", "table", "json", "detailed"],
            category="Results"
        ))
        self.add_preference(PreferenceItem(
            key="highlight_matches",
            name="Highlight Matches",
            description="Highlight query terms in results",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Results"
        ))
        
        # Keyboard preferences
        self.add_preference(PreferenceItem(
            key="enable_vim_bindings",
            name="Vim Bindings",
            description="Enable Vim-style keyboard shortcuts",
            type=PreferenceType.BOOLEAN,
            default=False,
            category="Keyboard"
        ))
        self.add_preference(PreferenceItem(
            key="show_keyboard_hints",
            name="Show Hints",
            description="Display keyboard shortcut hints",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="Keyboard"
        ))
        
        # System preferences
        self.add_preference(PreferenceItem(
            key="auto_save_config",
            name="Auto Save",
            description="Automatically save configuration changes",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="System"
        ))
        self.add_preference(PreferenceItem(
            key="confirm_exit",
            name="Confirm Exit",
            description="Ask before exiting application",
            type=PreferenceType.BOOLEAN,
            default=True,
            category="System"
        ))
        self.add_preference(PreferenceItem(
            key="log_level",
            name="Log Level",
            description="Logging verbosity",
            type=PreferenceType.CHOICE,
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            category="System"
        ))
    
    def add_preference(self, item: PreferenceItem) -> None:
        """Add a preference item.
        
        Args:
            item: Preference item to add
        """
        self.preference_items[item.key] = item
        
        # Set current value from preferences
        if hasattr(self.preferences, item.key):
            item.value = getattr(self.preferences, item.key)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get preference value.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value
        """
        return getattr(self.preferences, key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """Set preference value.
        
        Args:
            key: Preference key
            value: New value
            
        Returns:
            True if set successfully
        """
        if key in self.preference_items:
            item = self.preference_items[key]
            if item.validate(value):
                setattr(self.preferences, key, value)
                item.value = value
                if self.preferences.auto_save_config:
                    self.save()
                return True
        return False
    
    def reset(self, key: Optional[str] = None) -> None:
        """Reset preferences to defaults.
        
        Args:
            key: Specific key to reset, or None for all
        """
        if key:
            if key in self.preference_items:
                item = self.preference_items[key]
                self.set(key, item.default)
        else:
            # Reset all
            self.preferences = UserPreferences()
            for item in self.preference_items.values():
                item.value = item.default
            if self.preferences.auto_save_config:
                self.save()
    
    def save(self) -> bool:
        """Save preferences to file.
        
        Returns:
            True if saved successfully
        """
        try:
            self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.preferences_path, 'w') as f:
                json.dump(self.preferences.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to save preferences: {e}[/red]")
            return False
    
    def load(self) -> bool:
        """Load preferences from file.
        
        Returns:
            True if loaded successfully
        """
        if not self.preferences_path.exists():
            return False
        
        try:
            with open(self.preferences_path, 'r') as f:
                data = json.load(f)
            
            self.preferences = UserPreferences.from_dict(data)
            
            # Update items
            for key, value in data.items():
                if key in self.preference_items:
                    self.preference_items[key].value = value
            
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to load preferences: {e}[/red]")
            return False
    
    def edit_interactive(self) -> bool:
        """Edit preferences interactively.
        
        Returns:
            True if any changes were made
        """
        changes_made = False
        
        while True:
            self.console.clear()
            self.console.print(Panel.fit(
                "[bold cyan]User Preferences[/bold cyan]",
                border_style="cyan"
            ))
            
            # Group by category
            categories = {}
            for item in self.preference_items.values():
                if item.category not in categories:
                    categories[item.category] = []
                categories[item.category].append(item)
            
            # Show menu
            choices = []
            for category in sorted(categories.keys()):
                choices.append(f"[{category}]")
                for item in categories[category]:
                    value_str = str(item.get_value())
                    if item.type == PreferenceType.BOOLEAN:
                        value_str = "✓" if item.get_value() else "✗"
                    choices.append(f"  {item.name}: {value_str}")
            
            choices.extend(["", "Reset All to Defaults", "Save and Exit", "Cancel"])
            
            choice = questionary.select(
                "Select preference to edit:",
                choices=choices
            ).ask()
            
            if choice == "Cancel":
                break
            elif choice == "Save and Exit":
                if self.save():
                    self.console.print("[green]Preferences saved![/green]")
                break
            elif choice == "Reset All to Defaults":
                if questionary.confirm("Reset all preferences to defaults?").ask():
                    self.reset()
                    changes_made = True
                    self.console.print("[yellow]All preferences reset[/yellow]")
                    self.console.input("\nPress Enter to continue...")
            elif choice and not choice.startswith("["):
                # Find the item
                item_name = choice.strip().split(":")[0]
                item = next((i for i in self.preference_items.values() 
                            if i.name == item_name), None)
                
                if item:
                    new_value = self._edit_preference(item)
                    if new_value is not None and new_value != item.get_value():
                        if self.set(item.key, new_value):
                            changes_made = True
                            self.console.print(f"[green]Updated {item.name}[/green]")
                        else:
                            self.console.print(f"[red]Invalid value for {item.name}[/red]")
                        self.console.input("\nPress Enter to continue...")
        
        return changes_made
    
    def _edit_preference(self, item: PreferenceItem) -> Optional[Any]:
        """Edit a single preference.
        
        Args:
            item: Preference item to edit
            
        Returns:
            New value or None
        """
        self.console.clear()
        self.console.print(f"[bold]{item.name}[/bold]")
        self.console.print(f"[dim]{item.description}[/dim]")
        self.console.print(f"\nCurrent value: {item.get_value()}")
        self.console.print(f"Default value: {item.default}\n")
        
        if item.type == PreferenceType.BOOLEAN:
            return questionary.confirm(
                "New value:",
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.STRING:
            return questionary.text(
                "New value:",
                default=str(item.get_value())
            ).ask()
        
        elif item.type == PreferenceType.INTEGER:
            prompt = "New value"
            if item.min_value is not None or item.max_value is not None:
                prompt += f" ({item.min_value or ''}-{item.max_value or ''})"
            prompt += ":"
            
            value = questionary.text(
                prompt,
                default=str(item.get_value())
            ).ask()
            
            try:
                return int(value) if value else None
            except ValueError:
                return None
        
        elif item.type == PreferenceType.CHOICE:
            return questionary.select(
                "New value:",
                choices=item.choices or [],
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.THEME:
            return questionary.select(
                "New value:",
                choices=list(THEME_STYLES.keys()),
                default=item.get_value()
            ).ask()
        
        elif item.type == PreferenceType.PATH:
            return questionary.path(
                "New value:",
                default=str(item.get_value())
            ).ask()
        
        elif item.type == PreferenceType.LIST:
            # Simple comma-separated input
            current = ", ".join(item.get_value() or [])
            new_value = questionary.text(
                "New value (comma-separated):",
                default=current
            ).ask()
            
            if new_value:
                return [v.strip() for v in new_value.split(",") if v.strip()]
            return None
        
        return None
    
    def display(self) -> None:
        """Display current preferences."""
        self.console.clear()
        self.console.print(Panel.fit(
            "[bold cyan]Current Preferences[/bold cyan]",
            border_style="cyan"
        ))
        
        # Group by category
        categories = {}
        for item in self.preference_items.values():
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        for category in sorted(categories.keys()):
            self.console.print(f"\n[bold yellow]{category}:[/bold yellow]")
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Name", style="cyan")
            table.add_column("Value", style="white")
            table.add_column("Description", style="dim")
            
            for item in categories[category]:
                value_str = str(item.get_value())
                if item.type == PreferenceType.BOOLEAN:
                    value_str = "[green]✓[/green]" if item.get_value() else "[red]✗[/red]"
                
                table.add_row(
                    item.name,
                    value_str,
                    item.description
                )
            
            self.console.print(table)


# Global preferences instance
_global_preferences: Optional[PreferencesManager] = None


def get_preferences() -> PreferencesManager:
    """Get global preferences instance.
    
    Returns:
        Global preferences manager
    """
    global _global_preferences
    if _global_preferences is None:
        _global_preferences = PreferencesManager()
    return _global_preferences


def get_preference(key: str, default: Any = None) -> Any:
    """Get a preference value.
    
    Args:
        key: Preference key
        default: Default value
        
    Returns:
        Preference value
    """
    return get_preferences().get(key, default)


def set_preference(key: str, value: Any) -> bool:
    """Set a preference value.
    
    Args:
        key: Preference key
        value: New value
        
    Returns:
        True if set successfully
    """
    return get_preferences().set(key, value)