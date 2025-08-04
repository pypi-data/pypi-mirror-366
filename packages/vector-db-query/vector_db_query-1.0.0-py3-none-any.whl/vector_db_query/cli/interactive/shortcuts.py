"""Global keyboard shortcuts and hotkey management."""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import platform

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .keyboard import Key, KeyBinding


class ShortcutContext(Enum):
    """Contexts where shortcuts are active."""
    GLOBAL = "global"
    MENU = "menu"
    FILE_BROWSER = "file_browser"
    QUERY_BUILDER = "query_builder"
    RESULTS = "results"
    CONFIG_EDITOR = "config_editor"
    PROGRESS = "progress"
    TEXT_INPUT = "text_input"


@dataclass
class Shortcut:
    """Keyboard shortcut definition."""
    key: str
    description: str
    handler: Optional[Callable] = None
    context: ShortcutContext = ShortcutContext.GLOBAL
    enabled: bool = True
    category: str = "General"
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.key}: {self.description}"


class ShortcutManager:
    """Manage global keyboard shortcuts."""
    
    def __init__(self):
        """Initialize shortcut manager."""
        self.shortcuts: Dict[ShortcutContext, List[Shortcut]] = {
            context: [] for context in ShortcutContext
        }
        self.console = Console()
        self._register_default_shortcuts()
    
    def _register_default_shortcuts(self) -> None:
        """Register default shortcuts."""
        # Global shortcuts
        self.register(Shortcut(
            key="?",
            description="Show help/shortcuts",
            context=ShortcutContext.GLOBAL,
            category="Help"
        ))
        self.register(Shortcut(
            key="Ctrl+C",
            description="Exit application",
            context=ShortcutContext.GLOBAL,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="Ctrl+L",
            description="Clear screen",
            context=ShortcutContext.GLOBAL,
            category="Display"
        ))
        self.register(Shortcut(
            key="Esc",
            description="Go back/Cancel",
            context=ShortcutContext.GLOBAL,
            category="Navigation"
        ))
        
        # Menu shortcuts
        self.register(Shortcut(
            key="↑/↓",
            description="Navigate up/down",
            context=ShortcutContext.MENU,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="Enter",
            description="Select item",
            context=ShortcutContext.MENU,
            category="Selection"
        ))
        self.register(Shortcut(
            key="1-9",
            description="Quick select (first 9 items)",
            context=ShortcutContext.MENU,
            category="Selection"
        ))
        self.register(Shortcut(
            key="/",
            description="Search menu items",
            context=ShortcutContext.MENU,
            category="Search"
        ))
        self.register(Shortcut(
            key="h",
            description="Show menu help",
            context=ShortcutContext.MENU,
            category="Help"
        ))
        self.register(Shortcut(
            key="b",
            description="Show breadcrumbs",
            context=ShortcutContext.MENU,
            category="Navigation"
        ))
        
        # File browser shortcuts
        self.register(Shortcut(
            key="Space",
            description="Toggle file selection",
            context=ShortcutContext.FILE_BROWSER,
            category="Selection"
        ))
        self.register(Shortcut(
            key="a",
            description="Select all files",
            context=ShortcutContext.FILE_BROWSER,
            category="Selection"
        ))
        self.register(Shortcut(
            key="d",
            description="Done selecting",
            context=ShortcutContext.FILE_BROWSER,
            category="Selection"
        ))
        self.register(Shortcut(
            key="p",
            description="Toggle preview pane",
            context=ShortcutContext.FILE_BROWSER,
            category="Display"
        ))
        self.register(Shortcut(
            key="h",
            description="Toggle hidden files",
            context=ShortcutContext.FILE_BROWSER,
            category="Display"
        ))
        self.register(Shortcut(
            key="u",
            description="Go up directory",
            context=ShortcutContext.FILE_BROWSER,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="r",
            description="Refresh file list",
            context=ShortcutContext.FILE_BROWSER,
            category="Display"
        ))
        self.register(Shortcut(
            key="s",
            description="Sort files",
            context=ShortcutContext.FILE_BROWSER,
            category="Display"
        ))
        
        # Query builder shortcuts
        self.register(Shortcut(
            key="Ctrl+H",
            description="Show query history",
            context=ShortcutContext.QUERY_BUILDER,
            category="History"
        ))
        self.register(Shortcut(
            key="Ctrl+T",
            description="Show query templates",
            context=ShortcutContext.QUERY_BUILDER,
            category="Templates"
        ))
        self.register(Shortcut(
            key="Ctrl+S",
            description="Save query to history",
            context=ShortcutContext.QUERY_BUILDER,
            category="History"
        ))
        self.register(Shortcut(
            key="Ctrl+L",
            description="Clear query",
            context=ShortcutContext.QUERY_BUILDER,
            category="Edit"
        ))
        self.register(Shortcut(
            key="Tab",
            description="Show suggestions",
            context=ShortcutContext.QUERY_BUILDER,
            category="Suggestions"
        ))
        
        # Results shortcuts
        self.register(Shortcut(
            key="n",
            description="Next page",
            context=ShortcutContext.RESULTS,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="p",
            description="Previous page",
            context=ShortcutContext.RESULTS,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="f",
            description="First page",
            context=ShortcutContext.RESULTS,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="l",
            description="Last page",
            context=ShortcutContext.RESULTS,
            category="Navigation"
        ))
        self.register(Shortcut(
            key="v",
            description="Change view format",
            context=ShortcutContext.RESULTS,
            category="Display"
        ))
        self.register(Shortcut(
            key="e",
            description="Export results",
            context=ShortcutContext.RESULTS,
            category="Export"
        ))
        self.register(Shortcut(
            key="s",
            description="Sort results",
            context=ShortcutContext.RESULTS,
            category="Display"
        ))
        self.register(Shortcut(
            key="f",
            description="Filter results",
            context=ShortcutContext.RESULTS,
            category="Filter"
        ))
        
        # Config editor shortcuts
        self.register(Shortcut(
            key="e",
            description="Edit value",
            context=ShortcutContext.CONFIG_EDITOR,
            category="Edit"
        ))
        self.register(Shortcut(
            key="r",
            description="Reset to default",
            context=ShortcutContext.CONFIG_EDITOR,
            category="Edit"
        ))
        self.register(Shortcut(
            key="s",
            description="Save configuration",
            context=ShortcutContext.CONFIG_EDITOR,
            category="File"
        ))
        self.register(Shortcut(
            key="Ctrl+Z",
            description="Undo change",
            context=ShortcutContext.CONFIG_EDITOR,
            category="Edit"
        ))
        self.register(Shortcut(
            key="/",
            description="Search settings",
            context=ShortcutContext.CONFIG_EDITOR,
            category="Search"
        ))
        
        # Progress shortcuts
        self.register(Shortcut(
            key="p",
            description="Pause/Resume",
            context=ShortcutContext.PROGRESS,
            category="Control"
        ))
        self.register(Shortcut(
            key="c",
            description="Cancel operation",
            context=ShortcutContext.PROGRESS,
            category="Control"
        ))
        self.register(Shortcut(
            key="d",
            description="Show details",
            context=ShortcutContext.PROGRESS,
            category="Display"
        ))
        
        # Text input shortcuts
        self.register(Shortcut(
            key="Ctrl+A",
            description="Select all",
            context=ShortcutContext.TEXT_INPUT,
            category="Edit"
        ))
        self.register(Shortcut(
            key="Ctrl+K",
            description="Clear to end of line",
            context=ShortcutContext.TEXT_INPUT,
            category="Edit"
        ))
        self.register(Shortcut(
            key="Ctrl+U",
            description="Clear to start of line",
            context=ShortcutContext.TEXT_INPUT,
            category="Edit"
        ))
    
    def register(self, shortcut: Shortcut) -> None:
        """Register a shortcut.
        
        Args:
            shortcut: Shortcut to register
        """
        self.shortcuts[shortcut.context].append(shortcut)
    
    def unregister(self, key: str, context: ShortcutContext) -> None:
        """Unregister a shortcut.
        
        Args:
            key: Key combination
            context: Context to remove from
        """
        self.shortcuts[context] = [
            s for s in self.shortcuts[context]
            if s.key != key
        ]
    
    def get_shortcuts(self, context: ShortcutContext) -> List[Shortcut]:
        """Get shortcuts for a context.
        
        Args:
            context: Context to get shortcuts for
            
        Returns:
            List of shortcuts
        """
        # Get context-specific shortcuts
        shortcuts = list(self.shortcuts[context])
        
        # Add global shortcuts
        if context != ShortcutContext.GLOBAL:
            shortcuts.extend(self.shortcuts[ShortcutContext.GLOBAL])
        
        return shortcuts
    
    def display_shortcuts(self, context: Optional[ShortcutContext] = None) -> None:
        """Display shortcuts in a formatted table.
        
        Args:
            context: Specific context to show, or None for all
        """
        self.console.clear()
        
        # Header
        self.console.print(Panel.fit(
            "[bold cyan]Keyboard Shortcuts[/bold cyan]",
            border_style="cyan"
        ))
        
        # Platform-specific note
        system = platform.system()
        if system == "Darwin":
            self.console.print("\n[dim]Note: Use ⌘ instead of Ctrl on macOS[/dim]\n")
        
        # Get contexts to display
        contexts = [context] if context else list(ShortcutContext)
        
        for ctx in contexts:
            shortcuts = self.shortcuts[ctx]
            if not shortcuts:
                continue
            
            # Group by category
            categories: Dict[str, List[Shortcut]] = {}
            for shortcut in shortcuts:
                if shortcut.category not in categories:
                    categories[shortcut.category] = []
                categories[shortcut.category].append(shortcut)
            
            # Context header
            self.console.print(f"\n[bold yellow]{ctx.value.replace('_', ' ').title()}:[/bold yellow]")
            
            # Create table
            table = Table(show_header=True, header_style="bold magenta", box=None)
            table.add_column("Key", style="cyan", width=20)
            table.add_column("Description", style="white")
            table.add_column("Category", style="dim")
            
            # Add shortcuts by category
            for category in sorted(categories.keys()):
                for shortcut in sorted(categories[category], key=lambda s: s.key):
                    table.add_row(
                        shortcut.key,
                        shortcut.description,
                        category
                    )
            
            self.console.print(table)
    
    def export_shortcuts(self, format: str = "markdown") -> str:
        """Export shortcuts in various formats.
        
        Args:
            format: Export format (markdown, html, json)
            
        Returns:
            Formatted shortcuts
        """
        if format == "markdown":
            return self._export_markdown()
        elif format == "html":
            return self._export_html()
        elif format == "json":
            return self._export_json()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_markdown(self) -> str:
        """Export shortcuts as Markdown."""
        lines = ["# Keyboard Shortcuts\n"]
        
        for context in ShortcutContext:
            shortcuts = self.shortcuts[context]
            if not shortcuts:
                continue
            
            lines.append(f"\n## {context.value.replace('_', ' ').title()}\n")
            
            # Group by category
            categories: Dict[str, List[Shortcut]] = {}
            for shortcut in shortcuts:
                if shortcut.category not in categories:
                    categories[shortcut.category] = []
                categories[shortcut.category].append(shortcut)
            
            for category in sorted(categories.keys()):
                lines.append(f"\n### {category}\n")
                for shortcut in sorted(categories[category], key=lambda s: s.key):
                    lines.append(f"- **{shortcut.key}**: {shortcut.description}")
        
        return "\n".join(lines)
    
    def _export_html(self) -> str:
        """Export shortcuts as HTML."""
        html = ["<html><head><title>Keyboard Shortcuts</title>"]
        html.append("<style>")
        html.append("body { font-family: Arial, sans-serif; }")
        html.append("table { border-collapse: collapse; margin: 20px 0; }")
        html.append("th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }")
        html.append("th { background-color: #f2f2f2; }")
        html.append("kbd { background: #eee; padding: 2px 4px; border-radius: 3px; }")
        html.append("</style></head><body>")
        html.append("<h1>Keyboard Shortcuts</h1>")
        
        for context in ShortcutContext:
            shortcuts = self.shortcuts[context]
            if not shortcuts:
                continue
            
            html.append(f"<h2>{context.value.replace('_', ' ').title()}</h2>")
            html.append("<table>")
            html.append("<tr><th>Key</th><th>Description</th><th>Category</th></tr>")
            
            for shortcut in sorted(shortcuts, key=lambda s: (s.category, s.key)):
                html.append(f"<tr>")
                html.append(f"<td><kbd>{shortcut.key}</kbd></td>")
                html.append(f"<td>{shortcut.description}</td>")
                html.append(f"<td>{shortcut.category}</td>")
                html.append(f"</tr>")
            
            html.append("</table>")
        
        html.append("</body></html>")
        return "\n".join(html)
    
    def _export_json(self) -> str:
        """Export shortcuts as JSON."""
        import json
        
        data = {}
        for context in ShortcutContext:
            shortcuts = self.shortcuts[context]
            if shortcuts:
                data[context.value] = [
                    {
                        "key": s.key,
                        "description": s.description,
                        "category": s.category,
                        "enabled": s.enabled
                    }
                    for s in shortcuts
                ]
        
        return json.dumps(data, indent=2)


# Global shortcut manager instance
shortcut_manager = ShortcutManager()


def show_shortcuts(context: Optional[ShortcutContext] = None) -> None:
    """Show keyboard shortcuts.
    
    Args:
        context: Specific context to show
    """
    shortcut_manager.display_shortcuts(context)


def get_context_shortcuts(context: ShortcutContext) -> List[Shortcut]:
    """Get shortcuts for a specific context.
    
    Args:
        context: Context to get shortcuts for
        
    Returns:
        List of shortcuts
    """
    return shortcut_manager.get_shortcuts(context)