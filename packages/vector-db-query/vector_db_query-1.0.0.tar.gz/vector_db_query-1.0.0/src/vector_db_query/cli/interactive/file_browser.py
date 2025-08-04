"""Interactive file browser component with preview capabilities."""

import os
import mimetypes
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Set, Tuple
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.tree import Tree
import questionary

from .base import BaseUIComponent, UIConfig
from .styles import get_icon, get_color
from .keyboard import KeyboardHandler, Key


@dataclass
class FileInfo:
    """File information container."""
    
    path: Path
    name: str
    size: int
    modified: datetime
    is_dir: bool
    is_hidden: bool
    extension: str
    mime_type: Optional[str] = None
    permissions: Optional[str] = None
    
    @classmethod
    def from_path(cls, path: Path) -> 'FileInfo':
        """Create FileInfo from path.
        
        Args:
            path: File path
            
        Returns:
            FileInfo instance
        """
        stat = path.stat()
        name = path.name
        
        return cls(
            path=path,
            name=name,
            size=stat.st_size if not path.is_dir() else 0,
            modified=datetime.fromtimestamp(stat.st_mtime),
            is_dir=path.is_dir(),
            is_hidden=name.startswith('.'),
            extension=path.suffix.lower() if path.suffix else '',
            mime_type=mimetypes.guess_type(str(path))[0],
            permissions=oct(stat.st_mode)[-3:] if hasattr(stat, 'st_mode') else None
        )
    
    @property
    def size_formatted(self) -> str:
        """Get human-readable size."""
        if self.is_dir:
            return "<DIR>"
        
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(self.size)
        unit_idx = 0
        
        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1
        
        return f"{size:.1f} {units[unit_idx]}"
    
    @property
    def modified_formatted(self) -> str:
        """Get formatted modification time."""
        return self.modified.strftime("%Y-%m-%d %H:%M")
    
    @property
    def icon(self) -> str:
        """Get file icon based on type."""
        if self.is_dir:
            return get_icon("folder")
        
        # Map extensions to icons
        icon_map = {
            '.txt': '📄',
            '.md': '📝',
            '.pdf': '📕',
            '.doc': '📘',
            '.docx': '📘',
            '.py': '🐍',
            '.js': '📜',
            '.json': '📊',
            '.yaml': '⚙️',
            '.yml': '⚙️',
            '.csv': '📊',
            '.log': '📋',
            '.xml': '📄',
            '.html': '🌐',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.jpg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.mp4': '🎬',
            '.mp3': '🎵',
        }
        
        return icon_map.get(self.extension, get_icon("file"))


class FileBrowser(BaseUIComponent):
    """Interactive file browser with preview."""
    
    def __init__(
        self,
        start_path: Optional[Path] = None,
        filters: Optional[List[str]] = None,
        show_hidden: bool = False,
        allow_multiple: bool = True,
        preview_enabled: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize file browser.
        
        Args:
            start_path: Starting directory
            filters: File extension filters
            show_hidden: Show hidden files
            allow_multiple: Allow multiple selection
            preview_enabled: Enable file preview
            config: UI configuration
        """
        super().__init__(config)
        self.current_path = Path(start_path or Path.cwd()).resolve()
        self.filters = filters or []
        self.show_hidden = show_hidden
        self.allow_multiple = allow_multiple
        self.preview_enabled = preview_enabled
        self.selected_files: Set[Path] = set()
        self.navigation_history: List[Path] = [self.current_path]
        self.history_index = 0
        self.keyboard = KeyboardHandler(self.console)
        
        # Set up keyboard shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        self.keyboard.register("toggle_hidden", "h", "Toggle hidden files",
                             self._toggle_hidden, "View")
        self.keyboard.register("go_up", "u", "Go up directory",
                             self._go_up, "Navigation")
        self.keyboard.register("go_home", "~", "Go to home",
                             self._go_home, "Navigation")
        self.keyboard.register("refresh", "r", "Refresh",
                             self._refresh, "View")
        self.keyboard.register("toggle_preview", "p", "Toggle preview",
                             self._toggle_preview, "View")
    
    def _get_files(self) -> List[FileInfo]:
        """Get files in current directory.
        
        Returns:
            List of FileInfo objects
        """
        files = []
        
        try:
            for path in self.current_path.iterdir():
                try:
                    file_info = FileInfo.from_path(path)
                    
                    # Apply filters
                    if not self.show_hidden and file_info.is_hidden:
                        continue
                    
                    if self.filters and not file_info.is_dir:
                        if file_info.extension not in self.filters:
                            continue
                    
                    files.append(file_info)
                except (PermissionError, OSError):
                    # Skip files we can't access
                    continue
                    
        except (PermissionError, OSError) as e:
            self.print_error(f"Cannot access directory: {e}")
            return []
        
        # Sort: directories first, then by name
        files.sort(key=lambda f: (not f.is_dir, f.name.lower()))
        
        return files
    
    def _render_file_list(self, files: List[FileInfo], selected_index: int) -> Table:
        """Render file list as table.
        
        Args:
            files: List of files
            selected_index: Currently selected index
            
        Returns:
            Rich Table
        """
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            title=f"📁 {self.current_path}",
            title_style="bold",
            expand=True
        )
        
        # Add columns
        table.add_column("", width=3)  # Selection/Icon
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Size", style="green", justify="right", width=10)
        table.add_column("Modified", style="yellow", width=16)
        
        # Add parent directory option
        if self.current_path != self.current_path.root:
            icon = "↰" if selected_index == 0 else " "
            table.add_row(
                icon,
                "..",
                "<UP>",
                "",
                style="dim" if selected_index != 0 else "bold cyan"
            )
        
        # Add files
        start_index = 1 if self.current_path != self.current_path.root else 0
        
        for i, file_info in enumerate(files):
            actual_index = i + start_index
            
            # Selection indicator
            if actual_index == selected_index:
                selector = "▸"
                style = "bold cyan"
            else:
                selector = "✓" if file_info.path in self.selected_files else " "
                style = ""
            
            # File display
            name_display = f"{file_info.icon} {file_info.name}"
            if file_info.is_dir:
                name_display += "/"
            
            table.add_row(
                selector,
                name_display,
                file_info.size_formatted,
                file_info.modified_formatted,
                style=style
            )
        
        return table
    
    def _preview_file(self, file_info: FileInfo) -> Optional[Panel]:
        """Generate file preview.
        
        Args:
            file_info: File to preview
            
        Returns:
            Preview panel or None
        """
        if not self.preview_enabled or file_info.is_dir:
            return None
        
        try:
            # Determine preview type
            if file_info.extension in ['.txt', '.md', '.log', '.csv']:
                # Text preview
                with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)  # First 1000 chars
                    if len(content) == 1000:
                        content += "\n\n[dim]... (truncated)[/dim]"
                
                return Panel(
                    content,
                    title=f"Preview: {file_info.name}",
                    border_style="green"
                )
            
            elif file_info.extension in ['.py', '.js', '.json', '.yaml', '.yml', '.xml', '.html']:
                # Syntax highlighted preview
                with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000)
                
                # Determine lexer
                lexer_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.json': 'json',
                    '.yaml': 'yaml',
                    '.yml': 'yaml',
                    '.xml': 'xml',
                    '.html': 'html',
                }
                lexer = lexer_map.get(file_info.extension, 'text')
                
                syntax = Syntax(
                    content,
                    lexer,
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True
                )
                
                return Panel(
                    syntax,
                    title=f"Preview: {file_info.name}",
                    border_style="green"
                )
            
            else:
                # File info for binary/unsupported files
                info_text = f"File: {file_info.name}\n"
                info_text += f"Type: {file_info.mime_type or 'Unknown'}\n"
                info_text += f"Size: {file_info.size_formatted}\n"
                info_text += f"Modified: {file_info.modified_formatted}\n"
                if file_info.permissions:
                    info_text += f"Permissions: {file_info.permissions}"
                
                return Panel(
                    info_text,
                    title="File Information",
                    border_style="yellow"
                )
                
        except Exception as e:
            return Panel(
                f"[red]Cannot preview file:[/red]\n{str(e)}",
                title="Preview Error",
                border_style="red"
            )
    
    def browse(self) -> List[Path]:
        """Browse files and return selection.
        
        Returns:
            List of selected paths
        """
        selected_index = 0
        
        while True:
            # Get files
            files = self._get_files()
            
            # Clear and render
            self.clear()
            
            # Show path breadcrumb
            self._show_breadcrumb()
            
            # Create layout
            file_table = self._render_file_list(files, selected_index)
            
            if self.preview_enabled and files and selected_index > 0:
                # Show preview for selected file
                preview_index = selected_index - 1
                if preview_index < len(files):
                    preview = self._preview_file(files[preview_index])
                    if preview:
                        # Two column layout
                        self.console.print(Columns([file_table, preview], equal=True))
                    else:
                        self.console.print(file_table)
                else:
                    self.console.print(file_table)
            else:
                self.console.print(file_table)
            
            # Show help
            self._show_help()
            
            # Get user input
            key = self.keyboard.wait_for_key()
            
            # Handle navigation
            if key == Key.UP.value:
                selected_index = max(0, selected_index - 1)
            elif key == Key.DOWN.value:
                max_index = len(files) if self.current_path == self.current_path.root else len(files) + 1
                selected_index = min(max_index - 1, selected_index + 1)
            elif key == Key.ENTER.value:
                if selected_index == 0 and self.current_path != self.current_path.root:
                    # Go up
                    self._go_up()
                    selected_index = 0
                elif files:
                    file_index = selected_index - 1 if self.current_path != self.current_path.root else selected_index
                    if 0 <= file_index < len(files):
                        file_info = files[file_index]
                        if file_info.is_dir:
                            # Navigate into directory
                            self._navigate_to(file_info.path)
                            selected_index = 0
                        else:
                            # Select/deselect file
                            if self.allow_multiple:
                                if file_info.path in self.selected_files:
                                    self.selected_files.remove(file_info.path)
                                else:
                                    self.selected_files.add(file_info.path)
                            else:
                                return [file_info.path]
            elif key == Key.SPACE.value and self.allow_multiple:
                # Toggle selection
                if files and selected_index > 0:
                    file_index = selected_index - 1
                    if 0 <= file_index < len(files):
                        file_info = files[file_index]
                        if not file_info.is_dir:
                            if file_info.path in self.selected_files:
                                self.selected_files.remove(file_info.path)
                            else:
                                self.selected_files.add(file_info.path)
            elif key in ['q', Key.ESCAPE.value]:
                # Cancel
                return []
            elif key == 'd' and self.allow_multiple and self.selected_files:
                # Done selecting
                return list(self.selected_files)
            else:
                # Handle other shortcuts
                self.keyboard.handle_key(key)
    
    def _navigate_to(self, path: Path) -> None:
        """Navigate to directory.
        
        Args:
            path: Directory path
        """
        try:
            # Verify it's a directory
            if not path.is_dir():
                return
            
            # Update current path
            self.current_path = path.resolve()
            
            # Update history
            if self.history_index < len(self.navigation_history) - 1:
                # Truncate forward history
                self.navigation_history = self.navigation_history[:self.history_index + 1]
            
            self.navigation_history.append(self.current_path)
            self.history_index = len(self.navigation_history) - 1
            
        except (PermissionError, OSError) as e:
            self.print_error(f"Cannot access directory: {e}")
    
    def _go_up(self) -> None:
        """Go up one directory."""
        parent = self.current_path.parent
        if parent != self.current_path:
            self._navigate_to(parent)
    
    def _go_home(self) -> None:
        """Go to home directory."""
        self._navigate_to(Path.home())
    
    def _toggle_hidden(self) -> None:
        """Toggle hidden files visibility."""
        self.show_hidden = not self.show_hidden
    
    def _toggle_preview(self) -> None:
        """Toggle file preview."""
        self.preview_enabled = not self.preview_enabled
    
    def _refresh(self) -> None:
        """Refresh file list."""
        # Just re-render on next loop
        pass
    
    def _show_breadcrumb(self) -> None:
        """Show directory breadcrumb."""
        parts = self.current_path.parts
        if len(parts) > 5:
            # Truncate long paths
            breadcrumb = f"{parts[0]}/.../{'/'.join(parts[-3:])}"
        else:
            breadcrumb = str(self.current_path)
        
        self.console.print(f"[dim]Path:[/dim] {breadcrumb}\n")
    
    def _show_help(self) -> None:
        """Show keyboard help."""
        help_items = [
            ("↑/↓", "Navigate"),
            ("Enter", "Open/Select"),
            ("Space", "Toggle selection"),
            ("d", "Done"),
            ("h", "Hidden files"),
            ("p", "Preview"),
            ("u", "Up dir"),
            ("q", "Cancel"),
        ]
        
        help_text = " | ".join([f"[cyan]{key}[/cyan]: {action}" for key, action in help_items])
        self.console.print(f"\n[dim]{help_text}[/dim]")
    
    def render(self) -> List[Path]:
        """Render component (calls browse)."""
        return self.browse()


class FilePreview(BaseUIComponent):
    """File preview component."""
    
    def __init__(
        self,
        file_path: Path,
        max_lines: int = 50,
        syntax_highlight: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize file preview.
        
        Args:
            file_path: File to preview
            max_lines: Maximum lines to show
            syntax_highlight: Enable syntax highlighting
            config: UI configuration
        """
        super().__init__(config)
        self.file_path = file_path
        self.max_lines = max_lines
        self.syntax_highlight = syntax_highlight
    
    def render(self) -> None:
        """Render file preview."""
        if not self.file_path.exists():
            self.print_error(f"File not found: {self.file_path}")
            return
        
        if self.file_path.is_dir():
            self._render_directory()
        else:
            self._render_file()
    
    def _render_file(self) -> None:
        """Render file content."""
        file_info = FileInfo.from_path(self.file_path)
        
        # Show file info
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Property", style="cyan")
        info_table.add_column("Value")
        
        info_table.add_row("Name", file_info.name)
        info_table.add_row("Size", file_info.size_formatted)
        info_table.add_row("Type", file_info.mime_type or "Unknown")
        info_table.add_row("Modified", file_info.modified_formatted)
        
        self.show_panel(info_table, title="File Information", border_style="blue")
        self.console.print()
        
        # Show content
        try:
            if file_info.extension in ['.py', '.js', '.json', '.yaml', '.yml', '.xml', '.html'] and self.syntax_highlight:
                # Syntax highlighted
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Determine lexer
                lexer_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.json': 'json',
                    '.yaml': 'yaml',
                    '.yml': 'yaml',
                    '.xml': 'xml',
                    '.html': 'html',
                }
                lexer = lexer_map.get(file_info.extension, 'text')
                
                syntax = Syntax(
                    content,
                    lexer,
                    theme="monokai",
                    line_numbers=True,
                    word_wrap=True,
                    line_range=(1, self.max_lines)
                )
                
                self.console.print(syntax)
                
                # Show if truncated
                lines = content.count('\n') + 1
                if lines > self.max_lines:
                    self.console.print(f"\n[dim]... ({lines - self.max_lines} more lines)[/dim]")
                    
            else:
                # Plain text
                with open(self.file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f):
                        if i >= self.max_lines:
                            self.console.print(f"\n[dim]... (more lines)[/dim]")
                            break
                        self.console.print(line, end='')
                        
        except Exception as e:
            self.print_error(f"Cannot read file: {e}")
    
    def _render_directory(self) -> None:
        """Render directory contents."""
        try:
            # Build tree
            tree = Tree(f"[bold]{self.file_path.name}/[/bold]")
            
            def add_tree_contents(tree_node: Tree, path: Path, level: int = 0):
                """Recursively add directory contents to tree."""
                if level > 2:  # Limit depth
                    tree_node.add("[dim]...[/dim]")
                    return
                
                try:
                    items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
                    for item in items[:20]:  # Limit items
                        if item.name.startswith('.'):
                            continue
                        
                        if item.is_dir():
                            subtree = tree_node.add(f"[blue]{item.name}/[/blue]")
                            add_tree_contents(subtree, item, level + 1)
                        else:
                            file_info = FileInfo.from_path(item)
                            tree_node.add(f"{file_info.icon} {item.name}")
                            
                    if len(items) > 20:
                        tree_node.add("[dim]... more items[/dim]")
                        
                except PermissionError:
                    tree_node.add("[red]Permission denied[/red]")
            
            add_tree_contents(tree, self.file_path)
            
            self.show_panel(tree, title=f"Directory: {self.file_path}", border_style="blue")
            
        except Exception as e:
            self.print_error(f"Cannot read directory: {e}")


class FileSearch(BaseUIComponent):
    """File search component."""
    
    def __init__(
        self,
        root_path: Path,
        config: Optional[UIConfig] = None
    ):
        """Initialize file search.
        
        Args:
            root_path: Root path for search
            config: UI configuration
        """
        super().__init__(config)
        self.root_path = root_path
    
    def search(
        self,
        pattern: str,
        file_type: Optional[str] = None,
        max_results: int = 50
    ) -> List[Path]:
        """Search for files.
        
        Args:
            pattern: Search pattern
            file_type: File extension filter
            max_results: Maximum results
            
        Returns:
            List of matching paths
        """
        results = []
        pattern_lower = pattern.lower()
        
        for path in self.root_path.rglob("*"):
            if len(results) >= max_results:
                break
            
            try:
                # Skip hidden files
                if any(part.startswith('.') for part in path.parts):
                    continue
                
                # Check pattern match
                if pattern_lower not in path.name.lower():
                    continue
                
                # Check file type
                if file_type and path.suffix.lower() != file_type:
                    continue
                
                results.append(path)
                
            except (PermissionError, OSError):
                continue
        
        return results
    
    def render(self) -> List[Path]:
        """Interactive search interface."""
        pattern = self.prompt("Search pattern: ")
        if not pattern:
            return []
        
        # Get file type filter
        file_types = ["All files", ".txt", ".py", ".js", ".json", ".yaml", ".md", ".pdf", ".doc"]
        file_type = self.select("File type:", file_types)
        
        if file_type == "All files":
            file_type = None
        
        # Search with progress
        self.print_info(f"Searching for '{pattern}'...")
        
        results = self.search(pattern, file_type)
        
        if not results:
            self.print_warning("No files found")
            return []
        
        # Show results
        self.print_success(f"Found {len(results)} files")
        
        # Let user select from results
        choices = []
        for path in results:
            rel_path = path.relative_to(self.root_path)
            choices.append({
                "name": str(rel_path),
                "value": path
            })
        
        selected = self.checkbox(
            "Select files:",
            choices=choices
        )
        
        return selected