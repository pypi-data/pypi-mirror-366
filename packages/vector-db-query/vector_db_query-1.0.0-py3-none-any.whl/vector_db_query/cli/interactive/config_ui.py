"""Interactive configuration UI components."""

import json
import yaml
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable, Type
from pathlib import Path
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.text import Text
import questionary
from questionary import Choice

from .base import BaseUIComponent, UIConfig
from .styles import get_icon, get_color
from .keyboard import KeyboardHandler, Key
from .file_browser import FileBrowser


class ConfigType(Enum):
    """Configuration value types."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    CHOICE = "choice"


@dataclass
class ConfigField:
    """Configuration field definition."""
    
    key: str
    name: str
    description: str
    type: ConfigType
    default: Any = None
    required: bool = True
    choices: Optional[List[Any]] = None
    validator: Optional[Callable[[Any], bool]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None
    category: str = "General"
    advanced: bool = False
    
    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate field value.
        
        Args:
            value: Value to validate
            
        Returns:
            Valid flag and error message
        """
        # Check required
        if self.required and value is None:
            return False, "Value is required"
        
        if value is None:
            return True, None
        
        # Type validation
        if self.type == ConfigType.STRING:
            if not isinstance(value, str):
                return False, "Value must be a string"
            if self.pattern:
                import re
                if not re.match(self.pattern, value):
                    return False, f"Value must match pattern: {self.pattern}"
        
        elif self.type == ConfigType.INTEGER:
            if not isinstance(value, int):
                return False, "Value must be an integer"
            if self.min_value is not None and value < self.min_value:
                return False, f"Value must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"Value must be <= {self.max_value}"
        
        elif self.type == ConfigType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, "Value must be a number"
            if self.min_value is not None and value < self.min_value:
                return False, f"Value must be >= {self.min_value}"
            if self.max_value is not None and value > self.max_value:
                return False, f"Value must be <= {self.max_value}"
        
        elif self.type == ConfigType.BOOLEAN:
            if not isinstance(value, bool):
                return False, "Value must be true or false"
        
        elif self.type == ConfigType.LIST:
            if not isinstance(value, list):
                return False, "Value must be a list"
        
        elif self.type == ConfigType.DICT:
            if not isinstance(value, dict):
                return False, "Value must be a dictionary"
        
        elif self.type == ConfigType.PATH:
            try:
                path = Path(value).expanduser()
                # Just check it's a valid path format
            except Exception:
                return False, "Invalid path format"
        
        elif self.type == ConfigType.CHOICE:
            if self.choices and value not in self.choices:
                return False, f"Value must be one of: {', '.join(map(str, self.choices))}"
        
        # Custom validator
        if self.validator:
            try:
                if not self.validator(value):
                    return False, "Custom validation failed"
            except Exception as e:
                return False, f"Validation error: {str(e)}"
        
        return True, None


@dataclass
class ConfigSection:
    """Configuration section."""
    
    name: str
    title: str
    description: str
    fields: List[ConfigField] = field(default_factory=list)
    icon: Optional[str] = None
    
    def __post_init__(self):
        """Set default icon."""
        if self.icon is None:
            self.icon = get_icon("config")


class ConfigEditor(BaseUIComponent):
    """Interactive configuration editor."""
    
    def __init__(
        self,
        config_path: Path,
        schema: Optional[List[ConfigSection]] = None,
        format: str = "yaml",
        backup: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize config editor.
        
        Args:
            config_path: Path to configuration file
            schema: Configuration schema
            format: Config format (yaml/json)
            backup: Create backups before saving
            config: UI configuration
        """
        super().__init__(config)
        self.config_path = config_path
        self.schema = schema or []
        self.format = format
        self.backup = backup
        self.data: Dict[str, Any] = {}
        self.original_data: Dict[str, Any] = {}
        self.keyboard = KeyboardHandler(self.console)
        
        # Load existing config
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    if self.format == "yaml":
                        self.data = yaml.safe_load(f) or {}
                    else:
                        self.data = json.load(f)
                
                # Save original for comparison
                self.original_data = self.data.copy()
                
            except Exception as e:
                self.print_error(f"Failed to load config: {e}")
                self.data = {}
    
    def _save_config(self) -> bool:
        """Save configuration to file.
        
        Returns:
            Success flag
        """
        try:
            # Create backup if enabled
            if self.backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix(
                    self.config_path.suffix + ".bak"
                )
                import shutil
                shutil.copy2(self.config_path, backup_path)
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save config
            with open(self.config_path, 'w') as f:
                if self.format == "yaml":
                    yaml.dump(self.data, f, default_flow_style=False, indent=2)
                else:
                    json.dump(self.data, f, indent=2)
            
            # Update original
            self.original_data = self.data.copy()
            
            return True
            
        except Exception as e:
            self.print_error(f"Failed to save config: {e}")
            return False
    
    def edit(self) -> bool:
        """Edit configuration interactively.
        
        Returns:
            True if changes were saved
        """
        while True:
            self.clear()
            self._show_header()
            
            # Show menu
            choices = []
            
            # Add sections
            for section in self.schema:
                choices.append(Choice(
                    f"{section.icon} {section.title}",
                    section
                ))
            
            choices.extend([
                questionary.Separator(),
                Choice("📝 Edit Raw", "raw"),
                Choice("🔍 Search Settings", "search"),
                Choice("📊 View Current Config", "view"),
                Choice("💾 Save Changes", "save"),
                Choice("🔄 Reset to Defaults", "reset"),
                Choice("🚪 Exit", "exit"),
            ])
            
            selection = questionary.select(
                "Select action:",
                choices=choices,
                style=self.style
            ).ask()
            
            if selection == "exit":
                if self._has_changes():
                    if self.confirm("You have unsaved changes. Exit without saving?"):
                        return False
                else:
                    return False
            
            elif selection == "save":
                if self._save_config():
                    self.print_success("Configuration saved successfully!")
                    self.wait_for_enter()
                    return True
            
            elif selection == "raw":
                self._edit_raw()
            
            elif selection == "search":
                self._search_settings()
            
            elif selection == "view":
                self._view_config()
            
            elif selection == "reset":
                if self.confirm("Reset all settings to defaults?", destructive=True):
                    self._reset_to_defaults()
            
            elif isinstance(selection, ConfigSection):
                self._edit_section(selection)
    
    def _show_header(self) -> None:
        """Show editor header."""
        header = Panel(
            f"[bold]Configuration Editor[/bold]\n"
            f"File: {self.config_path}",
            border_style="blue"
        )
        self.console.print(header)
        
        # Show change indicator
        if self._has_changes():
            self.console.print("[yellow]⚠ You have unsaved changes[/yellow]")
        
        self.console.print()
    
    def _has_changes(self) -> bool:
        """Check if configuration has changes.
        
        Returns:
            True if changed
        """
        return self.data != self.original_data
    
    def _edit_section(self, section: ConfigSection) -> None:
        """Edit configuration section.
        
        Args:
            section: Section to edit
        """
        while True:
            self.clear()
            
            # Show section header
            self.show_panel(
                f"[bold]{section.title}[/bold]\n{section.description}",
                title=f"{section.icon} {section.name}",
                border_style="cyan"
            )
            self.console.print()
            
            # Build field choices
            choices = []
            for field in section.fields:
                # Get current value
                current = self._get_field_value(field.key)
                value_str = self._format_value(current, field.type)
                
                # Validation status
                valid, error = field.validate(current)
                if not valid and current is not None:
                    status = f" [red]({error})[/red]"
                else:
                    status = ""
                
                choices.append(Choice(
                    f"{field.name}: {value_str}{status}",
                    field
                ))
            
            choices.extend([
                questionary.Separator(),
                Choice("⬅️ Back", "back"),
            ])
            
            selection = questionary.select(
                "Select field to edit:",
                choices=choices,
                style=self.style
            ).ask()
            
            if selection == "back":
                break
            
            elif isinstance(selection, ConfigField):
                self._edit_field(selection)
    
    def _edit_field(self, field: ConfigField) -> None:
        """Edit configuration field.
        
        Args:
            field: Field to edit
        """
        self.clear()
        
        # Show field info
        info = f"[bold]{field.name}[/bold]\n"
        info += f"{field.description}\n\n"
        info += f"Type: {field.type.value}\n"
        
        if field.default is not None:
            info += f"Default: {self._format_value(field.default, field.type)}\n"
        
        if field.min_value is not None or field.max_value is not None:
            info += f"Range: {field.min_value or '-∞'} to {field.max_value or '∞'}\n"
        
        if field.choices:
            info += f"Choices: {', '.join(map(str, field.choices))}\n"
        
        self.show_panel(info, title="Field Information", border_style="blue")
        self.console.print()
        
        # Get current value
        current = self._get_field_value(field.key)
        
        # Get new value based on type
        new_value = self._get_field_input(field, current)
        
        if new_value is not None:
            # Validate
            valid, error = field.validate(new_value)
            if valid:
                self._set_field_value(field.key, new_value)
                self.print_success("Value updated successfully!")
            else:
                self.print_error(f"Invalid value: {error}")
            
            self.wait_for_enter()
    
    def _get_field_input(
        self,
        field: ConfigField,
        current: Any
    ) -> Optional[Any]:
        """Get input for field.
        
        Args:
            field: Field definition
            current: Current value
            
        Returns:
            New value or None
        """
        if field.type == ConfigType.STRING:
            return self.prompt(
                "Enter value:",
                default=str(current) if current is not None else ""
            )
        
        elif field.type == ConfigType.INTEGER:
            value = self.prompt(
                "Enter integer:",
                default=str(current) if current is not None else ""
            )
            try:
                return int(value) if value else None
            except ValueError:
                self.print_error("Invalid integer")
                return None
        
        elif field.type == ConfigType.FLOAT:
            value = self.prompt(
                "Enter number:",
                default=str(current) if current is not None else ""
            )
            try:
                return float(value) if value else None
            except ValueError:
                self.print_error("Invalid number")
                return None
        
        elif field.type == ConfigType.BOOLEAN:
            return self.confirm(
                "Enable?",
                default=current if current is not None else False
            )
        
        elif field.type == ConfigType.LIST:
            return self._edit_list(current or [])
        
        elif field.type == ConfigType.DICT:
            return self._edit_dict(current or {})
        
        elif field.type == ConfigType.PATH:
            return self._select_path(current)
        
        elif field.type == ConfigType.CHOICE:
            if field.choices:
                return self.select(
                    "Select value:",
                    choices=field.choices,
                    default=current
                )
        
        return None
    
    def _edit_list(self, current: List[Any]) -> List[Any]:
        """Edit list value.
        
        Args:
            current: Current list
            
        Returns:
            Updated list
        """
        items = current.copy()
        
        while True:
            self.clear()
            
            # Show current items
            self.print("[bold]List Items:[/bold]")
            if items:
                for i, item in enumerate(items):
                    self.print(f"{i+1}. {item}")
            else:
                self.print("[dim]No items[/dim]")
            
            self.console.print()
            
            # Options
            action = questionary.select(
                "Select action:",
                choices=[
                    Choice("Add item", "add"),
                    Choice("Remove item", "remove"),
                    Choice("Clear all", "clear"),
                    Choice("Done", "done"),
                ],
                style=self.style
            ).ask()
            
            if action == "done":
                return items
            elif action == "add":
                item = self.prompt("Enter item:")
                if item:
                    items.append(item)
            elif action == "remove" and items:
                choices = [
                    Choice(f"{i+1}. {item}", i)
                    for i, item in enumerate(items)
                ]
                idx = self.select("Select item to remove:", choices=choices)
                if idx is not None:
                    items.pop(idx)
            elif action == "clear":
                if self.confirm("Clear all items?", destructive=True):
                    items.clear()
    
    def _edit_dict(self, current: Dict[str, Any]) -> Dict[str, Any]:
        """Edit dictionary value.
        
        Args:
            current: Current dict
            
        Returns:
            Updated dict
        """
        data = current.copy()
        
        while True:
            self.clear()
            
            # Show current items
            self.print("[bold]Dictionary Items:[/bold]")
            if data:
                table = Table(show_header=True)
                table.add_column("Key", style="cyan")
                table.add_column("Value")
                
                for key, value in data.items():
                    table.add_row(key, str(value))
                
                self.console.print(table)
            else:
                self.print("[dim]No items[/dim]")
            
            self.console.print()
            
            # Options
            action = questionary.select(
                "Select action:",
                choices=[
                    Choice("Add/Edit item", "add"),
                    Choice("Remove item", "remove"),
                    Choice("Clear all", "clear"),
                    Choice("Done", "done"),
                ],
                style=self.style
            ).ask()
            
            if action == "done":
                return data
            elif action == "add":
                key = self.prompt("Enter key:")
                if key:
                    value = self.prompt("Enter value:")
                    data[key] = value
            elif action == "remove" and data:
                key = self.select(
                    "Select key to remove:",
                    choices=list(data.keys())
                )
                if key:
                    del data[key]
            elif action == "clear":
                if self.confirm("Clear all items?", destructive=True):
                    data.clear()
    
    def _select_path(self, current: Optional[str]) -> Optional[str]:
        """Select path using file browser.
        
        Args:
            current: Current path
            
        Returns:
            Selected path or None
        """
        # Manual input option
        use_browser = self.confirm("Use file browser?", default=True)
        
        if use_browser:
            start_path = Path(current).parent if current else Path.home()
            browser = FileBrowser(
                start_path=start_path,
                allow_multiple=False,
                preview_enabled=False
            )
            
            selected = browser.browse()
            if selected:
                return str(selected[0])
        else:
            return self.prompt(
                "Enter path:",
                default=current or ""
            )
        
        return None
    
    def _get_field_value(self, key: str) -> Any:
        """Get field value from config.
        
        Args:
            key: Field key (supports nested)
            
        Returns:
            Field value
        """
        parts = key.split('.')
        value = self.data
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None
        
        return value
    
    def _set_field_value(self, key: str, value: Any) -> None:
        """Set field value in config.
        
        Args:
            key: Field key (supports nested)
            value: New value
        """
        parts = key.split('.')
        data = self.data
        
        # Navigate to parent
        for part in parts[:-1]:
            if part not in data:
                data[part] = {}
            data = data[part]
        
        # Set value
        data[parts[-1]] = value
    
    def _format_value(self, value: Any, type: ConfigType) -> str:
        """Format value for display.
        
        Args:
            value: Value to format
            type: Value type
            
        Returns:
            Formatted string
        """
        if value is None:
            return "[dim]<not set>[/dim]"
        
        if type == ConfigType.BOOLEAN:
            return "[green]✓[/green]" if value else "[red]✗[/red]"
        elif type == ConfigType.LIST:
            return f"[{len(value)} items]"
        elif type == ConfigType.DICT:
            return f"{{{len(value)} items}}"
        elif type == ConfigType.PATH:
            path = Path(value)
            if path.exists():
                return f"{value} [green]✓[/green]"
            else:
                return f"{value} [red]✗[/red]"
        else:
            return str(value)
    
    def _edit_raw(self) -> None:
        """Edit raw configuration."""
        self.clear()
        
        # Show current config
        if self.format == "yaml":
            content = yaml.dump(self.data, default_flow_style=False, indent=2)
            syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
        else:
            content = json.dumps(self.data, indent=2)
            syntax = Syntax(content, "json", theme="monokai", line_numbers=True)
        
        self.console.print(syntax)
        self.console.print()
        
        self.print_warning("Raw editing not implemented in demo")
        self.wait_for_enter()
    
    def _search_settings(self) -> None:
        """Search configuration settings."""
        query = self.prompt("Search settings:")
        if not query:
            return
        
        query_lower = query.lower()
        results = []
        
        # Search fields
        for section in self.schema:
            for field in section.fields:
                if (query_lower in field.name.lower() or
                    query_lower in field.description.lower() or
                    query_lower in field.key.lower()):
                    results.append((section, field))
        
        if results:
            self.clear()
            self.print(f"[bold]Search Results for '{query}':[/bold]\n")
            
            for section, field in results:
                self.print(f"{section.icon} {section.title} > {field.name}")
                self.print(f"  [dim]{field.description}[/dim]")
                self.print()
        else:
            self.print_warning("No settings found")
        
        self.wait_for_enter()
    
    def _view_config(self) -> None:
        """View current configuration."""
        self.clear()
        
        # Build tree view
        tree = Tree("[bold]Current Configuration[/bold]")
        
        def add_node(parent: Tree, data: Dict[str, Any], prefix: str = ""):
            """Add nodes to tree."""
            for key, value in data.items():
                if isinstance(value, dict):
                    branch = parent.add(f"[cyan]{key}[/cyan]")
                    add_node(branch, value, f"{prefix}{key}.")
                else:
                    formatted = self._format_value(value, self._guess_type(value))
                    parent.add(f"[yellow]{key}[/yellow] = {formatted}")
        
        add_node(tree, self.data)
        
        self.console.print(tree)
        self.wait_for_enter()
    
    def _guess_type(self, value: Any) -> ConfigType:
        """Guess config type from value.
        
        Args:
            value: Value to check
            
        Returns:
            Guessed type
        """
        if isinstance(value, bool):
            return ConfigType.BOOLEAN
        elif isinstance(value, int):
            return ConfigType.INTEGER
        elif isinstance(value, float):
            return ConfigType.FLOAT
        elif isinstance(value, list):
            return ConfigType.LIST
        elif isinstance(value, dict):
            return ConfigType.DICT
        else:
            return ConfigType.STRING
    
    def _reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self.data = {}
        
        # Set defaults from schema
        for section in self.schema:
            for field in section.fields:
                if field.default is not None:
                    self._set_field_value(field.key, field.default)
        
        self.print_success("Configuration reset to defaults!")
        self.wait_for_enter()
    
    def render(self) -> bool:
        """Render component (calls edit).
        
        Returns:
            True if changes were saved
        """
        return self.edit()


class ConfigWizard(BaseUIComponent):
    """Configuration setup wizard."""
    
    def __init__(
        self,
        schema: List[ConfigSection],
        config: Optional[UIConfig] = None
    ):
        """Initialize config wizard.
        
        Args:
            schema: Configuration schema
            config: UI configuration
        """
        super().__init__(config)
        self.schema = schema
        self.data: Dict[str, Any] = {}
    
    def run(self) -> Dict[str, Any]:
        """Run configuration wizard.
        
        Returns:
            Configuration data
        """
        self.clear()
        
        # Welcome
        self.show_panel(
            "[bold]Configuration Wizard[/bold]\n\n"
            "This wizard will help you set up your configuration.\n"
            "You can always change these settings later.",
            title="Welcome",
            border_style="green"
        )
        self.wait_for_enter()
        
        # Process sections
        for i, section in enumerate(self.schema):
            self.clear()
            
            # Show progress
            progress = f"Step {i+1} of {len(self.schema)}"
            self.console.print(f"[dim]{progress}[/dim]\n")
            
            # Show section info
            self.show_panel(
                f"[bold]{section.title}[/bold]\n{section.description}",
                title=f"{section.icon} {section.name}",
                border_style="blue"
            )
            self.console.print()
            
            # Process required fields only
            for field in section.fields:
                if not field.required and not field.default:
                    continue
                
                self._process_field(field)
        
        # Summary
        self._show_summary()
        
        return self.data
    
    def _process_field(self, field: ConfigField) -> None:
        """Process single field in wizard.
        
        Args:
            field: Field to process
        """
        # Show field info
        self.print(f"[bold]{field.name}[/bold]")
        self.print(f"[dim]{field.description}[/dim]")
        
        # Get value
        if field.type == ConfigType.BOOLEAN:
            value = self.confirm(
                "Enable?",
                default=bool(field.default) if field.default is not None else False
            )
        elif field.type == ConfigType.CHOICE and field.choices:
            value = self.select(
                "Select:",
                choices=field.choices,
                default=field.default
            )
        else:
            default_str = str(field.default) if field.default is not None else ""
            value = self.prompt(f"Enter {field.type.value}:", default=default_str)
            
            # Convert type
            if field.type == ConfigType.INTEGER and value:
                try:
                    value = int(value)
                except ValueError:
                    self.print_error("Invalid integer, using default")
                    value = field.default
            elif field.type == ConfigType.FLOAT and value:
                try:
                    value = float(value)
                except ValueError:
                    self.print_error("Invalid number, using default")
                    value = field.default
        
        # Validate
        valid, error = field.validate(value)
        if not valid:
            self.print_error(f"Invalid value: {error}")
            if field.default is not None:
                self.print_info(f"Using default: {field.default}")
                value = field.default
            else:
                # Retry
                self._process_field(field)
                return
        
        # Store value
        self._set_field_value(field.key, value)
        self.console.print()
    
    def _set_field_value(self, key: str, value: Any) -> None:
        """Set field value in data.
        
        Args:
            key: Field key
            value: Field value
        """
        parts = key.split('.')
        data = self.data
        
        for part in parts[:-1]:
            if part not in data:
                data[part] = {}
            data = data[part]
        
        data[parts[-1]] = value
    
    def _show_summary(self) -> None:
        """Show configuration summary."""
        self.clear()
        
        self.print("[bold]Configuration Summary[/bold]\n")
        
        # Format as YAML for readability
        content = yaml.dump(self.data, default_flow_style=False, indent=2)
        syntax = Syntax(content, "yaml", theme="monokai")
        
        self.console.print(syntax)
        self.console.print()
        
        if not self.confirm("Is this correct?", default=True):
            # Allow editing
            self.print_info("Wizard editing not implemented in demo")
    
    def render(self) -> Dict[str, Any]:
        """Render component (calls run).
        
        Returns:
            Configuration data
        """
        return self.run()