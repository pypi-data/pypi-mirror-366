"""Enhanced menu system with keyboard navigation and rich display."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
from pathlib import Path

import questionary
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align

from .styles import get_custom_style, get_rich_theme, get_icon
from .animations import MenuAnimations, TransitionEffect, MenuDecorations
from .keyboard import KeyboardHandler, Key
from .navigation import NavigationManager, NavigationItem


@dataclass
class MenuItem:
    """Menu item configuration."""
    
    key: str
    label: str
    handler: Optional[Callable[[], Any]] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    submenu: Optional['InteractiveMenu'] = None
    enabled: bool = True
    visible: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default icon based on key if not provided."""
        if self.icon is None:
            self.icon = get_icon(self.key.lower())
    
    @property
    def display_label(self) -> str:
        """Get label with icon for display."""
        if self.icon:
            return f"{self.icon} {self.label}"
        return self.label
    
    @property
    def is_separator(self) -> bool:
        """Check if this is a separator item."""
        return self.key == "---"


class InteractiveMenu:
    """Enhanced interactive menu with rich display and keyboard navigation."""
    
    def __init__(
        self,
        title: str,
        items: Optional[List[MenuItem]] = None,
        parent: Optional['InteractiveMenu'] = None,
        theme: str = "default",
        show_help: bool = True,
        show_breadcrumb: bool = True,
        enable_animations: bool = True,
        enable_keyboard_nav: bool = True
    ):
        """Initialize interactive menu.
        
        Args:
            title: Menu title
            items: List of menu items
            parent: Parent menu for navigation
            theme: Theme name for styling
            show_help: Show keyboard help
            show_breadcrumb: Show navigation breadcrumb
            enable_animations: Enable menu animations
            enable_keyboard_nav: Enable keyboard navigation
        """
        self.title = title
        self.items = items or []
        self.parent = parent
        self.theme = theme
        self.show_help = show_help
        self.show_breadcrumb = show_breadcrumb
        self.enable_animations = enable_animations
        self.enable_keyboard_nav = enable_keyboard_nav
        self.console = Console(theme=get_rich_theme(theme))
        self.style = get_custom_style(theme)
        self._history: List[str] = []
        
        # Initialize components
        self.animations = MenuAnimations()
        self.transitions = TransitionEffect(self.console)
        self.keyboard = KeyboardHandler(self.console)
        self.navigation = NavigationManager(self.console)
        
        # Set up keyboard shortcuts
        self._setup_keyboard_shortcuts()
    
    def add_item(self, item: MenuItem) -> None:
        """Add item to menu."""
        self.items.append(item)
    
    def add_separator(self) -> None:
        """Add separator to menu."""
        self.add_item(MenuItem(key="---", label=""))
    
    def remove_item(self, key: str) -> bool:
        """Remove item by key."""
        for i, item in enumerate(self.items):
            if item.key == key:
                del self.items[i]
                return True
        return False
    
    def get_item(self, key: str) -> Optional[MenuItem]:
        """Get item by key."""
        for item in self.items:
            if item.key == key:
                return item
        return None
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts for menu navigation."""
        if not self.enable_keyboard_nav:
            return
        
        # Number shortcuts for first 9 items
        for i, item in enumerate(self.items[:9]):
            if not item.is_separator:
                self.keyboard.register(
                    f"select_{i+1}",
                    str(i + 1),
                    f"Select {item.label}",
                    lambda idx=i: self._select_by_index(idx),
                    category="Quick Select"
                )
        
        # Search functionality
        self.keyboard.register(
            "search",
            "/",
            "Search menu items",
            self._search_items,
            category="Navigation"
        )
        
        # Theme switching
        self.keyboard.register(
            "theme",
            "t",
            "Switch theme",
            self._cycle_theme,
            category="Display"
        )
        
        # Navigation history
        self.keyboard.register(
            "history",
            "ctrl+h",
            "Show navigation history",
            self._show_navigation_history,
            category="Navigation"
        )
    
    def _select_by_index(self, index: int) -> str:
        """Select menu item by index."""
        if 0 <= index < len(self.items):
            item = self.items[index]
            if item.enabled and not item.is_separator:
                return item.key
        return ""
    
    def _search_items(self) -> Optional[str]:
        """Search menu items interactively."""
        from questionary import autocomplete
        
        # Build searchable items
        choices = []
        for item in self.items:
            if item.visible and not item.is_separator:
                choices.append({
                    "title": item.label,
                    "value": item.key
                })
        
        # Show search prompt
        result = autocomplete(
            "Search menu items:",
            choices=[c["title"] for c in choices],
            style=self.style
        ).ask()
        
        # Find and return matching item
        if result:
            for choice in choices:
                if choice["title"] == result:
                    return choice["value"]
        
        return None
    
    def _cycle_theme(self) -> None:
        """Cycle through available themes."""
        themes = ["default", "dark", "light"]
        current_idx = themes.index(self.theme)
        self.theme = themes[(current_idx + 1) % len(themes)]
        
        # Update console and style
        self.console = Console(theme=get_rich_theme(self.theme))
        self.style = get_custom_style(self.theme)
        
        # Show theme change
        self.console.print(f"Theme changed to: {self.theme}", style="success")
    
    def _show_navigation_history(self) -> None:
        """Display navigation history."""
        self.navigation.show_history()
    
    def _build_choices(self) -> List[Dict[str, Any]]:
        """Build questionary choices from menu items."""
        choices = []
        
        for item in self.items:
            if not item.visible:
                continue
                
            if item.is_separator:
                choices.append(questionary.Separator())
                continue
            
            choice = {
                "name": item.display_label,
                "value": item.key,
                "disabled": not item.enabled
            }
            
            if item.description and item.enabled:
                choice["name"] = f"{item.display_label} - {item.description}"
            elif not item.enabled:
                choice["name"] = f"{item.display_label} (disabled)"
            
            choices.append(choice)
        
        # Add navigation options
        if self.parent:
            choices.append(questionary.Separator())
            choices.append({
                "name": f"{get_icon('back')} Back",
                "value": "__back__"
            })
        
        choices.append({
            "name": f"{get_icon('exit')} Exit",
            "value": "__exit__"
        })
        
        return choices
    
    def _show_header(self) -> None:
        """Display menu header with title and breadcrumb."""
        self.console.clear()
        
        # Show breadcrumb if enabled
        if self.show_breadcrumb:
            # Update navigation manager
            self.navigation.navigate_to(self.title, self.title)
            self.navigation.show_breadcrumb()
            self.console.print()
        
        # Show title with animation
        title_panel = MenuDecorations.create_banner(
            self.title,
            subtitle=f"{len([i for i in self.items if i.visible and not i.is_separator])} options available",
            style="menu.title"
        )
        
        if self.enable_animations:
            self.animations.fade_in(self.console, str(title_panel), duration=0.3)
        else:
            self.console.print(title_panel)
        
        self.console.print()
    
    def _build_breadcrumb(self) -> str:
        """Build navigation breadcrumb."""
        parts = []
        current = self
        
        while current:
            parts.append(current.title)
            current = current.parent
        
        parts.reverse()
        return " > ".join(parts)
    
    def _show_help(self) -> None:
        """Display keyboard shortcuts help."""
        if not self.show_help:
            return
            
        help_table = Table(show_header=False, show_edge=False, padding=0)
        help_table.add_column("Key", style="cyan")
        help_table.add_column("Action")
        
        help_items = [
            ("↑/↓", "Navigate"),
            ("Enter", "Select"),
            ("q", "Exit"),
            ("/", "Search"),
            ("h", "Help"),
        ]
        
        for key, action in help_items:
            help_table.add_row(key, action)
        
        self.console.print(
            Panel(help_table, title="Keyboard Shortcuts", border_style="dim"),
            justify="center"
        )
        self.console.print()
    
    def show(self) -> Optional[str]:
        """Display menu and get user selection.
        
        Returns:
            Selected item key or None if exited
        """
        # Apply entrance animation
        if self.enable_animations and not hasattr(self, '_shown_once'):
            self.transitions.dissolve(duration=0.2)
            self._shown_once = True
        
        while True:
            # Show header and help
            self._show_header()
            if self.show_help:
                self._show_help()
            
            # Build and show menu
            choices = self._build_choices()
            
            # Check for keyboard navigation mode
            if self.enable_keyboard_nav and self._should_use_keyboard_nav():
                selection = self._keyboard_navigation(choices)
            else:
                try:
                    selection = questionary.select(
                        "Select an option:",
                        choices=choices,
                        style=self.style,
                        use_shortcuts=True,
                        use_arrow_keys=True,
                        instruction="(Use arrow keys or press 'k' for keyboard mode)"
                    ).ask()
                except KeyboardInterrupt:
                    if self.enable_animations:
                        self.transitions.wipe(direction="right", duration=0.2)
                    return None
            
            # Handle special selections
            if selection == "__exit__":
                if self.enable_animations:
                    self.transitions.wipe(direction="right", duration=0.2)
                return None
            elif selection == "__back__":
                if self.enable_animations:
                    self.transitions.wipe(direction="left", duration=0.2)
                return "__back__"
            elif selection:
                self._history.append(selection)
                if self.enable_animations:
                    self.animations.pulse(self.console, f"Selected: {selection}", cycles=1, duration=0.3)
                return selection
            
            # User cancelled
            return None
    
    def _should_use_keyboard_nav(self) -> bool:
        """Check if keyboard navigation should be used."""
        # Could check terminal capabilities or user preference
        return False  # Default to questionary for now
    
    def _keyboard_navigation(self, choices: List[Dict[str, Any]]) -> Optional[str]:
        """Handle keyboard-based navigation."""
        # Filter out separators and disabled items
        valid_items = []
        for choice in choices:
            if isinstance(choice, dict) and not choice.get("disabled", False):
                valid_items.append(choice)
        
        if not valid_items:
            return None
        
        current_index = 0
        
        with self.keyboard.raw_mode():
            while True:
                # Display menu with current selection
                self.console.clear()
                self._show_header()
                
                for i, choice in enumerate(valid_items):
                    if i == current_index:
                        self.console.print(f"▸ {choice['name']}", style="bold cyan")
                    else:
                        self.console.print(f"  {choice['name']}")
                
                # Show help at bottom
                self.console.print("\n[dim]↑/↓: Navigate | Enter: Select | q: Quit | /: Search[/dim]")
                
                # Read key
                key = self.keyboard.read_key()
                
                # Handle navigation
                if key == Key.UP.value:
                    current_index = (current_index - 1) % len(valid_items)
                elif key == Key.DOWN.value:
                    current_index = (current_index + 1) % len(valid_items)
                elif key == Key.ENTER.value:
                    return valid_items[current_index]["value"]
                elif key in ['q', Key.ESCAPE.value]:
                    return "__exit__"
                elif key == '/':
                    # Search mode
                    result = self._search_items()
                    if result:
                        return result
                elif key.isdigit() and 1 <= int(key) <= min(9, len(valid_items)):
                    # Quick select by number
                    return valid_items[int(key) - 1]["value"]
    
    def handle_selection(self, key: str) -> Any:
        """Handle menu selection.
        
        Args:
            key: Selected item key
            
        Returns:
            Handler result or submenu selection
        """
        item = self.get_item(key)
        if not item:
            return None
        
        # Handle submenu
        if item.submenu:
            return item.submenu.show()
        
        # Handle handler
        if item.handler:
            return item.handler()
        
        return None
    
    def run_interactive(self) -> None:
        """Run menu in interactive loop."""
        while True:
            selection = self.show()
            
            if selection is None:
                # User exited
                if questionary.confirm("Exit application?", style=self.style).ask():
                    break
                continue
            
            if selection == "__back__":
                # Go back to parent menu
                break
            
            # Handle selection
            result = self.handle_selection(selection)
            
            if result == "__back__":
                # Handler requested to go back
                continue
            
            # Show result if any
            if result is not None:
                self.console.print()
                if isinstance(result, str):
                    self.console.print(result)
                self.console.print()
                self.console.input("Press Enter to continue...")
    
    def get_history(self) -> List[str]:
        """Get selection history."""
        return self._history.copy()
    
    def clear_history(self) -> None:
        """Clear selection history."""
        self._history.clear()


class MenuBuilder:
    """Builder for creating complex menu structures."""
    
    def __init__(self, theme: str = "default"):
        """Initialize menu builder.
        
        Args:
            theme: Theme name for styling
        """
        self.theme = theme
        self._menus: Dict[str, InteractiveMenu] = {}
    
    def create_menu(
        self,
        name: str,
        title: str,
        parent: Optional[str] = None
    ) -> InteractiveMenu:
        """Create a new menu.
        
        Args:
            name: Unique menu identifier
            title: Menu title
            parent: Parent menu name
            
        Returns:
            Created menu instance
        """
        parent_menu = self._menus.get(parent) if parent else None
        menu = InteractiveMenu(
            title=title,
            parent=parent_menu,
            theme=self.theme
        )
        self._menus[name] = menu
        return menu
    
    def add_item(
        self,
        menu_name: str,
        key: str,
        label: str,
        handler: Optional[Callable[[], Any]] = None,
        description: Optional[str] = None,
        icon: Optional[str] = None,
        submenu_name: Optional[str] = None,
        enabled: bool = True
    ) -> None:
        """Add item to menu.
        
        Args:
            menu_name: Target menu name
            key: Item key
            label: Item label
            handler: Item handler function
            description: Item description
            icon: Item icon
            submenu_name: Submenu name to link
            enabled: Whether item is enabled
        """
        menu = self._menus.get(menu_name)
        if not menu:
            raise ValueError(f"Menu '{menu_name}' not found")
        
        submenu = self._menus.get(submenu_name) if submenu_name else None
        
        item = MenuItem(
            key=key,
            label=label,
            handler=handler,
            description=description,
            icon=icon,
            submenu=submenu,
            enabled=enabled
        )
        
        menu.add_item(item)
    
    def add_separator(self, menu_name: str) -> None:
        """Add separator to menu.
        
        Args:
            menu_name: Target menu name
        """
        menu = self._menus.get(menu_name)
        if menu:
            menu.add_separator()
    
    def get_menu(self, name: str) -> Optional[InteractiveMenu]:
        """Get menu by name.
        
        Args:
            name: Menu name
            
        Returns:
            Menu instance or None
        """
        return self._menus.get(name)
    
    def create_main_menu(self) -> InteractiveMenu:
        """Create standard main menu structure.
        
        Returns:
            Main menu instance
        """
        # Create main menu
        main = self.create_menu("main", "Vector DB Query System")
        
        # Add main menu items
        self.add_item(
            "main", "process", "Process Documents",
            description="Process and index documents",
            icon=get_icon("process")
        )
        self.add_item(
            "main", "query", "Query Database",
            description="Search indexed documents",
            icon=get_icon("query")
        )
        self.add_item(
            "main", "mcp", "MCP Server",
            description="Manage MCP server",
            icon=get_icon("mcp"),
            submenu_name="mcp"
        )
        self.add_separator("main")
        self.add_item(
            "main", "config", "Settings",
            description="Configure application",
            icon=get_icon("config"),
            submenu_name="settings"
        )
        self.add_item(
            "main", "status", "System Status",
            description="View system information",
            icon=get_icon("status")
        )
        self.add_item(
            "main", "help", "Help & Documentation",
            description="View help and tutorials",
            icon=get_icon("help")
        )
        
        # Create MCP submenu
        mcp = self.create_menu("mcp", "MCP Server Management", parent="main")
        self.add_item(
            "mcp", "start", "Start Server",
            description="Start MCP server"
        )
        self.add_item(
            "mcp", "stop", "Stop Server",
            description="Stop MCP server"
        )
        self.add_item(
            "mcp", "status", "Server Status",
            description="Check server status"
        )
        self.add_separator("mcp")
        self.add_item(
            "mcp", "auth", "Manage Auth",
            description="Manage authentication"
        )
        self.add_item(
            "mcp", "test", "Test Server",
            description="Run server tests"
        )
        
        # Create settings submenu
        settings = self.create_menu("settings", "Settings", parent="main")
        self.add_item(
            "settings", "general", "General Settings",
            description="Configure general options"
        )
        self.add_item(
            "settings", "vector", "Vector Database",
            description="Configure Qdrant settings"
        )
        self.add_item(
            "settings", "embeddings", "Embeddings",
            description="Configure embedding model"
        )
        self.add_item(
            "settings", "theme", "UI Theme",
            description="Change display theme"
        )
        
        return main
    
    def create_context_menu(
        self,
        context: str,
        items: List[Dict[str, Any]]
    ) -> InteractiveMenu:
        """Create context-specific menu.
        
        Args:
            context: Context identifier
            items: List of item configurations
            
        Returns:
            Context menu instance
        """
        menu = self.create_menu(f"context_{context}", f"{context} Options")
        
        for item in items:
            self.add_item(
                f"context_{context}",
                item["key"],
                item["label"],
                handler=item.get("handler"),
                description=item.get("description"),
                icon=item.get("icon"),
                enabled=item.get("enabled", True)
            )
        
        return menu