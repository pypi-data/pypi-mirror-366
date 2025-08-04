"""Demo script for result viewer components."""

import random
from datetime import datetime, timedelta
from rich.console import Console

from .results import ResultViewer, SearchResult, ResultFormatter


def generate_demo_results(count: int = 25) -> list[SearchResult]:
    """Generate demo search results.
    
    Args:
        count: Number of results to generate
        
    Returns:
        List of search results
    """
    # Sample content
    topics = [
        "machine learning", "neural networks", "deep learning",
        "natural language processing", "computer vision",
        "reinforcement learning", "transformer models",
        "data preprocessing", "model optimization",
        "artificial intelligence ethics"
    ]
    
    sources = ["research_papers", "documentation", "tutorials", "blog_posts", "textbooks"]
    
    results = []
    
    for i in range(count):
        topic = random.choice(topics)
        source = random.choice(sources)
        
        # Generate content
        content = f"""This document discusses {topic} in detail. {topic.title()} is a fundamental concept in artificial intelligence that has revolutionized how we approach complex problems. 

The key aspects of {topic} include:
1. Understanding the basic principles
2. Implementing practical solutions
3. Evaluating performance metrics
4. Scaling to production systems

Recent advances in {topic} have shown promising results in various applications, from healthcare to autonomous vehicles. Researchers continue to push the boundaries of what's possible with {topic}.

This comprehensive guide covers everything from beginner concepts to advanced techniques in {topic}."""
        
        # Create result
        result = SearchResult(
            id=f"doc_{i+1:03d}",
            content=content,
            score=random.uniform(0.65, 0.99),
            metadata={
                "title": f"{topic.title()} - {'Advanced' if i % 3 == 0 else 'Introduction'}",
                "source": source,
                "author": f"Author {random.randint(1, 10)}",
                "date": (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d"),
                "pages": random.randint(5, 50),
                "category": topic.split()[0].title(),
                "tags": [topic, "AI", source]
            }
        )
        
        # Add some highlights
        if "machine learning" in content.lower():
            # Find positions of the term
            import re
            for match in re.finditer(r"machine learning", content, re.IGNORECASE):
                result.highlights.append((match.start(), match.end()))
        
        results.append(result)
    
    # Sort by score
    results.sort(key=lambda r: r.score, reverse=True)
    
    return results


def demo_result_viewer():
    """Demo result viewer with multiple formats."""
    console = Console()
    
    console.print("\n[bold]Result Viewer Demo[/bold]\n")
    console.print("Displaying search results with multiple view formats.\n")
    
    # Generate results
    results = generate_demo_results(25)
    query = "machine learning neural networks"
    
    # Create viewer
    viewer = ResultViewer(
        results=results,
        query=query,
        page_size=5,
        highlight_matches=True
    )
    
    # Display results
    selected = viewer.display()
    
    if selected:
        console.print(f"\n[green]Selected result:[/green] {selected.title}")
        console.print(f"ID: {selected.id}")
        console.print(f"Score: {selected.score:.4f}")
    else:
        console.print("\n[yellow]No result selected[/yellow]")


def demo_display_formats():
    """Demo different display formats."""
    console = Console()
    
    console.print("\n[bold]Display Formats Demo[/bold]\n")
    
    # Generate a few results
    results = generate_demo_results(3)
    
    # Create viewer for each format
    formats = ["cards", "table", "json", "detailed"]
    
    for format_name in formats:
        console.print(f"\n[cyan]Format: {format_name.upper()}[/cyan]")
        console.print("─" * 80)
        
        viewer = ResultViewer(results=results[:3], page_size=10)
        viewer.current_format = format_name
        
        # Display without interaction
        if format_name == "cards":
            viewer._display_cards(results[:2])
        elif format_name == "table":
            viewer._display_table(results)
        elif format_name == "json":
            viewer._display_json(results[:2])
        elif format_name == "detailed":
            viewer._display_detailed(results[:1])
        
        console.input("\nPress Enter to see next format...")


def demo_result_export():
    """Demo result export functionality."""
    console = Console()
    
    console.print("\n[bold]Result Export Demo[/bold]\n")
    
    # Generate results
    results = generate_demo_results(10)
    
    # Show results
    console.print(f"Generated {len(results)} results for export demo.\n")
    
    # Export to different formats
    viewer = ResultViewer(results=results)
    
    # JSON export
    console.print("[cyan]Exporting to JSON...[/cyan]")
    viewer._export_json("/tmp/demo_results.json")
    
    # CSV export
    console.print("[cyan]Exporting to CSV...[/cyan]")
    viewer._export_csv("/tmp/demo_results.csv")
    
    # Markdown export
    console.print("[cyan]Exporting to Markdown...[/cyan]")
    viewer._export_markdown("/tmp/demo_results.md")
    
    console.print("\n[green]Export complete![/green]")
    console.print("Files saved to /tmp/demo_results.*")


def demo_result_filtering():
    """Demo result filtering and sorting."""
    console = Console()
    
    console.print("\n[bold]Result Filtering Demo[/bold]\n")
    
    # Generate results with varied scores
    results = generate_demo_results(20)
    
    # Show original
    console.print(f"Original: {len(results)} results")
    console.print(f"Score range: {min(r.score for r in results):.3f} - {max(r.score for r in results):.3f}")
    
    # Filter by score
    high_score_results = [r for r in results if r.score >= 0.85]
    console.print(f"\nHigh score (≥0.85): {len(high_score_results)} results")
    
    # Filter by source
    sources = list(set(r.source for r in results))
    console.print(f"\nSources: {', '.join(sources)}")
    
    research_results = [r for r in results if r.source == "research_papers"]
    console.print(f"Research papers only: {len(research_results)} results")
    
    # Sort demo
    console.print("\n[cyan]Sorting options:[/cyan]")
    
    # By score
    sorted_by_score = sorted(results, key=lambda r: r.score, reverse=True)
    console.print(f"Top 3 by score:")
    for i, result in enumerate(sorted_by_score[:3], 1):
        console.print(f"  {i}. {result.title} (Score: {result.score:.3f})")
    
    # By date
    sorted_by_date = sorted(results, key=lambda r: r.metadata.get("date", ""), reverse=True)
    console.print(f"\nMost recent 3:")
    for i, result in enumerate(sorted_by_date[:3], 1):
        console.print(f"  {i}. {result.title} (Date: {result.metadata.get('date', 'N/A')})")


def demo_result_formatter():
    """Demo result formatter for different outputs."""
    console = Console()
    
    console.print("\n[bold]Result Formatter Demo[/bold]\n")
    
    # Generate a few results
    results = generate_demo_results(3)
    
    # Terminal format
    console.print("[cyan]Terminal Format:[/cyan]")
    console.print("─" * 80)
    terminal_output = ResultFormatter.format_terminal(results)
    console.print(terminal_output)
    
    # HTML format preview
    console.print("\n[cyan]HTML Format (preview):[/cyan]")
    console.print("─" * 80)
    html_output = ResultFormatter.format_html(results[:1])
    # Show just a snippet
    console.print(html_output[:500] + "...\n</body>\n</html>")


def demo_interactive_features():
    """Demo interactive features like highlighting."""
    console = Console()
    
    console.print("\n[bold]Interactive Features Demo[/bold]\n")
    
    # Create result with highlights
    content = """Machine learning is a subset of artificial intelligence that focuses on 
enabling systems to learn and improve from experience. Deep learning, a subfield 
of machine learning, uses neural networks with multiple layers to progressively 
extract higher-level features from raw input."""
    
    result = SearchResult(
        id="demo_001",
        content=content,
        score=0.95,
        metadata={
            "title": "Introduction to Machine Learning",
            "source": "tutorial"
        }
    )
    
    # Create viewer
    viewer = ResultViewer(
        results=[result],
        query="machine learning neural",
        highlight_matches=True
    )
    
    # Show highlighting
    console.print("[cyan]Query term highlighting:[/cyan]")
    highlighted = viewer._highlight_text(content, "machine learning neural")
    console.print(highlighted)
    
    # Show metadata formatting
    console.print("\n[cyan]Metadata display:[/cyan]")
    for key, value in result.metadata.items():
        console.print(f"  {key}: {value}")


def main():
    """Run result viewer demos."""
    console = Console()
    
    demos = [
        ("Interactive Result Viewer", demo_result_viewer),
        ("Display Formats", demo_display_formats),
        ("Result Export", demo_result_export),
        ("Filtering and Sorting", demo_result_filtering),
        ("Result Formatter", demo_result_formatter),
        ("Interactive Features", demo_interactive_features),
    ]
    
    console.print("\n[bold cyan]Result Viewer Demo Suite[/bold cyan]\n")
    console.print("Explore result viewing capabilities:\n")
    
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