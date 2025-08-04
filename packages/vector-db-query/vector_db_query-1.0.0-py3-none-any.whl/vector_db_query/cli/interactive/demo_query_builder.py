"""Demo script for query builder component."""

from pathlib import Path
from datetime import datetime
from rich.console import Console

from .query_builder import (
    QueryBuilder, QueryWizard, QueryTemplate,
    QueryHistoryItem, QueryHistory, QuerySuggester
)


def demo_query_builder():
    """Demo main query builder."""
    console = Console()
    
    console.print("\n[bold]Query Builder Demo[/bold]\n")
    console.print("Build queries with templates, history, and suggestions.\n")
    
    # Create query builder
    builder = QueryBuilder()
    
    # Build a query
    query = builder.build_query()
    
    if query:
        console.print(f"\n[green]Generated query:[/green]\n{query}")
        
        # Simulate adding to history with results
        builder.history.add(QueryHistoryItem(
            query=query,
            timestamp=datetime.now(),
            results_count=42,
            execution_time=0.234
        ))
    else:
        console.print("\n[yellow]No query generated[/yellow]")


def demo_query_wizard():
    """Demo query wizard."""
    console = Console()
    
    console.print("\n[bold]Query Wizard Demo[/bold]\n")
    console.print("Guided query creation for different use cases.\n")
    
    # Create wizard
    wizard = QueryWizard()
    
    # Run wizard
    query = wizard.guide_query_creation()
    
    if query:
        console.print(f"\n[green]Wizard generated:[/green]\n{query}")
    else:
        console.print("\n[yellow]Wizard cancelled[/yellow]")


def demo_query_history():
    """Demo query history management."""
    console = Console()
    
    console.print("\n[bold]Query History Demo[/bold]\n")
    
    # Create history
    history = QueryHistory()
    
    # Add some sample queries
    sample_queries = [
        "Find documents about machine learning",
        "python tutorial type:pdf",
        "neural networks AND deep learning",
        "date:last_7d size:<10MB",
        "similar_to:reference.txt score>0.8"
    ]
    
    for i, query in enumerate(sample_queries):
        history.add(QueryHistoryItem(
            query=query,
            timestamp=datetime.now(),
            results_count=10 + i * 5,
            execution_time=0.1 + i * 0.05
        ))
    
    # Show recent history
    console.print("[cyan]Recent queries:[/cyan]")
    for item in history.get_recent(5):
        console.print(f"  • {item.query} [{item.age}]")
    
    # Search history
    console.print("\n[cyan]Search for 'learning':[/cyan]")
    results = history.search("learning")
    for item in results:
        console.print(f"  • {item.query}")


def demo_query_suggestions():
    """Demo query suggestion system."""
    console = Console()
    
    console.print("\n[bold]Query Suggestions Demo[/bold]\n")
    
    # Create suggester
    suggester = QuerySuggester()
    
    # Test various inputs
    test_inputs = [
        "",
        "find",
        "find doc",
        "search for",
        "documents about py",
        "type:",
        "machine lea"
    ]
    
    for input_text in test_inputs:
        suggestions = suggester.suggest(input_text)
        console.print(f"\n[yellow]Input:[/yellow] '{input_text}'")
        console.print("[cyan]Suggestions:[/cyan]")
        if suggestions:
            for suggestion in suggestions[:5]:
                console.print(f"  • {suggestion}")
        else:
            console.print("  (no suggestions)")


def demo_query_templates():
    """Demo query templates."""
    console = Console()
    
    console.print("\n[bold]Query Templates Demo[/bold]\n")
    
    # Create custom templates
    templates = [
        QueryTemplate(
            name="research_papers",
            description="Find research papers on a topic",
            template='type:pdf "{topic}" (abstract OR introduction) author:{author}',
            variables=["topic", "author"],
            examples=[{"topic": "quantum computing", "author": "Smith"}],
            category="Academic"
        ),
        QueryTemplate(
            name="code_search",
            description="Search for code examples",
            template='type:{language} "{function_name}" (import OR def OR class)',
            variables=["language", "function_name"],
            examples=[{"language": ".py", "function_name": "neural_network"}],
            category="Programming"
        ),
        QueryTemplate(
            name="recent_docs",
            description="Find recent documents on topic",
            template='"{topic}" date:last_{days}d sort:date_desc limit:{limit}',
            variables=["topic", "days", "limit"],
            examples=[{"topic": "AI safety", "days": "30", "limit": "20"}],
            category="Time-based"
        )
    ]
    
    # Show templates
    console.print("[cyan]Available templates:[/cyan]\n")
    
    for template in templates:
        console.print(f"[bold]{template.name}[/bold] ({template.category})")
        console.print(f"  {template.description}")
        console.print(f"  Template: {template.template}")
        if template.examples:
            example = template.examples[0]
            formatted = template.format(**example)
            console.print(f"  Example: {formatted}")
        console.print()


def demo_advanced_query():
    """Demo advanced query building."""
    console = Console()
    
    console.print("\n[bold]Advanced Query Building Demo[/bold]\n")
    
    # Example of building complex query programmatically
    from .query_builder import QueryBuilder
    
    # Create builder
    builder = QueryBuilder()
    
    # Build query parts
    terms = ["machine learning", "neural networks"]
    filters = {
        "type": ".pdf",
        "date": "2024",
        "size": "<50MB"
    }
    options = {
        "limit": "100",
        "min_score": "0.7",
        "sort": "relevance"
    }
    
    # Show how to build query string
    query = builder._build_query_string(terms, filters, options)
    
    console.print("[cyan]Query components:[/cyan]")
    console.print(f"  Terms: {terms}")
    console.print(f"  Filters: {filters}")
    console.print(f"  Options: {options}")
    console.print(f"\n[green]Generated query:[/green]\n{query}")
    
    # Preview the query
    builder._preview_query(query)


def main():
    """Run query builder demos."""
    console = Console()
    
    demos = [
        ("Interactive Query Builder", demo_query_builder),
        ("Query Wizard", demo_query_wizard),
        ("Query History", demo_query_history),
        ("Query Suggestions", demo_query_suggestions),
        ("Query Templates", demo_query_templates),
        ("Advanced Query Building", demo_advanced_query),
    ]
    
    console.print("\n[bold cyan]Query Builder Demo Suite[/bold cyan]\n")
    console.print("Explore query building capabilities:\n")
    
    for i, (name, _) in enumerate(demos, 1):
        console.print(f"{i}. {name}")
    
    console.print("\nPress Ctrl+C to exit")
    
    while True:
        try:
            choice = console.input("\nSelect demo (1-6): ")
            if choice.isdigit() and 1 <= int(choice) <= len(demos):
                _, demo_func = demos[int(choice) - 1]
                demo_func()
                console.input("\nPress Enter to continue...")
            else:
                console.print("[red]Invalid choice![/red]")
        except KeyboardInterrupt:
            console.print("\n\n[dim]Goodbye![/dim]")
            break


if __name__ == "__main__":
    main()