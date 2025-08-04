"""Interactive query builder with suggestions and history."""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable, Set
from pathlib import Path
from datetime import datetime
from difflib import get_close_matches

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.text import Text
import questionary
from questionary import Choice

from .base import BaseUIComponent, UIConfig
from .styles import get_icon, get_color
from .keyboard import KeyboardHandler, Key


@dataclass
class QueryTemplate:
    """Query template definition."""
    
    name: str
    description: str
    template: str
    variables: List[str] = field(default_factory=list)
    examples: List[Dict[str, str]] = field(default_factory=list)
    category: str = "General"
    
    def format(self, **kwargs) -> str:
        """Format template with variables.
        
        Args:
            **kwargs: Variable values
            
        Returns:
            Formatted query
        """
        return self.template.format(**kwargs)
    
    def get_missing_variables(self, provided: Dict[str, Any]) -> List[str]:
        """Get missing variables.
        
        Args:
            provided: Provided variables
            
        Returns:
            List of missing variable names
        """
        return [var for var in self.variables if var not in provided]


@dataclass
class QueryHistoryItem:
    """Query history entry."""
    
    query: str
    timestamp: datetime
    results_count: Optional[int] = None
    execution_time: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def display_time(self) -> str:
        """Get formatted timestamp."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @property
    def age(self) -> str:
        """Get human-readable age."""
        delta = datetime.now() - self.timestamp
        
        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            return f"{delta.seconds // 3600}h ago"
        elif delta.seconds > 60:
            return f"{delta.seconds // 60}m ago"
        else:
            return "just now"


class QueryHistory:
    """Manage query history."""
    
    def __init__(self, history_file: Optional[Path] = None, max_items: int = 100):
        """Initialize query history.
        
        Args:
            history_file: Path to history file
            max_items: Maximum history items
        """
        self.history_file = history_file or Path.home() / ".vector_query_history.json"
        self.max_items = max_items
        self.items: List[QueryHistoryItem] = []
        self._load()
    
    def _load(self) -> None:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    for item_data in data:
                        item = QueryHistoryItem(
                            query=item_data["query"],
                            timestamp=datetime.fromisoformat(item_data["timestamp"]),
                            results_count=item_data.get("results_count"),
                            execution_time=item_data.get("execution_time"),
                            tags=item_data.get("tags", [])
                        )
                        self.items.append(item)
            except Exception:
                # Ignore load errors
                pass
    
    def _save(self) -> None:
        """Save history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = []
            for item in self.items[-self.max_items:]:
                data.append({
                    "query": item.query,
                    "timestamp": item.timestamp.isoformat(),
                    "results_count": item.results_count,
                    "execution_time": item.execution_time,
                    "tags": item.tags
                })
            
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Ignore save errors
            pass
    
    def add(self, item: QueryHistoryItem) -> None:
        """Add item to history.
        
        Args:
            item: History item
        """
        # Remove duplicates
        self.items = [i for i in self.items if i.query != item.query]
        
        # Add new item
        self.items.append(item)
        
        # Limit size
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items:]
        
        # Save
        self._save()
    
    def search(self, pattern: str, limit: int = 10) -> List[QueryHistoryItem]:
        """Search history.
        
        Args:
            pattern: Search pattern
            limit: Maximum results
            
        Returns:
            Matching items
        """
        pattern_lower = pattern.lower()
        matches = []
        
        for item in reversed(self.items):
            if pattern_lower in item.query.lower():
                matches.append(item)
                if len(matches) >= limit:
                    break
        
        return matches
    
    def get_recent(self, count: int = 10) -> List[QueryHistoryItem]:
        """Get recent queries.
        
        Args:
            count: Number of items
            
        Returns:
            Recent items
        """
        return list(reversed(self.items[-count:]))
    
    def clear(self) -> None:
        """Clear history."""
        self.items.clear()
        self._save()


class QuerySuggester:
    """Provide query suggestions and completions."""
    
    def __init__(self):
        """Initialize suggester."""
        self.keywords = [
            # Common query terms
            "find", "search", "show", "get", "list",
            "documents", "files", "about", "containing",
            "related", "similar", "to", "from", "with",
            "and", "or", "not", "in", "by",
            
            # Operators
            "before", "after", "between", "near",
            "exactly", "approximately", "at least", "no more than",
            
            # Modifiers
            "latest", "recent", "oldest", "first", "last",
            "top", "best", "most relevant", "highest score",
        ]
        
        self.field_names = [
            "content", "title", "author", "date", "type",
            "category", "tags", "source", "path", "size"
        ]
        
        self.common_phrases = [
            "machine learning", "artificial intelligence",
            "data science", "neural networks", "deep learning",
            "natural language processing", "computer vision",
            "project management", "software development",
            "best practices", "documentation", "tutorial",
            "how to", "getting started", "troubleshooting"
        ]
    
    def suggest(self, partial: str, context: Optional[str] = None) -> List[str]:
        """Get suggestions for partial input.
        
        Args:
            partial: Partial query
            context: Query context
            
        Returns:
            List of suggestions
        """
        if not partial:
            return self.get_starters()
        
        partial_lower = partial.lower()
        suggestions = []
        
        # Get word completions
        words = partial.split()
        if words:
            last_word = words[-1].lower()
            prefix = " ".join(words[:-1]) + " " if len(words) > 1 else ""
            
            # Check keywords
            for keyword in self.keywords:
                if keyword.startswith(last_word) and keyword != last_word:
                    suggestions.append(prefix + keyword)
            
            # Check field names
            if ":" in last_word or (len(words) > 1 and words[-2] in ["by", "in"]):
                for field in self.field_names:
                    if field.startswith(last_word.replace(":", "")):
                        suggestions.append(prefix + field + ":")
            
            # Check common phrases
            for phrase in self.common_phrases:
                if phrase.startswith(partial_lower):
                    suggestions.append(phrase)
        
        # Add contextual suggestions
        if context:
            suggestions.extend(self.get_contextual_suggestions(partial, context))
        
        # Remove duplicates and limit
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)
        
        return unique_suggestions[:10]
    
    def get_starters(self) -> List[str]:
        """Get query starter suggestions.
        
        Returns:
            List of starter queries
        """
        return [
            "Find documents about ",
            "Search for files containing ",
            "Show all documents with ",
            "Get latest documents about ",
            "List files from ",
            "Find similar documents to ",
        ]
    
    def get_contextual_suggestions(self, partial: str, context: str) -> List[str]:
        """Get context-aware suggestions.
        
        Args:
            partial: Partial query
            context: Query context
            
        Returns:
            Contextual suggestions
        """
        suggestions = []
        
        # Based on previous words
        words = partial.split()
        if len(words) >= 2:
            prev_word = words[-2].lower()
            
            if prev_word in ["about", "containing", "with"]:
                # Suggest topics
                suggestions.extend([
                    partial + topic
                    for topic in ["python", "javascript", "api", "database", "security"]
                    if topic.startswith(words[-1].lower())
                ])
            elif prev_word in ["from", "by", "in"]:
                # Suggest filters
                suggestions.extend([
                    partial + "last week",
                    partial + "this month",
                    partial + "2024",
                    partial + "author:",
                ])
        
        return suggestions


class QueryBuilder(BaseUIComponent):
    """Interactive query builder with history and suggestions."""
    
    def __init__(
        self,
        history_file: Optional[Path] = None,
        templates: Optional[List[QueryTemplate]] = None,
        config: Optional[UIConfig] = None
    ):
        """Initialize query builder.
        
        Args:
            history_file: Path to history file
            templates: Query templates
            config: UI configuration
        """
        super().__init__(config)
        self.history = QueryHistory(history_file)
        self.suggester = QuerySuggester()
        self.templates = templates or self._get_default_templates()
        self.keyboard = KeyboardHandler(self.console)
        
        # Set up shortcuts
        self._setup_shortcuts()
    
    def _get_default_templates(self) -> List[QueryTemplate]:
        """Get default query templates.
        
        Returns:
            List of templates
        """
        return [
            QueryTemplate(
                name="simple_search",
                description="Basic keyword search",
                template="Find documents about {topic}",
                variables=["topic"],
                examples=[{"topic": "machine learning"}],
                category="Basic"
            ),
            QueryTemplate(
                name="filtered_search",
                description="Search with filters",
                template="Find {type} documents containing {keywords} from {time_period}",
                variables=["type", "keywords", "time_period"],
                examples=[{
                    "type": "PDF",
                    "keywords": "neural networks",
                    "time_period": "last month"
                }],
                category="Filtered"
            ),
            QueryTemplate(
                name="similarity_search",
                description="Find similar documents",
                template="Find documents similar to {reference} with score > {threshold}",
                variables=["reference", "threshold"],
                examples=[{
                    "reference": "document.pdf",
                    "threshold": "0.8"
                }],
                category="Advanced"
            ),
            QueryTemplate(
                name="complex_query",
                description="Complex boolean search",
                template='({term1} AND {term2}) OR ({term3} NOT {term4})',
                variables=["term1", "term2", "term3", "term4"],
                examples=[{
                    "term1": "python",
                    "term2": "tutorial",
                    "term3": "programming",
                    "term4": "java"
                }],
                category="Advanced"
            ),
        ]
    
    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        self.keyboard.register("history", "ctrl+h", "Show history",
                             self._show_history, "Query")
        self.keyboard.register("templates", "ctrl+t", "Show templates",
                             self._show_templates, "Query")
        self.keyboard.register("clear", "ctrl+l", "Clear query",
                             lambda: "", "Query")
    
    def build_query(self) -> Optional[str]:
        """Build query interactively.
        
        Returns:
            Query string or None
        """
        # Show query builder interface
        self.clear()
        self._show_header()
        
        # Offer options
        choices = [
            Choice("Natural Language", "natural"),
            Choice("Use Template", "template"),
            Choice("From History", "history"),
            Choice("Advanced Builder", "advanced"),
        ]
        
        mode = questionary.select(
            "How would you like to build your query?",
            choices=choices,
            style=self.style
        ).ask()
        
        if not mode:
            return None
        
        if mode == "natural":
            return self._build_natural_query()
        elif mode == "template":
            return self._build_from_template()
        elif mode == "history":
            return self._select_from_history()
        elif mode == "advanced":
            return self._build_advanced_query()
        
        return None
    
    def _show_header(self) -> None:
        """Show query builder header."""
        header = Panel(
            "[bold]Query Builder[/bold]\n"
            "Build powerful queries with suggestions and templates",
            border_style="blue"
        )
        self.console.print(header)
        self.console.print()
    
    def _build_natural_query(self) -> Optional[str]:
        """Build natural language query.
        
        Returns:
            Query string or None
        """
        self.print_info("Enter your query in natural language.")
        self.print("[dim]Suggestions will appear as you type.[/dim]\n")
        
        # Use autocomplete with suggestions
        query = questionary.autocomplete(
            "Query:",
            choices=lambda text: self.suggester.suggest(text),
            style=self.style,
            validate=lambda text: len(text.strip()) > 0
        ).ask()
        
        if query:
            # Add to history
            self.history.add(QueryHistoryItem(
                query=query,
                timestamp=datetime.now()
            ))
            
            # Show query preview
            self._preview_query(query)
            
            if self.confirm("Use this query?"):
                return query
        
        return None
    
    def _build_from_template(self) -> Optional[str]:
        """Build query from template.
        
        Returns:
            Query string or None
        """
        # Group templates by category
        categories = {}
        for template in self.templates:
            if template.category not in categories:
                categories[template.category] = []
            categories[template.category].append(template)
        
        # Select category
        cat_choices = [
            Choice(f"{cat} ({len(templates)} templates)", cat)
            for cat, templates in categories.items()
        ]
        
        category = questionary.select(
            "Select template category:",
            choices=cat_choices,
            style=self.style
        ).ask()
        
        if not category:
            return None
        
        # Select template
        template_choices = [
            Choice(f"{t.name} - {t.description}", t)
            for t in categories[category]
        ]
        
        template = questionary.select(
            "Select template:",
            choices=template_choices,
            style=self.style
        ).ask()
        
        if not template:
            return None
        
        # Show template info
        self._show_template_info(template)
        
        # Get variable values
        variables = {}
        for var in template.variables:
            value = self.prompt(f"{var}: ")
            if not value:
                return None
            variables[var] = value
        
        # Format query
        query = template.format(**variables)
        
        # Preview and confirm
        self._preview_query(query)
        
        if self.confirm("Use this query?"):
            # Add to history
            self.history.add(QueryHistoryItem(
                query=query,
                timestamp=datetime.now(),
                tags=[template.name]
            ))
            return query
        
        return None
    
    def _select_from_history(self) -> Optional[str]:
        """Select query from history.
        
        Returns:
            Query string or None
        """
        # Get recent queries
        recent = self.history.get_recent(20)
        
        if not recent:
            self.print_warning("No query history found.")
            return None
        
        # Build choices
        choices = []
        for item in recent:
            display = f"{item.query[:50]}..."  if len(item.query) > 50 else item.query
            meta = f"[{item.age}]"
            if item.results_count is not None:
                meta += f" [{item.results_count} results]"
            
            choices.append(
                Choice(f"{display} {meta}", item.query)
            )
        
        # Select from history
        query = questionary.select(
            "Select from history:",
            choices=choices,
            style=self.style
        ).ask()
        
        if query:
            # Show full query
            self._preview_query(query)
            
            if self.confirm("Use this query?"):
                # Re-add to move to top
                self.history.add(QueryHistoryItem(
                    query=query,
                    timestamp=datetime.now()
                ))
                return query
        
        return None
    
    def _build_advanced_query(self) -> Optional[str]:
        """Build advanced query with wizard.
        
        Returns:
            Query string or None
        """
        self.print_info("Advanced Query Builder")
        self.print("Build complex queries step by step.\n")
        
        # Initialize query parts
        terms = []
        filters = {}
        options = {}
        
        while True:
            # Show current query
            self._show_query_parts(terms, filters, options)
            
            # Options
            action = questionary.select(
                "What would you like to add?",
                choices=[
                    Choice("Add search term", "term"),
                    Choice("Add filter", "filter"),
                    Choice("Add option", "option"),
                    Choice("Preview query", "preview"),
                    Choice("Done", "done"),
                    Choice("Cancel", "cancel"),
                ],
                style=self.style
            ).ask()
            
            if action == "cancel":
                return None
            elif action == "done":
                query = self._build_query_string(terms, filters, options)
                if query:
                    self.history.add(QueryHistoryItem(
                        query=query,
                        timestamp=datetime.now(),
                        tags=["advanced"]
                    ))
                    return query
                else:
                    self.print_warning("Query is empty!")
            elif action == "term":
                term = self._add_search_term()
                if term:
                    terms.append(term)
            elif action == "filter":
                filter_key, filter_value = self._add_filter()
                if filter_key:
                    filters[filter_key] = filter_value
            elif action == "option":
                opt_key, opt_value = self._add_option()
                if opt_key:
                    options[opt_key] = opt_value
            elif action == "preview":
                query = self._build_query_string(terms, filters, options)
                self._preview_query(query)
                self.wait_for_enter()
    
    def _add_search_term(self) -> Optional[str]:
        """Add search term with operators.
        
        Returns:
            Term with operator or None
        """
        # Get term
        term = self.prompt("Enter search term: ")
        if not term:
            return None
        
        # Get operator
        operator = questionary.select(
            "How should this term be used?",
            choices=[
                Choice("Must contain (AND)", "AND"),
                Choice("Should contain (OR)", "OR"),
                Choice("Must NOT contain (NOT)", "NOT"),
                Choice("Exact phrase", "EXACT"),
            ],
            style=self.style
        ).ask()
        
        if operator == "EXACT":
            return f'"{term}"'
        elif operator == "NOT":
            return f"NOT {term}"
        else:
            return f"{operator} {term}" if operator != "AND" else term
    
    def _add_filter(self) -> tuple[Optional[str], Optional[str]]:
        """Add filter to query.
        
        Returns:
            Filter key and value tuple
        """
        # Common filters
        filter_type = questionary.select(
            "Select filter type:",
            choices=[
                Choice("File type", "type"),
                Choice("Date range", "date"),
                Choice("Size range", "size"),
                Choice("Path pattern", "path"),
                Choice("Custom field", "custom"),
            ],
            style=self.style
        ).ask()
        
        if not filter_type:
            return None, None
        
        if filter_type == "type":
            file_type = questionary.select(
                "Select file type:",
                choices=[".txt", ".pdf", ".doc", ".docx", ".md", ".py", ".json"],
                style=self.style
            ).ask()
            return "type", file_type
        
        elif filter_type == "date":
            date_option = questionary.select(
                "Select date filter:",
                choices=[
                    Choice("Last 24 hours", "1d"),
                    Choice("Last week", "7d"),
                    Choice("Last month", "30d"),
                    Choice("Custom range", "custom"),
                ],
                style=self.style
            ).ask()
            return "date", date_option
        
        elif filter_type == "size":
            size_option = questionary.select(
                "Select size filter:",
                choices=[
                    Choice("< 1 MB", "<1MB"),
                    Choice("1-10 MB", "1-10MB"),
                    Choice("> 10 MB", ">10MB"),
                    Choice("Custom", "custom"),
                ],
                style=self.style
            ).ask()
            return "size", size_option
        
        elif filter_type == "path":
            pattern = self.prompt("Enter path pattern (e.g., */docs/*): ")
            return "path", pattern
        
        elif filter_type == "custom":
            field = self.prompt("Field name: ")
            value = self.prompt("Value: ")
            return field, value
        
        return None, None
    
    def _add_option(self) -> tuple[Optional[str], Optional[str]]:
        """Add query option.
        
        Returns:
            Option key and value tuple
        """
        option = questionary.select(
            "Select option:",
            choices=[
                Choice("Result limit", "limit"),
                Choice("Minimum score", "score"),
                Choice("Sort order", "sort"),
                Choice("Group by", "group"),
            ],
            style=self.style
        ).ask()
        
        if not option:
            return None, None
        
        if option == "limit":
            limit = self.prompt("Maximum results (default: 10): ", default="10")
            return "limit", limit
        
        elif option == "score":
            score = self.prompt("Minimum score (0.0-1.0): ", default="0.5")
            return "min_score", score
        
        elif option == "sort":
            sort = questionary.select(
                "Sort by:",
                choices=["relevance", "date_desc", "date_asc", "size_desc", "size_asc"],
                style=self.style
            ).ask()
            return "sort", sort
        
        elif option == "group":
            group = questionary.select(
                "Group by:",
                choices=["type", "date", "directory", "none"],
                style=self.style
            ).ask()
            return "group_by", group
        
        return None, None
    
    def _show_query_parts(
        self,
        terms: List[str],
        filters: Dict[str, str],
        options: Dict[str, str]
    ) -> None:
        """Show current query parts.
        
        Args:
            terms: Search terms
            filters: Query filters
            options: Query options
        """
        parts = []
        
        if terms:
            parts.append(f"[cyan]Terms:[/cyan] {' '.join(terms)}")
        
        if filters:
            filter_str = ", ".join([f"{k}:{v}" for k, v in filters.items()])
            parts.append(f"[yellow]Filters:[/yellow] {filter_str}")
        
        if options:
            opt_str = ", ".join([f"{k}={v}" for k, v in options.items()])
            parts.append(f"[green]Options:[/green] {opt_str}")
        
        if parts:
            self.show_panel(
                "\n".join(parts),
                title="Current Query",
                border_style="blue"
            )
            self.console.print()
    
    def _build_query_string(
        self,
        terms: List[str],
        filters: Dict[str, str],
        options: Dict[str, str]
    ) -> str:
        """Build query string from parts.
        
        Args:
            terms: Search terms
            filters: Query filters
            options: Query options
            
        Returns:
            Query string
        """
        query_parts = []
        
        # Add terms
        if terms:
            # Clean up operators
            clean_terms = []
            for i, term in enumerate(terms):
                if i == 0 and term.startswith(("AND ", "OR ")):
                    # Remove operator from first term
                    clean_terms.append(term.split(" ", 1)[1])
                else:
                    clean_terms.append(term)
            query_parts.append(" ".join(clean_terms))
        
        # Add filters
        for key, value in filters.items():
            query_parts.append(f"{key}:{value}")
        
        # Add options (these might be handled separately)
        # For now, include them in the query
        for key, value in options.items():
            query_parts.append(f"--{key}={value}")
        
        return " ".join(query_parts)
    
    def _preview_query(self, query: str) -> None:
        """Preview query with syntax highlighting.
        
        Args:
            query: Query string
        """
        # Simple syntax highlighting
        highlighted = Text(query)
        
        # Highlight operators
        for op in ["AND", "OR", "NOT"]:
            highlighted.highlight_words([op], style="bold red")
        
        # Highlight quoted strings
        import re
        for match in re.finditer(r'"[^"]*"', query):
            highlighted.stylize("green", match.start(), match.end())
        
        # Highlight filters (word:value)
        for match in re.finditer(r'\b\w+:[^\s]+', query):
            highlighted.stylize("yellow", match.start(), match.end())
        
        # Highlight options (--key=value)
        for match in re.finditer(r'--\w+=[^\s]+', query):
            highlighted.stylize("blue", match.start(), match.end())
        
        self.show_panel(
            highlighted,
            title="Query Preview",
            border_style="green"
        )
        self.console.print()
    
    def _show_template_info(self, template: QueryTemplate) -> None:
        """Show template information.
        
        Args:
            template: Query template
        """
        info = f"[bold]{template.name}[/bold]\n"
        info += f"{template.description}\n\n"
        info += f"[cyan]Template:[/cyan] {template.template}\n"
        info += f"[yellow]Variables:[/yellow] {', '.join(template.variables)}\n"
        
        if template.examples:
            info += "\n[green]Example:[/green]\n"
            example = template.examples[0]
            formatted = template.format(**example)
            info += f"  {formatted}"
        
        self.show_panel(info, title="Template Info", border_style="blue")
        self.console.print()
    
    def _show_history(self) -> None:
        """Show query history."""
        recent = self.history.get_recent(10)
        
        if not recent:
            self.print_info("No query history.")
            return
        
        table = Table(title="Query History", show_header=True)
        table.add_column("Time", style="yellow", width=20)
        table.add_column("Query", style="cyan")
        table.add_column("Results", style="green", width=10)
        
        for item in recent:
            results = str(item.results_count) if item.results_count is not None else "-"
            table.add_row(item.age, item.query[:60] + "..." if len(item.query) > 60 else item.query, results)
        
        self.console.print(table)
    
    def _show_templates(self) -> None:
        """Show available templates."""
        table = Table(title="Query Templates", show_header=True)
        table.add_column("Name", style="cyan")
        table.add_column("Category", style="yellow", width=15)
        table.add_column("Description", style="white")
        
        for template in self.templates:
            table.add_row(template.name, template.category, template.description)
        
        self.console.print(table)
    
    def render(self) -> Optional[str]:
        """Render component (calls build_query)."""
        return self.build_query()


class QueryWizard(BaseUIComponent):
    """Guided query creation wizard."""
    
    def __init__(self, config: Optional[UIConfig] = None):
        """Initialize query wizard.
        
        Args:
            config: UI configuration
        """
        super().__init__(config)
    
    def guide_query_creation(self) -> Optional[str]:
        """Guide user through query creation.
        
        Returns:
            Query string or None
        """
        self.clear()
        self.print("[bold]Query Creation Wizard[/bold]")
        self.print("I'll help you create the perfect query.\n")
        
        # Step 1: Query intent
        intent = questionary.select(
            "What are you looking for?",
            choices=[
                Choice("Specific documents by content", "content"),
                Choice("Documents by metadata", "metadata"),
                Choice("Similar documents", "similarity"),
                Choice("Documents in date range", "date"),
                Choice("Statistical information", "stats"),
            ],
            style=self.style
        ).ask()
        
        if not intent:
            return None
        
        if intent == "content":
            return self._content_query_wizard()
        elif intent == "metadata":
            return self._metadata_query_wizard()
        elif intent == "similarity":
            return self._similarity_query_wizard()
        elif intent == "date":
            return self._date_query_wizard()
        elif intent == "stats":
            return self._stats_query_wizard()
        
        return None
    
    def _content_query_wizard(self) -> Optional[str]:
        """Wizard for content-based queries."""
        # Get search terms
        terms = self.prompt("Enter keywords or phrases (comma-separated): ")
        if not terms:
            return None
        
        # Get search mode
        mode = questionary.select(
            "How should these terms match?",
            choices=[
                Choice("All terms must match", "all"),
                Choice("Any term can match", "any"),
                Choice("Exact phrase", "exact"),
            ],
            style=self.style
        ).ask()
        
        # Build query
        term_list = [t.strip() for t in terms.split(",")]
        
        if mode == "all":
            query = " AND ".join(term_list)
        elif mode == "any":
            query = " OR ".join(term_list)
        else:
            query = f'"{terms}"'
        
        # Add filters?
        if self.confirm("Add filters?"):
            filters = self._get_content_filters()
            if filters:
                query += " " + filters
        
        return query
    
    def _metadata_query_wizard(self) -> Optional[str]:
        """Wizard for metadata-based queries."""
        filters = []
        
        # File type
        if self.confirm("Filter by file type?"):
            file_type = questionary.select(
                "Select file type:",
                choices=[".txt", ".pdf", ".doc", ".docx", ".md", "other"],
                style=self.style
            ).ask()
            if file_type == "other":
                file_type = self.prompt("Enter file extension: ")
            if file_type:
                filters.append(f"type:{file_type}")
        
        # Size
        if self.confirm("Filter by size?"):
            size = questionary.select(
                "Select size range:",
                choices=["<1MB", "1-10MB", ">10MB", "custom"],
                style=self.style
            ).ask()
            if size == "custom":
                size = self.prompt("Enter size filter: ")
            if size:
                filters.append(f"size:{size}")
        
        # Path
        if self.confirm("Filter by path?"):
            path = self.prompt("Enter path pattern: ")
            if path:
                filters.append(f"path:{path}")
        
        return " ".join(filters) if filters else None
    
    def _similarity_query_wizard(self) -> Optional[str]:
        """Wizard for similarity queries."""
        reference = self.prompt("Enter reference document path or content: ")
        if not reference:
            return None
        
        threshold = self.prompt("Minimum similarity score (0.0-1.0): ", default="0.7")
        
        query = f"similar_to:{reference} score>{threshold}"
        
        return query
    
    def _date_query_wizard(self) -> Optional[str]:
        """Wizard for date-based queries."""
        date_type = questionary.select(
            "Select date range:",
            choices=[
                Choice("Last N days", "days"),
                Choice("Specific date range", "range"),
                Choice("Before date", "before"),
                Choice("After date", "after"),
            ],
            style=self.style
        ).ask()
        
        if date_type == "days":
            days = self.prompt("Number of days: ", default="7")
            return f"date:last_{days}d"
        elif date_type == "range":
            start = self.prompt("Start date (YYYY-MM-DD): ")
            end = self.prompt("End date (YYYY-MM-DD): ")
            return f"date:{start}..{end}"
        elif date_type == "before":
            date = self.prompt("Before date (YYYY-MM-DD): ")
            return f"date:<{date}"
        elif date_type == "after":
            date = self.prompt("After date (YYYY-MM-DD): ")
            return f"date:>{date}"
        
        return None
    
    def _stats_query_wizard(self) -> Optional[str]:
        """Wizard for statistical queries."""
        stat_type = questionary.select(
            "What statistics do you need?",
            choices=[
                Choice("Document count by type", "count_by_type"),
                Choice("Size distribution", "size_dist"),
                Choice("Date distribution", "date_dist"),
                Choice("Top keywords", "keywords"),
            ],
            style=self.style
        ).ask()
        
        return f"stats:{stat_type}"
    
    def _get_content_filters(self) -> str:
        """Get additional content filters."""
        filters = []
        
        # Language
        if self.confirm("Filter by language?"):
            lang = questionary.select(
                "Select language:",
                choices=["en", "es", "fr", "de", "other"],
                style=self.style
            ).ask()
            if lang == "other":
                lang = self.prompt("Enter language code: ")
            if lang:
                filters.append(f"lang:{lang}")
        
        # Score threshold
        if self.confirm("Set minimum relevance score?"):
            score = self.prompt("Minimum score (0.0-1.0): ", default="0.5")
            filters.append(f"score>{score}")
        
        return " ".join(filters)
    
    def render(self) -> Optional[str]:
        """Render component."""
        return self.guide_query_creation()