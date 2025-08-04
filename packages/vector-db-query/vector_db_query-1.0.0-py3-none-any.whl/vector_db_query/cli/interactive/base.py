"""Base classes and utilities for interactive UI components."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
import questionary

from .styles import get_rich_theme, get_custom_style, get_color, get_icon


@dataclass
class UIConfig:
    """UI component configuration."""
    
    theme: str = "default"
    show_help: bool = True
    show_borders: bool = True
    use_colors: bool = True
    page_size: int = 10
    confirm_destructive: bool = True
    auto_clear: bool = False
    use_emoji: bool = True


class BaseUIComponent(ABC):
    """Base class for all interactive UI components."""
    
    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize UI component.
        
        Args:
            config: UI configuration
        """
        self.config = config or UIConfig()
        self.console = Console(
            theme=get_rich_theme(self.config.theme),
            color_system="auto" if self.config.use_colors else None
        )
        self.style = get_custom_style(self.config.theme)
    
    @abstractmethod
    def render(self) -> Any:
        """Render the UI component."""
        pass
    
    def clear(self) -> None:
        """Clear console screen."""
        if self.config.auto_clear:
            self.console.clear()
    
    def print(self, *args, **kwargs) -> None:
        """Print to console with component settings."""
        self.console.print(*args, **kwargs)
    
    def print_info(self, message: str) -> None:
        """Print info message."""
        icon = get_icon("info") if self.config.use_emoji else "[INFO]"
        self.console.print(f"{icon} {message}", style=get_color("info"))
    
    def print_success(self, message: str) -> None:
        """Print success message."""
        icon = get_icon("success") if self.config.use_emoji else "[OK]"
        self.console.print(f"{icon} {message}", style=get_color("success"))
    
    def print_warning(self, message: str) -> None:
        """Print warning message."""
        icon = get_icon("warning") if self.config.use_emoji else "[WARN]"
        self.console.print(f"{icon} {message}", style=get_color("warning"))
    
    def print_error(self, message: str) -> None:
        """Print error message."""
        icon = get_icon("error") if self.config.use_emoji else "[ERROR]"
        self.console.print(f"{icon} {message}", style=get_color("error"))
    
    def prompt(
        self,
        message: str,
        default: Optional[str] = None,
        password: bool = False
    ) -> str:
        """Get text input from user.
        
        Args:
            message: Prompt message
            default: Default value
            password: Hide input for passwords
            
        Returns:
            User input
        """
        if password:
            return questionary.password(
                message,
                style=self.style
            ).ask()
        
        return questionary.text(
            message,
            default=default,
            style=self.style
        ).ask()
    
    def confirm(
        self,
        message: str,
        default: bool = False,
        destructive: bool = False
    ) -> bool:
        """Get confirmation from user.
        
        Args:
            message: Confirmation message
            default: Default value
            destructive: Whether action is destructive
            
        Returns:
            User confirmation
        """
        if destructive and self.config.confirm_destructive:
            message = f"{get_icon('warning')} {message}"
        
        return questionary.confirm(
            message,
            default=default,
            style=self.style
        ).ask()
    
    def select(
        self,
        message: str,
        choices: List[Union[str, Dict[str, Any]]],
        default: Optional[str] = None
    ) -> Optional[str]:
        """Get selection from user.
        
        Args:
            message: Selection message
            choices: List of choices
            default: Default selection
            
        Returns:
            Selected value or None
        """
        return questionary.select(
            message,
            choices=choices,
            default=default,
            style=self.style
        ).ask()
    
    def checkbox(
        self,
        message: str,
        choices: List[Union[str, Dict[str, Any]]],
        default: Optional[List[str]] = None
    ) -> List[str]:
        """Get multiple selections from user.
        
        Args:
            message: Selection message
            choices: List of choices
            default: Default selections
            
        Returns:
            List of selected values
        """
        return questionary.checkbox(
            message,
            choices=choices,
            default=default or [],
            style=self.style
        ).ask()
    
    def show_panel(
        self,
        content: Any,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        border_style: Optional[str] = None
    ) -> None:
        """Show content in a panel.
        
        Args:
            content: Panel content
            title: Panel title
            subtitle: Panel subtitle
            border_style: Border style
        """
        panel = Panel(
            content,
            title=title,
            subtitle=subtitle,
            border_style=border_style or "blue",
            expand=False
        )
        self.console.print(panel)
    
    def show_table(
        self,
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> None:
        """Show data in a table.
        
        Args:
            data: Table data
            columns: Column names (defaults to dict keys)
            title: Table title
        """
        if not data:
            self.print_info("No data to display")
            return
        
        # Get columns from first item if not specified
        if columns is None:
            columns = list(data[0].keys())
        
        # Create table
        table = Table(title=title, show_header=True)
        
        # Add columns
        for col in columns:
            table.add_column(col, style="cyan")
        
        # Add rows
        for item in data:
            row = [str(item.get(col, "")) for col in columns]
            table.add_row(*row)
        
        self.console.print(table)
    
    def wait_for_enter(self, message: str = "Press Enter to continue...") -> None:
        """Wait for user to press Enter."""
        self.console.input(f"\n{message}")


class ProgressTracker(BaseUIComponent):
    """Progress tracking component for long operations."""
    
    def __init__(
        self,
        description: str,
        total: Optional[int] = None,
        config: Optional[UIConfig] = None
    ):
        """Initialize progress tracker.
        
        Args:
            description: Progress description
            total: Total steps (None for indeterminate)
            config: UI configuration
        """
        super().__init__(config)
        self.description = description
        self.total = total
        self._progress: Optional[Progress] = None
        self._task_id: Optional[int] = None
    
    def __enter__(self):
        """Start progress tracking."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop progress tracking."""
        self.stop()
    
    def start(self) -> None:
        """Start progress display."""
        if self.total is None:
            # Indeterminate progress
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            )
        else:
            # Determinate progress
            self._progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=self.console
            )
        
        self._progress.start()
        self._task_id = self._progress.add_task(
            self.description,
            total=self.total
        )
    
    def update(
        self,
        advance: int = 1,
        description: Optional[str] = None
    ) -> None:
        """Update progress.
        
        Args:
            advance: Steps to advance
            description: New description
        """
        if self._progress and self._task_id is not None:
            if description:
                self._progress.update(
                    self._task_id,
                    description=description
                )
            self._progress.advance(self._task_id, advance)
    
    def stop(self) -> None:
        """Stop progress display."""
        if self._progress:
            self._progress.stop()
            self._progress = None
            self._task_id = None
    
    def render(self) -> None:
        """Render is handled by Progress context."""
        pass


class LoadingSpinner(BaseUIComponent):
    """Simple loading spinner for quick operations."""
    
    def __init__(
        self,
        message: str = "Loading...",
        config: Optional[UIConfig] = None
    ):
        """Initialize loading spinner.
        
        Args:
            message: Loading message
            config: UI configuration
        """
        super().__init__(config)
        self.message = message
        self._progress: Optional[Progress] = None
    
    def __enter__(self):
        """Start spinner."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop spinner."""
        self.stop()
    
    def start(self) -> None:
        """Start spinner."""
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn(self.message),
            console=self.console,
            transient=True
        )
        self._progress.start()
        self._progress.add_task("", total=None)
    
    def stop(self) -> None:
        """Stop spinner."""
        if self._progress:
            self._progress.stop()
            self._progress = None
    
    def render(self) -> None:
        """Render is handled by Progress."""
        pass


class ErrorDisplay(BaseUIComponent):
    """Error display component with recovery options."""
    
    def __init__(
        self,
        error: Exception,
        title: str = "Error Occurred",
        suggestions: Optional[List[str]] = None,
        config: Optional[UIConfig] = None
    ):
        """Initialize error display.
        
        Args:
            error: Exception to display
            title: Error title
            suggestions: Recovery suggestions
            config: UI configuration
        """
        super().__init__(config)
        self.error = error
        self.title = title
        self.suggestions = suggestions or []
    
    def render(self) -> Optional[str]:
        """Render error display and get user action.
        
        Returns:
            Selected recovery action or None
        """
        # Build error content
        error_type = type(self.error).__name__
        error_msg = str(self.error)
        
        content = f"[red]{error_type}[/red]: {error_msg}"
        
        # Add suggestions if any
        if self.suggestions:
            content += "\n\n[yellow]Suggestions:[/yellow]\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                content += f"{i}. {suggestion}\n"
        
        # Show error panel
        self.show_panel(
            content,
            title=f"{get_icon('error')} {self.title}",
            border_style="red"
        )
        
        # Offer recovery options
        choices = [
            {"name": "Retry", "value": "retry"},
            {"name": "Skip", "value": "skip"},
            {"name": "Abort", "value": "abort"},
            {"name": "View Details", "value": "details"},
        ]
        
        action = self.select(
            "How would you like to proceed?",
            choices=choices
        )
        
        if action == "details":
            # Show full error details
            import traceback
            details = traceback.format_exception(
                type(self.error),
                self.error,
                self.error.__traceback__
            )
            self.show_panel(
                "".join(details),
                title="Error Details",
                border_style="dim"
            )
            # Ask again
            return self.render()
        
        return action