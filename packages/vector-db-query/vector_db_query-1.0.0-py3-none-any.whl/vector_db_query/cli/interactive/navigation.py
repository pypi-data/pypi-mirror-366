"""Navigation components for interactive CLI."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich.panel import Panel


@dataclass
class NavigationItem:
    """Navigation item in breadcrumb or history."""
    
    name: str
    path: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[float] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class Breadcrumb:
    """Breadcrumb navigation component."""
    
    def __init__(
        self,
        separator: str = " > ",
        max_items: int = 5,
        style: str = "dim"
    ):
        """Initialize breadcrumb.
        
        Args:
            separator: Separator between items
            max_items: Maximum items to display
            style: Breadcrumb style
        """
        self.separator = separator
        self.max_items = max_items
        self.style = style
        self.items: List[NavigationItem] = []
    
    def push(self, item: NavigationItem) -> None:
        """Add item to breadcrumb.
        
        Args:
            item: Navigation item
        """
        # Check if we're navigating back
        for i, existing in enumerate(self.items):
            if existing.path == item.path:
                # Truncate to this point
                self.items = self.items[:i + 1]
                return
        
        # Add new item
        self.items.append(item)
        
        # Limit items
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items:]
    
    def pop(self) -> Optional[NavigationItem]:
        """Remove and return last item.
        
        Returns:
            Last navigation item or None
        """
        if self.items:
            return self.items.pop()
        return None
    
    def clear(self) -> None:
        """Clear breadcrumb."""
        self.items.clear()
    
    def get_path(self) -> str:
        """Get current path as string.
        
        Returns:
            Formatted breadcrumb path
        """
        if not self.items:
            return ""
        
        names = [item.name for item in self.items]
        
        # Truncate if too many items
        if len(names) > self.max_items:
            names = ["..."] + names[-self.max_items + 1:]
        
        return self.separator.join(names)
    
    def render(self, console: Console) -> None:
        """Render breadcrumb to console.
        
        Args:
            console: Rich console
        """
        path = self.get_path()
        if path:
            console.print(path, style=self.style)
    
    def get_items(self) -> List[NavigationItem]:
        """Get all navigation items.
        
        Returns:
            List of navigation items
        """
        return self.items.copy()
    
    def go_to(self, index: int) -> Optional[NavigationItem]:
        """Navigate to specific index.
        
        Args:
            index: Item index
            
        Returns:
            Navigation item at index
        """
        if 0 <= index < len(self.items):
            # Truncate to this point
            self.items = self.items[:index + 1]
            return self.items[-1]
        return None


class NavigationHistory:
    """Navigation history with back/forward support."""
    
    def __init__(self, max_size: int = 50):
        """Initialize navigation history.
        
        Args:
            max_size: Maximum history size
        """
        self.max_size = max_size
        self.history: List[NavigationItem] = []
        self.current_index: int = -1
    
    def push(self, item: NavigationItem) -> None:
        """Add item to history.
        
        Args:
            item: Navigation item
        """
        # Remove any forward history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
        
        # Add new item
        self.history.append(item)
        self.current_index = len(self.history) - 1
        
        # Limit size
        if len(self.history) > self.max_size:
            removed = len(self.history) - self.max_size
            self.history = self.history[removed:]
            self.current_index -= removed
    
    def back(self) -> Optional[NavigationItem]:
        """Go back in history.
        
        Returns:
            Previous item or None
        """
        if self.can_go_back():
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def forward(self) -> Optional[NavigationItem]:
        """Go forward in history.
        
        Returns:
            Next item or None
        """
        if self.can_go_forward():
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def can_go_back(self) -> bool:
        """Check if can go back."""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if can go forward."""
        return self.current_index < len(self.history) - 1
    
    def get_current(self) -> Optional[NavigationItem]:
        """Get current history item.
        
        Returns:
            Current item or None
        """
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
    
    def clear(self) -> None:
        """Clear history."""
        self.history.clear()
        self.current_index = -1
    
    def get_recent(self, count: int = 10) -> List[NavigationItem]:
        """Get recent history items.
        
        Args:
            count: Number of items
            
        Returns:
            Recent history items
        """
        return self.history[-count:]


class NavigationManager:
    """Manage navigation state and transitions."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize navigation manager.
        
        Args:
            console: Rich console
        """
        self.console = console or Console()
        self.breadcrumb = Breadcrumb()
        self.history = NavigationHistory()
        self.shortcuts: Dict[str, NavigationItem] = {}
        self._on_navigate: Optional[Callable[[NavigationItem], None]] = None
    
    def navigate_to(
        self,
        name: str,
        path: str,
        data: Optional[Dict[str, Any]] = None
    ) -> NavigationItem:
        """Navigate to a location.
        
        Args:
            name: Location name
            path: Location path
            data: Associated data
            
        Returns:
            Navigation item
        """
        item = NavigationItem(name=name, path=path, data=data)
        
        # Update breadcrumb and history
        self.breadcrumb.push(item)
        self.history.push(item)
        
        # Call navigation callback
        if self._on_navigate:
            self._on_navigate(item)
        
        return item
    
    def go_back(self) -> Optional[NavigationItem]:
        """Go back in navigation.
        
        Returns:
            Previous location or None
        """
        # Try history first
        item = self.history.back()
        if item:
            # Update breadcrumb
            self.breadcrumb.clear()
            for hist_item in self.history.history[:self.history.current_index + 1]:
                self.breadcrumb.push(hist_item)
            
            if self._on_navigate:
                self._on_navigate(item)
            
            return item
        
        # Fall back to breadcrumb
        self.breadcrumb.pop()  # Remove current
        item = self.breadcrumb.pop()  # Get previous
        if item:
            self.breadcrumb.push(item)  # Re-add it
            if self._on_navigate:
                self._on_navigate(item)
        
        return item
    
    def go_forward(self) -> Optional[NavigationItem]:
        """Go forward in navigation.
        
        Returns:
            Next location or None
        """
        item = self.history.forward()
        if item:
            # Update breadcrumb
            self.breadcrumb.push(item)
            
            if self._on_navigate:
                self._on_navigate(item)
        
        return item
    
    def go_home(self) -> Optional[NavigationItem]:
        """Go to home/root.
        
        Returns:
            Home location or None
        """
        if self.breadcrumb.items:
            home = self.breadcrumb.items[0]
            return self.navigate_to(home.name, home.path, home.data)
        return None
    
    def add_shortcut(self, key: str, item: NavigationItem) -> None:
        """Add navigation shortcut.
        
        Args:
            key: Shortcut key
            item: Navigation item
        """
        self.shortcuts[key] = item
    
    def go_to_shortcut(self, key: str) -> Optional[NavigationItem]:
        """Navigate to shortcut.
        
        Args:
            key: Shortcut key
            
        Returns:
            Navigation item or None
        """
        if key in self.shortcuts:
            item = self.shortcuts[key]
            return self.navigate_to(item.name, item.path, item.data)
        return None
    
    def set_navigation_callback(
        self,
        callback: Callable[[NavigationItem], None]
    ) -> None:
        """Set navigation callback.
        
        Args:
            callback: Function called on navigation
        """
        self._on_navigate = callback
    
    def show_breadcrumb(self) -> None:
        """Display breadcrumb."""
        self.breadcrumb.render(self.console)
    
    def show_history(self, count: int = 10) -> None:
        """Display navigation history.
        
        Args:
            count: Number of items to show
        """
        recent = self.history.get_recent(count)
        if not recent:
            self.console.print("No navigation history", style="dim")
            return
        
        text = Text("Recent Navigation:\n", style="bold")
        for i, item in enumerate(recent):
            is_current = i == len(recent) - 1
            style = "bold cyan" if is_current else "dim"
            prefix = "> " if is_current else "  "
            text.append(f"{prefix}{item.name}\n", style=style)
        
        panel = Panel(
            text,
            title="Navigation History",
            border_style="blue"
        )
        self.console.print(panel)
    
    def get_state(self) -> Dict[str, Any]:
        """Get navigation state.
        
        Returns:
            Navigation state dict
        """
        return {
            "breadcrumb": [
                {"name": item.name, "path": item.path}
                for item in self.breadcrumb.items
            ],
            "history_size": len(self.history.history),
            "current_index": self.history.current_index,
            "can_go_back": self.history.can_go_back(),
            "can_go_forward": self.history.can_go_forward(),
            "shortcuts": list(self.shortcuts.keys())
        }