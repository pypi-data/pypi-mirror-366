"""Interactive result viewer components."""

import json
import csv
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from datetime import datetime
from io import StringIO

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.markdown import Markdown
from rich import box
import questionary
from questionary import Choice

from .base import BaseUIComponent, UIConfig
from .styles import get_icon, get_color
from .keyboard import KeyboardHandler, Key


@dataclass
class SearchResult:
    """Search result item."""
    
    id: str
    content: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    highlights: List[tuple[int, int]] = field(default_factory=list)
    
    @property
    def title(self) -> str:
        """Get result title."""
        return self.metadata.get("title", f"Document {self.id}")
    
    @property
    def source(self) -> str:
        """Get result source."""
        return self.metadata.get("source", "Unknown")
    
    @property
    def preview(self) -> str:
        """Get content preview."""
        max_length = 200
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."


class ResultViewer(BaseUIComponent):
    """Interactive result viewer with multiple formats."""
    
    def __init__(
        self,
        results: List[SearchResult],
        query: Optional[str] = None,
        page_size: int = 10,
        highlight_matches: bool = True,
        config: Optional[UIConfig] = None
    ):
        """Initialize result viewer.
        
        Args:
            results: Search results
            query: Original query
            page_size: Results per page
            highlight_matches: Highlight query matches
            config: UI configuration
        """
        super().__init__(config)
        self.results = results
        self.query = query
        self.page_size = page_size
        self.highlight_matches = highlight_matches
        self.current_page = 0
        self.current_format = "cards"
        self.keyboard = KeyboardHandler(self.console)
        
        # Set up shortcuts
        self._setup_shortcuts()
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        self.keyboard.register("next_page", "n", "Next page",
                             self._next_page, "Navigation")
        self.keyboard.register("prev_page", "p", "Previous page",
                             self._prev_page, "Navigation")
        self.keyboard.register("first_page", "f", "First page",
                             self._first_page, "Navigation")
        self.keyboard.register("last_page", "l", "Last page",
                             self._last_page, "Navigation")
        self.keyboard.register("change_format", "v", "Change view format",
                             self._change_format, "View")
    
    @property
    def total_pages(self) -> int:
        """Get total number of pages."""
        if not self.results:
            return 1
        return (len(self.results) + self.page_size - 1) // self.page_size
    
    def _get_page_results(self) -> List[SearchResult]:
        """Get results for current page."""
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.results[start:end]
    
    def _next_page(self) -> None:
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
    
    def _prev_page(self) -> None:
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
    
    def _first_page(self) -> None:
        """Go to first page."""
        self.current_page = 0
    
    def _last_page(self) -> None:
        """Go to last page."""
        self.current_page = self.total_pages - 1
    
    def _change_format(self) -> None:
        """Change display format."""
        formats = ["cards", "table", "json", "detailed"]
        current_idx = formats.index(self.current_format)
        self.current_format = formats[(current_idx + 1) % len(formats)]
    
    def display(self) -> Optional[SearchResult]:
        """Display results and get selection.
        
        Returns:
            Selected result or None
        """
        while True:
            self.clear()
            self._show_header()
            
            # Get page results
            page_results = self._get_page_results()
            
            if not page_results:
                self.print_warning("No results to display")
                self.wait_for_enter()
                return None
            
            # Display based on format
            if self.current_format == "cards":
                self._display_cards(page_results)
            elif self.current_format == "table":
                self._display_table(page_results)
            elif self.current_format == "json":
                self._display_json(page_results)
            elif self.current_format == "detailed":
                self._display_detailed(page_results)
            
            # Show footer
            self._show_footer()
            
            # Get user input
            choices = self._build_choices(page_results)
            
            selection = questionary.select(
                "Select result or action:",
                choices=choices,
                style=self.style,
                use_shortcuts=True
            ).ask()
            
            if selection == "exit":
                return None
            elif selection == "export":
                self._export_results()
            elif selection == "filter":
                self._filter_results()
            elif selection == "sort":
                self._sort_results()
            elif isinstance(selection, int):
                # Result selected
                return page_results[selection]
    
    def _show_header(self) -> None:
        """Show viewer header."""
        header_text = "[bold]Search Results[/bold]"
        if self.query:
            header_text += f"\nQuery: [cyan]{self.query}[/cyan]"
        
        header_text += f"\nFound: [green]{len(self.results)} results[/green]"
        
        self.show_panel(header_text, border_style="blue")
        self.console.print()
    
    def _show_footer(self) -> None:
        """Show pagination and help."""
        footer_text = f"Page {self.current_page + 1} of {self.total_pages}"
        footer_text += f" | Format: {self.current_format}"
        footer_text += " | [dim]n: next, p: prev, v: view, ?: help[/dim]"
        
        self.console.print(f"\n[dim]{footer_text}[/dim]")
    
    def _build_choices(self, results: List[SearchResult]) -> List[Choice]:
        """Build selection choices.
        
        Args:
            results: Page results
            
        Returns:
            Choice list
        """
        choices = []
        
        # Add result choices
        for i, result in enumerate(results):
            display = f"{i+1}. {result.title} (Score: {result.score:.2f})"
            choices.append(Choice(display, i))
        
        # Add actions
        choices.extend([
            questionary.Separator(),
            Choice("📤 Export Results", "export"),
            Choice("🔍 Filter Results", "filter"),
            Choice("📊 Sort Results", "sort"),
            Choice("🚪 Exit", "exit"),
        ])
        
        return choices
    
    def _display_cards(self, results: List[SearchResult]) -> None:
        """Display results as cards.
        
        Args:
            results: Results to display
        """
        cards = []
        
        for i, result in enumerate(results):
            # Build card content
            content = Text()
            
            # Title
            content.append(f"{i+1}. {result.title}\n", style="bold cyan")
            
            # Score and source
            content.append(f"Score: {result.score:.3f} | ", style="green")
            content.append(f"Source: {result.source}\n", style="yellow")
            
            # Preview
            preview = result.preview
            if self.highlight_matches and self.query:
                preview = self._highlight_text(preview, self.query)
            content.append(f"\n{preview}\n", style="white")
            
            # Metadata
            if result.metadata:
                meta_items = []
                for key, value in result.metadata.items():
                    if key not in ["title", "source", "content"]:
                        meta_items.append(f"{key}: {value}")
                if meta_items:
                    content.append("\n" + " • ".join(meta_items[:3]), style="dim")
            
            # Create card
            card = Panel(
                content,
                border_style="blue",
                padding=(1, 2)
            )
            cards.append(card)
        
        # Display cards in columns
        if len(cards) > 1:
            self.console.print(Columns(cards[:2], equal=True))
            for i in range(2, len(cards), 2):
                self.console.print()
                if i + 1 < len(cards):
                    self.console.print(Columns(cards[i:i+2], equal=True))
                else:
                    self.console.print(cards[i])
        else:
            self.console.print(cards[0])
    
    def _display_table(self, results: List[SearchResult]) -> None:
        """Display results as table.
        
        Args:
            results: Results to display
        """
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            box=box.ROUNDED
        )
        
        # Add columns
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="cyan")
        table.add_column("Score", style="green", justify="right", width=8)
        table.add_column("Source", style="yellow")
        table.add_column("Preview", style="white", max_width=50)
        
        # Add rows
        for i, result in enumerate(results):
            preview = result.preview
            if self.highlight_matches and self.query:
                preview = self._highlight_text(preview, self.query)
            
            table.add_row(
                str(i + 1),
                result.title,
                f"{result.score:.3f}",
                result.source,
                preview
            )
        
        self.console.print(table)
    
    def _display_json(self, results: List[SearchResult]) -> None:
        """Display results as JSON.
        
        Args:
            results: Results to display
        """
        # Convert to JSON-serializable format
        data = []
        for result in results:
            data.append({
                "id": result.id,
                "title": result.title,
                "score": result.score,
                "source": result.source,
                "content": result.content[:500],  # Limit content
                "metadata": result.metadata
            })
        
        # Format as JSON
        json_str = json.dumps(data, indent=2)
        
        # Syntax highlight
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        
        self.console.print(syntax)
    
    def _display_detailed(self, results: List[SearchResult]) -> None:
        """Display detailed view of results.
        
        Args:
            results: Results to display
        """
        for i, result in enumerate(results):
            # Header
            header = f"{i+1}. {result.title}"
            self.show_panel(
                header,
                border_style="cyan",
                padding=(0, 1)
            )
            
            # Details table
            details = Table(show_header=False, box=None)
            details.add_column("Property", style="cyan", width=15)
            details.add_column("Value")
            
            details.add_row("ID", result.id)
            details.add_row("Score", f"{result.score:.4f}")
            details.add_row("Source", result.source)
            
            # Add metadata
            for key, value in result.metadata.items():
                if key not in ["title", "source", "content"]:
                    details.add_row(key.title(), str(value))
            
            self.console.print(details)
            
            # Content
            self.console.print("\n[bold]Content:[/bold]")
            content = result.content
            if self.highlight_matches and self.query:
                content = self._highlight_text(content, self.query)
            
            # Wrap in panel for better readability
            content_panel = Panel(
                content,
                border_style="dim",
                padding=(1, 2)
            )
            self.console.print(content_panel)
            
            # Separator
            if i < len(results) - 1:
                self.console.print("\n" + "─" * 80 + "\n")
    
    def _highlight_text(self, text: str, query: str) -> str:
        """Highlight query terms in text.
        
        Args:
            text: Text to highlight
            query: Query terms
            
        Returns:
            Highlighted text
        """
        # Simple highlighting - wrap matches in color tags
        words = query.lower().split()
        result = text
        
        for word in words:
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            result = pattern.sub(lambda m: f"[bold yellow]{m.group()}[/bold yellow]", result)
        
        return result
    
    def _export_results(self) -> None:
        """Export results to file."""
        format_choice = questionary.select(
            "Select export format:",
            choices=["JSON", "CSV", "Markdown", "Cancel"],
            style=self.style
        ).ask()
        
        if format_choice == "Cancel":
            return
        
        # Get filename
        filename = self.prompt(
            "Enter filename (without extension):",
            default="search_results"
        )
        
        if not filename:
            return
        
        # Export based on format
        if format_choice == "JSON":
            self._export_json(f"{filename}.json")
        elif format_choice == "CSV":
            self._export_csv(f"{filename}.csv")
        elif format_choice == "Markdown":
            self._export_markdown(f"{filename}.md")
    
    def _export_json(self, filename: str) -> None:
        """Export results as JSON.
        
        Args:
            filename: Output filename
        """
        data = []
        for result in self.results:
            data.append({
                "id": result.id,
                "title": result.title,
                "score": result.score,
                "source": result.source,
                "content": result.content,
                "metadata": result.metadata
            })
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            self.print_success(f"Exported {len(self.results)} results to {filename}")
        except Exception as e:
            self.print_error(f"Export failed: {e}")
        
        self.wait_for_enter()
    
    def _export_csv(self, filename: str) -> None:
        """Export results as CSV.
        
        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w', newline='') as f:
                # Determine fields
                fields = ["id", "title", "score", "source", "content_preview"]
                
                # Add metadata fields
                metadata_fields = set()
                for result in self.results:
                    metadata_fields.update(result.metadata.keys())
                metadata_fields.discard("title")
                metadata_fields.discard("source")
                metadata_fields.discard("content")
                
                fields.extend(sorted(metadata_fields))
                
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for result in self.results:
                    row = {
                        "id": result.id,
                        "title": result.title,
                        "score": result.score,
                        "source": result.source,
                        "content_preview": result.preview
                    }
                    
                    # Add metadata
                    for field in metadata_fields:
                        row[field] = result.metadata.get(field, "")
                    
                    writer.writerow(row)
            
            self.print_success(f"Exported {len(self.results)} results to {filename}")
        except Exception as e:
            self.print_error(f"Export failed: {e}")
        
        self.wait_for_enter()
    
    def _export_markdown(self, filename: str) -> None:
        """Export results as Markdown.
        
        Args:
            filename: Output filename
        """
        try:
            with open(filename, 'w') as f:
                # Header
                f.write("# Search Results\n\n")
                if self.query:
                    f.write(f"**Query:** {self.query}\n\n")
                f.write(f"**Total Results:** {len(self.results)}\n\n")
                f.write("---\n\n")
                
                # Results
                for i, result in enumerate(self.results, 1):
                    f.write(f"## {i}. {result.title}\n\n")
                    f.write(f"- **Score:** {result.score:.4f}\n")
                    f.write(f"- **Source:** {result.source}\n")
                    
                    # Metadata
                    for key, value in result.metadata.items():
                        if key not in ["title", "source", "content"]:
                            f.write(f"- **{key.title()}:** {value}\n")
                    
                    f.write(f"\n### Content\n\n")
                    f.write(f"{result.content}\n\n")
                    f.write("---\n\n")
            
            self.print_success(f"Exported {len(self.results)} results to {filename}")
        except Exception as e:
            self.print_error(f"Export failed: {e}")
        
        self.wait_for_enter()
    
    def _filter_results(self) -> None:
        """Filter results interactively."""
        filter_type = questionary.select(
            "Filter by:",
            choices=["Score", "Source", "Metadata", "Cancel"],
            style=self.style
        ).ask()
        
        if filter_type == "Cancel":
            return
        
        if filter_type == "Score":
            min_score = self.prompt("Minimum score (0.0-1.0):", default="0.5")
            try:
                min_score = float(min_score)
                self.results = [r for r in self.results if r.score >= min_score]
                self.current_page = 0
                self.print_success(f"Filtered to {len(self.results)} results")
            except ValueError:
                self.print_error("Invalid score value")
        
        elif filter_type == "Source":
            sources = list(set(r.source for r in self.results))
            selected = self.checkbox(
                "Select sources:",
                choices=sources
            )
            if selected:
                self.results = [r for r in self.results if r.source in selected]
                self.current_page = 0
                self.print_success(f"Filtered to {len(self.results)} results")
        
        self.wait_for_enter()
    
    def _sort_results(self) -> None:
        """Sort results interactively."""
        sort_by = questionary.select(
            "Sort by:",
            choices=["Score (High to Low)", "Score (Low to High)", 
                    "Title (A-Z)", "Title (Z-A)", "Cancel"],
            style=self.style
        ).ask()
        
        if sort_by == "Cancel":
            return
        
        if sort_by == "Score (High to Low)":
            self.results.sort(key=lambda r: r.score, reverse=True)
        elif sort_by == "Score (Low to High)":
            self.results.sort(key=lambda r: r.score)
        elif sort_by == "Title (A-Z)":
            self.results.sort(key=lambda r: r.title.lower())
        elif sort_by == "Title (Z-A)":
            self.results.sort(key=lambda r: r.title.lower(), reverse=True)
        
        self.current_page = 0
        self.print_success("Results sorted")
        self.wait_for_enter()
    
    def render(self) -> Optional[SearchResult]:
        """Render component (calls display).
        
        Returns:
            Selected result or None
        """
        return self.display()


class ResultFormatter:
    """Format results for different outputs."""
    
    @staticmethod
    def format_terminal(
        results: List[SearchResult],
        max_width: int = 80
    ) -> str:
        """Format results for terminal display.
        
        Args:
            results: Search results
            max_width: Maximum line width
            
        Returns:
            Formatted string
        """
        output = []
        
        for i, result in enumerate(results, 1):
            # Header
            output.append(f"\n{i}. {result.title}")
            output.append("=" * min(len(result.title) + 3, max_width))
            
            # Details
            output.append(f"Score: {result.score:.4f}")
            output.append(f"Source: {result.source}")
            
            # Content preview
            output.append("\nContent:")
            content_lines = result.preview.split('\n')
            for line in content_lines[:5]:
                if len(line) > max_width:
                    line = line[:max_width-3] + "..."
                output.append(f"  {line}")
            
            output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def format_html(results: List[SearchResult]) -> str:
        """Format results as HTML.
        
        Args:
            results: Search results
            
        Returns:
            HTML string
        """
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Search Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .result { border: 1px solid #ddd; padding: 15px; margin: 10px 0; }
        .title { font-size: 18px; font-weight: bold; color: #333; }
        .score { color: #090; float: right; }
        .source { color: #666; font-size: 14px; }
        .content { margin-top: 10px; line-height: 1.6; }
        .highlight { background-color: #ff0; }
    </style>
</head>
<body>
    <h1>Search Results</h1>
"""
        
        for result in results:
            html += f"""
    <div class="result">
        <div class="title">{result.title} <span class="score">Score: {result.score:.3f}</span></div>
        <div class="source">Source: {result.source}</div>
        <div class="content">{result.preview}</div>
    </div>
"""
        
        html += """
</body>
</html>
"""
        return html