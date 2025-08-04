"""Global hotkey handler for interactive components."""

import asyncio
from typing import Dict, Callable, Optional, Any, List
from dataclasses import dataclass
from threading import Thread
import queue

from rich.console import Console

from .keyboard import KeyboardHandler, Key
from .shortcuts import ShortcutContext, shortcut_manager


@dataclass
class HotkeyBinding:
    """Hotkey binding definition."""
    key: Key
    handler: Callable[[], Any]
    context: ShortcutContext
    description: str
    enabled: bool = True
    async_handler: bool = False


class HotkeyHandler:
    """Global hotkey handler for the application."""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize hotkey handler.
        
        Args:
            console: Console for output
        """
        self.console = console or Console()
        self.keyboard = KeyboardHandler()
        self.bindings: Dict[str, List[HotkeyBinding]] = {}
        self.active_context = ShortcutContext.GLOBAL
        self._running = False
        self._handler_thread: Optional[Thread] = None
        self._key_queue: queue.Queue = queue.Queue()
        self._setup_default_bindings()
    
    def _setup_default_bindings(self) -> None:
        """Setup default hotkey bindings."""
        # Global help
        self.register(
            Key.QUESTION,
            self._show_help,
            ShortcutContext.GLOBAL,
            "Show help"
        )
        
        # Global clear screen
        self.register(
            Key.CTRL_L,
            self._clear_screen,
            ShortcutContext.GLOBAL,
            "Clear screen"
        )
    
    def register(
        self,
        key: Key,
        handler: Callable,
        context: ShortcutContext,
        description: str,
        async_handler: bool = False
    ) -> None:
        """Register a hotkey binding.
        
        Args:
            key: Key to bind
            handler: Handler function
            context: Context where binding is active
            description: Description of the binding
            async_handler: Whether handler is async
        """
        binding = HotkeyBinding(
            key=key,
            handler=handler,
            context=context,
            description=description,
            async_handler=async_handler
        )
        
        key_str = key.value
        if key_str not in self.bindings:
            self.bindings[key_str] = []
        self.bindings[key_str].append(binding)
    
    def unregister(self, key: Key, context: ShortcutContext) -> None:
        """Unregister a hotkey binding.
        
        Args:
            key: Key to unbind
            context: Context to remove from
        """
        key_str = key.value
        if key_str in self.bindings:
            self.bindings[key_str] = [
                b for b in self.bindings[key_str]
                if b.context != context
            ]
    
    def set_context(self, context: ShortcutContext) -> None:
        """Set the active context.
        
        Args:
            context: New active context
        """
        self.active_context = context
    
    def start(self) -> None:
        """Start listening for hotkeys."""
        if self._running:
            return
        
        self._running = True
        self._handler_thread = Thread(target=self._key_handler_loop, daemon=True)
        self._handler_thread.start()
    
    def stop(self) -> None:
        """Stop listening for hotkeys."""
        self._running = False
        if self._handler_thread:
            self._handler_thread.join(timeout=1)
    
    def _key_handler_loop(self) -> None:
        """Main key handler loop (runs in thread)."""
        while self._running:
            try:
                # Get key with timeout
                key = self._key_queue.get(timeout=0.1)
                if key:
                    self._handle_key(key)
            except queue.Empty:
                continue
            except Exception as e:
                self.console.print(f"[red]Hotkey error: {e}[/red]")
    
    def process_key(self, key: Key) -> bool:
        """Process a key press.
        
        Args:
            key: Key pressed
            
        Returns:
            True if key was handled
        """
        # Add to queue for processing
        self._key_queue.put(key)
        
        # Check if we have a binding
        key_str = key.value
        if key_str in self.bindings:
            bindings = self.bindings[key_str]
            
            # Find matching binding for current context
            for binding in bindings:
                if binding.enabled and (
                    binding.context == self.active_context or
                    binding.context == ShortcutContext.GLOBAL
                ):
                    return True
        
        return False
    
    def _handle_key(self, key: Key) -> None:
        """Handle a key press.
        
        Args:
            key: Key pressed
        """
        key_str = key.value
        if key_str not in self.bindings:
            return
        
        # Find matching binding
        for binding in self.bindings[key_str]:
            if not binding.enabled:
                continue
            
            # Check context
            if binding.context == self.active_context or binding.context == ShortcutContext.GLOBAL:
                try:
                    if binding.async_handler:
                        # Run async handler
                        asyncio.create_task(binding.handler())
                    else:
                        # Run sync handler
                        binding.handler()
                    break
                except Exception as e:
                    self.console.print(f"[red]Handler error: {e}[/red]")
    
    def _show_help(self) -> None:
        """Show context-sensitive help."""
        shortcut_manager.display_shortcuts(self.active_context)
        self.console.input("\nPress Enter to continue...")
    
    def _clear_screen(self) -> None:
        """Clear the screen."""
        self.console.clear()
    
    def get_active_bindings(self) -> List[HotkeyBinding]:
        """Get active bindings for current context.
        
        Returns:
            List of active bindings
        """
        active = []
        
        for key_bindings in self.bindings.values():
            for binding in key_bindings:
                if binding.enabled and (
                    binding.context == self.active_context or
                    binding.context == ShortcutContext.GLOBAL
                ):
                    active.append(binding)
        
        return active
    
    def show_active_hotkeys(self) -> None:
        """Show currently active hotkeys."""
        self.console.print(f"\n[bold]Active Hotkeys ({self.active_context.value}):[/bold]\n")
        
        bindings = self.get_active_bindings()
        if not bindings:
            self.console.print("[dim]No hotkeys active[/dim]")
            return
        
        # Group by context
        global_bindings = []
        context_bindings = []
        
        for binding in bindings:
            if binding.context == ShortcutContext.GLOBAL:
                global_bindings.append(binding)
            else:
                context_bindings.append(binding)
        
        # Show context-specific first
        if context_bindings:
            self.console.print(f"[cyan]{self.active_context.value.replace('_', ' ').title()}:[/cyan]")
            for binding in sorted(context_bindings, key=lambda b: b.key.value):
                self.console.print(f"  {binding.key.value:<15} {binding.description}")
        
        # Show global
        if global_bindings:
            self.console.print("\n[cyan]Global:[/cyan]")
            for binding in sorted(global_bindings, key=lambda b: b.key.value):
                self.console.print(f"  {binding.key.value:<15} {binding.description}")


class HotkeyMixin:
    """Mixin to add hotkey support to components."""
    
    def __init__(self, *args, **kwargs):
        """Initialize mixin."""
        super().__init__(*args, **kwargs)
        self.hotkey_handler: Optional[HotkeyHandler] = None
        self._hotkey_context: Optional[ShortcutContext] = None
    
    def setup_hotkeys(self, handler: HotkeyHandler, context: ShortcutContext) -> None:
        """Setup hotkeys for this component.
        
        Args:
            handler: Hotkey handler
            context: Context for this component
        """
        self.hotkey_handler = handler
        self._hotkey_context = context
        self._register_component_hotkeys()
    
    def _register_component_hotkeys(self) -> None:
        """Register component-specific hotkeys.
        
        Override in subclasses to register hotkeys.
        """
        pass
    
    def activate_hotkeys(self) -> None:
        """Activate hotkeys for this component."""
        if self.hotkey_handler and self._hotkey_context:
            self.hotkey_handler.set_context(self._hotkey_context)
    
    def deactivate_hotkeys(self) -> None:
        """Deactivate hotkeys for this component."""
        if self.hotkey_handler:
            self.hotkey_handler.set_context(ShortcutContext.GLOBAL)


# Global hotkey handler instance
_global_handler: Optional[HotkeyHandler] = None


def get_hotkey_handler() -> HotkeyHandler:
    """Get global hotkey handler instance.
    
    Returns:
        Global hotkey handler
    """
    global _global_handler
    if _global_handler is None:
        _global_handler = HotkeyHandler()
    return _global_handler


def start_global_hotkeys() -> None:
    """Start global hotkey handling."""
    handler = get_hotkey_handler()
    handler.start()


def stop_global_hotkeys() -> None:
    """Stop global hotkey handling."""
    handler = get_hotkey_handler()
    handler.stop()