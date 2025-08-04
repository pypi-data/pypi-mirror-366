"""Keyboard navigation and shortcut handling."""

from dataclasses import dataclass
from typing import Dict, Callable, Optional, List, Any
from enum import Enum
import sys
import tty
import termios
from contextlib import contextmanager

from rich.console import Console
from rich.table import Table


class Key(Enum):
    """Keyboard key codes."""
    
    # Navigation
    UP = "\x1b[A"
    DOWN = "\x1b[B"
    LEFT = "\x1b[D"
    RIGHT = "\x1b[C"
    HOME = "\x1b[H"
    END = "\x1b[F"
    PAGE_UP = "\x1b[5~"
    PAGE_DOWN = "\x1b[6~"
    
    # Control
    ENTER = "\r"
    SPACE = " "
    TAB = "\t"
    ESCAPE = "\x1b"
    BACKSPACE = "\x7f"
    DELETE = "\x1b[3~"
    
    # Control combinations
    CTRL_A = "\x01"
    CTRL_C = "\x03"
    CTRL_D = "\x04"
    CTRL_E = "\x05"
    CTRL_H = "\x08"
    CTRL_K = "\x0b"
    CTRL_L = "\x0c"
    CTRL_S = "\x13"
    CTRL_T = "\x14"
    CTRL_U = "\x15"
    CTRL_Z = "\x1a"
    
    # Function keys
    F1 = "\x1bOP"
    F2 = "\x1bOQ"
    F3 = "\x1bOR"
    F4 = "\x1bOS"
    F5 = "\x1b[15~"
    F6 = "\x1b[17~"
    F7 = "\x1b[18~"
    F8 = "\x1b[19~"
    F9 = "\x1b[20~"
    F10 = "\x1b[21~"
    F11 = "\x1b[23~"
    F12 = "\x1b[24~"
    
    # Special
    QUESTION = "?"
    SLASH = "/"
    
    # Letters (lowercase)
    A = "a"
    B = "b"
    C = "c"
    D = "d"
    E = "e"
    F = "f"
    G = "g"
    H = "h"
    I = "i"
    J = "j"
    K = "k"
    L = "l"
    M = "m"
    N = "n"
    O = "o"
    P = "p"
    Q = "q"
    R = "r"
    S = "s"
    T = "t"
    U = "u"
    V = "v"
    W = "w"
    X = "x"
    Y = "y"
    Z = "z"
    
    # Numbers
    NUM_0 = "0"
    NUM_1 = "1"
    NUM_2 = "2"
    NUM_3 = "3"
    NUM_4 = "4"
    NUM_5 = "5"
    NUM_6 = "6"
    NUM_7 = "7"
    NUM_8 = "8"
    NUM_9 = "9"


@dataclass
class KeyBinding:
    """Key binding configuration."""
    
    key: str
    action: str
    handler: Callable[[], Any]
    description: str
    category: str = "General"
    enabled: bool = True
    global_binding: bool = False


class KeyboardHandler:
    """Handle keyboard input and navigation."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize keyboard handler.
        
        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.bindings: Dict[str, KeyBinding] = {}
        self.global_bindings: Dict[str, KeyBinding] = {}
        self.categories: Dict[str, List[str]] = {}
        self._original_settings = None
        
        # Register default bindings
        self._register_defaults()
    
    def _register_defaults(self) -> None:
        """Register default key bindings."""
        # Navigation
        self.register("up", Key.UP.value, "Navigate up", 
                     lambda: "navigate_up", "Navigation")
        self.register("down", Key.DOWN.value, "Navigate down",
                     lambda: "navigate_down", "Navigation")
        self.register("left", Key.LEFT.value, "Navigate left",
                     lambda: "navigate_left", "Navigation")
        self.register("right", Key.RIGHT.value, "Navigate right",
                     lambda: "navigate_right", "Navigation")
        
        # Actions
        self.register("select", Key.ENTER.value, "Select item",
                     lambda: "select", "Actions")
        self.register("back", Key.ESCAPE.value, "Go back",
                     lambda: "back", "Actions")
        self.register("quit", "q", "Quit application",
                     lambda: "quit", "Actions", global_binding=True)
        
        # Help
        self.register("help", "h", "Show help",
                     lambda: "help", "Help", global_binding=True)
        self.register("shortcuts", "?", "Show shortcuts",
                     lambda: "shortcuts", "Help", global_binding=True)
    
    def register(
        self,
        action: str,
        key: str,
        description: str,
        handler: Callable[[], Any],
        category: str = "General",
        global_binding: bool = False
    ) -> None:
        """Register a key binding.
        
        Args:
            action: Action name
            key: Key or key sequence
            description: Binding description
            handler: Handler function
            category: Binding category
            global_binding: Whether binding is global
        """
        binding = KeyBinding(
            key=key,
            action=action,
            handler=handler,
            description=description,
            category=category,
            global_binding=global_binding
        )
        
        if global_binding:
            self.global_bindings[key] = binding
        else:
            self.bindings[key] = binding
        
        # Track categories
        if category not in self.categories:
            self.categories[category] = []
        if action not in self.categories[category]:
            self.categories[category].append(action)
    
    def unregister(self, key: str) -> bool:
        """Unregister a key binding.
        
        Args:
            key: Key to unregister
            
        Returns:
            True if unregistered
        """
        if key in self.bindings:
            action = self.bindings[key].action
            category = self.bindings[key].category
            del self.bindings[key]
            
            # Clean up category
            if category in self.categories and action in self.categories[category]:
                self.categories[category].remove(action)
                if not self.categories[category]:
                    del self.categories[category]
            
            return True
        
        if key in self.global_bindings:
            del self.global_bindings[key]
            return True
        
        return False
    
    def get_binding(self, key: str) -> Optional[KeyBinding]:
        """Get binding for key.
        
        Args:
            key: Key to lookup
            
        Returns:
            Key binding or None
        """
        # Check local bindings first
        if key in self.bindings and self.bindings[key].enabled:
            return self.bindings[key]
        
        # Check global bindings
        if key in self.global_bindings and self.global_bindings[key].enabled:
            return self.global_bindings[key]
        
        return None
    
    @contextmanager
    def raw_mode(self):
        """Context manager for raw keyboard mode."""
        if sys.platform == 'win32':
            # Windows doesn't support termios
            yield
            return
            
        try:
            # Save current settings
            self._original_settings = termios.tcgetattr(sys.stdin)
            
            # Set raw mode
            tty.setraw(sys.stdin.fileno())
            
            yield
            
        finally:
            # Restore settings
            if self._original_settings:
                termios.tcsetattr(
                    sys.stdin.fileno(),
                    termios.TCSADRAIN,
                    self._original_settings
                )
    
    def read_key(self) -> str:
        """Read a single key press.
        
        Returns:
            Key pressed
        """
        if sys.platform == 'win32':
            import msvcrt
            key = msvcrt.getch()
            if key in [b'\x00', b'\xe0']:
                # Special key, read second byte
                key += msvcrt.getch()
            return key.decode('utf-8', errors='ignore')
        else:
            # Unix-like systems
            key = sys.stdin.read(1)
            
            # Check for escape sequences
            if key == '\x1b':
                # Could be escape key or sequence
                key += sys.stdin.read(2)
                
                # Check for longer sequences
                if key.endswith('['):
                    # Read until we get a letter
                    while True:
                        next_char = sys.stdin.read(1)
                        key += next_char
                        if next_char.isalpha() or next_char == '~':
                            break
            
            return key
    
    def wait_for_key(
        self,
        prompt: Optional[str] = None,
        valid_keys: Optional[List[str]] = None
    ) -> str:
        """Wait for a key press.
        
        Args:
            prompt: Optional prompt to display
            valid_keys: List of valid keys (None for any)
            
        Returns:
            Key pressed
        """
        if prompt:
            self.console.print(prompt, end="")
        
        with self.raw_mode():
            while True:
                key = self.read_key()
                
                # Check if valid
                if valid_keys is None or key in valid_keys:
                    if prompt:
                        self.console.print()  # New line after prompt
                    return key
    
    def handle_key(self, key: str) -> Any:
        """Handle a key press.
        
        Args:
            key: Key pressed
            
        Returns:
            Handler result or None
        """
        binding = self.get_binding(key)
        if binding:
            return binding.handler()
        return None
    
    def show_help(self) -> None:
        """Display keyboard shortcuts help."""
        table = Table(
            title="Keyboard Shortcuts",
            show_header=True,
            header_style="bold magenta"
        )
        
        table.add_column("Key", style="cyan", width=12)
        table.add_column("Action", style="yellow")
        table.add_column("Description", style="white")
        
        # Group by category
        for category in sorted(self.categories.keys()):
            # Add category separator
            table.add_row("", f"[bold]{category}[/bold]", "")
            
            # Add bindings in category
            bindings_in_cat = []
            
            for key, binding in self.bindings.items():
                if binding.category == category:
                    bindings_in_cat.append((key, binding))
            
            for key, binding in self.global_bindings.items():
                if binding.category == category:
                    bindings_in_cat.append((key, binding))
            
            # Sort and display
            for key, binding in sorted(bindings_in_cat, key=lambda x: x[1].action):
                key_display = self._format_key(key)
                scope = " (global)" if binding.global_binding else ""
                table.add_row(
                    key_display,
                    binding.action + scope,
                    binding.description
                )
        
        self.console.print()
        self.console.print(table)
        self.console.print()
    
    def _format_key(self, key: str) -> str:
        """Format key for display.
        
        Args:
            key: Key string
            
        Returns:
            Formatted key
        """
        # Map special keys to readable names
        key_names = {
            Key.UP.value: "↑",
            Key.DOWN.value: "↓",
            Key.LEFT.value: "←",
            Key.RIGHT.value: "→",
            Key.ENTER.value: "Enter",
            Key.SPACE.value: "Space",
            Key.TAB.value: "Tab",
            Key.ESCAPE.value: "Esc",
            Key.BACKSPACE.value: "Backspace",
            Key.DELETE.value: "Delete",
            Key.HOME.value: "Home",
            Key.END.value: "End",
            Key.PAGE_UP.value: "PgUp",
            Key.PAGE_DOWN.value: "PgDn",
            # Control keys
            Key.CTRL_A.value: "Ctrl+A",
            Key.CTRL_C.value: "Ctrl+C",
            Key.CTRL_D.value: "Ctrl+D",
            Key.CTRL_E.value: "Ctrl+E",
            Key.CTRL_H.value: "Ctrl+H",
            Key.CTRL_K.value: "Ctrl+K",
            Key.CTRL_L.value: "Ctrl+L",
            Key.CTRL_S.value: "Ctrl+S",
            Key.CTRL_T.value: "Ctrl+T",
            Key.CTRL_U.value: "Ctrl+U",
            Key.CTRL_Z.value: "Ctrl+Z",
            # Special
            Key.QUESTION.value: "?",
            Key.SLASH.value: "/",
        }
        
        # Add function keys
        for i in range(1, 13):
            key_names[getattr(Key, f"F{i}").value] = f"F{i}"
        
        return key_names.get(key, key)
    
    def create_navigation_handler(
        self,
        items: List[Any],
        on_select: Callable[[Any], Any],
        on_cancel: Optional[Callable[[], Any]] = None
    ) -> Callable[[], Any]:
        """Create a navigation handler for lists.
        
        Args:
            items: List of items to navigate
            on_select: Callback when item selected
            on_cancel: Callback when cancelled
            
        Returns:
            Navigation handler function
        """
        current_index = [0]  # Use list for mutability in closure
        
        def handler():
            """Handle navigation."""
            with self.raw_mode():
                while True:
                    # Display items with current selection
                    self.console.clear()
                    for i, item in enumerate(items):
                        if i == current_index[0]:
                            self.console.print(f"> {item}", style="bold cyan")
                        else:
                            self.console.print(f"  {item}")
                    
                    # Read key
                    key = self.read_key()
                    
                    # Handle navigation
                    if key == Key.UP.value:
                        current_index[0] = (current_index[0] - 1) % len(items)
                    elif key == Key.DOWN.value:
                        current_index[0] = (current_index[0] + 1) % len(items)
                    elif key == Key.ENTER.value:
                        return on_select(items[current_index[0]])
                    elif key == Key.ESCAPE.value or key == 'q':
                        if on_cancel:
                            return on_cancel()
                        return None
        
        return handler