"""Demo script for polish and optimization features."""

import time
import asyncio
from pathlib import Path
from rich.console import Console

from .optimization import (
    perf_monitor, cache_manager, lazy_loader,
    MemoryOptimizer, BatchProcessor, render_optimizer,
    optimize_startup, PERFORMANCE_TIPS
)
from .polish import (
    UsageAnalytics, SmartSuggestions, StatusBar,
    WelcomeScreen, ExitConfirmation, FeatureHighlight,
    get_polished_error
)


def demo_performance_monitoring():
    """Demo performance monitoring."""
    console = Console()
    
    console.clear()
    console.print("[bold]Performance Monitoring Demo[/bold]\n")
    
    # Enable monitoring
    perf_monitor.enabled = True
    perf_monitor.reset()
    
    # Simulate some operations
    @perf_monitor.measure("database_query")
    def simulate_query():
        time.sleep(0.1)  # Simulate 100ms query
        return "results"
    
    @perf_monitor.measure("file_processing")
    def simulate_processing():
        time.sleep(0.05)  # Simulate 50ms processing
        return "processed"
    
    @perf_monitor.measure("render_ui")
    def simulate_render():
        time.sleep(0.02)  # Simulate 20ms render
        return "rendered"
    
    console.print("Running performance tests...\n")
    
    # Run operations multiple times
    with console.status("[cyan]Executing operations..."):
        for i in range(5):
            simulate_query()
            simulate_processing()
            simulate_render()
            time.sleep(0.1)
    
    # Show report
    console.print("\n[green]Performance Report:[/green]\n")
    perf_monitor.display_report()
    
    console.input("\nPress Enter to continue...")


def demo_caching():
    """Demo caching functionality."""
    console = Console()
    
    console.clear()
    console.print("[bold]Caching Demo[/bold]\n")
    
    # Create cached function
    @cache_manager.cached("expensive_operation", ttl=5)
    def expensive_operation(n: int) -> int:
        console.print(f"[yellow]Computing result for {n}...[/yellow]")
        time.sleep(1)  # Simulate expensive operation
        return n * n
    
    # First calls (cache misses)
    console.print("First calls (will be slow):")
    for i in [1, 2, 3]:
        start = time.time()
        result = expensive_operation(i)
        duration = time.time() - start
        console.print(f"  expensive_operation({i}) = {result} (took {duration:.2f}s)")
    
    # Second calls (cache hits)
    console.print("\nSecond calls (from cache):")
    for i in [1, 2, 3]:
        start = time.time()
        result = expensive_operation(i)
        duration = time.time() - start
        console.print(f"  expensive_operation({i}) = {result} (took {duration:.2f}s)")
    
    # Show cache info
    console.print("\n[cyan]Cache Statistics:[/cyan]")
    for name, info in cache_manager.info().items():
        console.print(f"  {name}: {info['hits']} hits, {info['misses']} misses, "
                     f"{info['hit_rate']:.1%} hit rate")
    
    # Wait for TTL
    console.print("\n[dim]Waiting 5 seconds for cache to expire...[/dim]")
    time.sleep(5)
    
    console.print("\nAfter TTL expiration:")
    result = expensive_operation(1)
    console.print(f"  expensive_operation(1) = {result} (recomputed)")
    
    console.input("\nPress Enter to continue...")


def demo_batch_processing():
    """Demo batch processing."""
    console = Console()
    
    console.clear()
    console.print("[bold]Batch Processing Demo[/bold]\n")
    
    # Create sample data
    items = list(range(100))
    
    # Sync batch processing
    batch_processor = BatchProcessor(batch_size=20)
    
    def process_batch(batch):
        # Simulate processing
        return [x * 2 for x in batch]
    
    def progress_callback(current, total):
        console.print(f"[cyan]Processed {current}/{total} items[/cyan]", end="\r")
    
    console.print("Processing 100 items in batches of 20:\n")
    
    results = batch_processor.process_sync(
        items, process_batch, progress_callback
    )
    
    console.print(f"\n\n[green]Processed {len(results)} items![/green]")
    console.print(f"Sample results: {results[:5]}...")
    
    console.input("\nPress Enter to continue...")


async def demo_async_batch_processing():
    """Demo async batch processing."""
    console = Console()
    
    console.clear()
    console.print("[bold]Async Batch Processing Demo[/bold]\n")
    
    # Create sample data
    items = list(range(50))
    
    # Async batch processing
    batch_processor = BatchProcessor(batch_size=10)
    
    async def async_process_batch(batch):
        # Simulate async processing
        await asyncio.sleep(0.5)
        return [x * 3 for x in batch]
    
    console.print("Processing 50 items in 5 concurrent batches:\n")
    
    start = time.time()
    results = await batch_processor.process_async(
        items, async_process_batch, max_concurrent=5
    )
    duration = time.time() - start
    
    console.print(f"[green]Processed {len(results)} items in {duration:.2f}s![/green]")
    console.print(f"Sample results: {results[:5]}...")
    
    console.input("\nPress Enter to continue...")


def demo_memory_optimization():
    """Demo memory optimization."""
    console = Console()
    
    console.clear()
    console.print("[bold]Memory Optimization Demo[/bold]\n")
    
    # Show current memory
    console.print("[cyan]Current Memory Usage:[/cyan]")
    memory_before = MemoryOptimizer.get_memory_usage()
    for key, value in memory_before.items():
        console.print(f"  {key}: {value:.2f} MB")
    
    # Create some objects
    console.print("\n[yellow]Creating 10,000 objects...[/yellow]")
    objects = []
    for i in range(10000):
        objects.append({"id": i, "data": "x" * 1000})
    
    # Check memory again
    console.print("\n[cyan]After creating objects:[/cyan]")
    memory_after_create = MemoryOptimizer.get_memory_usage()
    for key, value in memory_after_create.items():
        console.print(f"  {key}: {value:.2f} MB")
    
    # Clear and collect
    console.print("\n[yellow]Clearing objects and collecting garbage...[/yellow]")
    objects.clear()
    gc_stats = MemoryOptimizer.collect_garbage()
    
    console.print(f"\n[green]Garbage Collection Stats:[/green]")
    console.print(f"  Objects before: {gc_stats['objects_before']}")
    console.print(f"  Objects after: {gc_stats['objects_after']}")
    console.print(f"  Collected: {gc_stats['collected']}")
    
    # Final memory
    console.print("\n[cyan]Final Memory Usage:[/cyan]")
    memory_final = MemoryOptimizer.get_memory_usage()
    for key, value in memory_final.items():
        console.print(f"  {key}: {value:.2f} MB")
    
    console.input("\nPress Enter to continue...")


def demo_usage_analytics():
    """Demo usage analytics."""
    console = Console()
    
    console.clear()
    console.print("[bold]Usage Analytics Demo[/bold]\n")
    
    # Create analytics
    analytics = UsageAnalytics(Path("/tmp/demo_analytics.json"))
    
    # Track some actions
    console.print("Tracking user actions...\n")
    
    actions = [
        ("process_documents", {"count": 5}),
        ("query_database", {"query": "test query"}),
        ("process_documents", {"count": 3}),
        ("export_results", {"format": "csv"}),
        ("query_database", {"query": "another query"}),
    ]
    
    for action, details in actions:
        analytics.track_action(action, details)
        console.print(f"  Tracked: {action}")
        time.sleep(0.2)
    
    # Track an error
    analytics.track_error("Connection timeout", {"service": "vector_db"})
    
    # Save session
    analytics.save_session()
    
    # Show insights
    console.print("\n[cyan]Usage Insights:[/cyan]")
    insights = analytics.get_insights()
    
    console.print(f"  Total sessions: {insights.get('total_sessions', 0)}")
    console.print(f"  Total actions: {insights.get('total_actions', 0)}")
    console.print(f"  Error rate: {insights.get('error_rate', 0):.1%}")
    
    console.print("\n[cyan]Most Common Actions:[/cyan]")
    for action, count in insights.get('most_common_actions', []):
        console.print(f"  {action}: {count} times")
    
    console.input("\nPress Enter to continue...")


def demo_smart_suggestions():
    """Demo smart suggestions."""
    console = Console()
    
    console.clear()
    console.print("[bold]Smart Suggestions Demo[/bold]\n")
    
    # Create suggestions engine
    suggestions = SmartSuggestions()
    
    # Show suggestions for different contexts
    contexts = [
        ("first_time", "New User"),
        ("after_processing", "After Processing Documents"),
        ("after_query", "After Running Query"),
    ]
    
    for context, title in contexts:
        console.print(f"[cyan]{title}:[/cyan]")
        suggs = suggestions.get_suggestions(context)
        for i, sugg in enumerate(suggs, 1):
            console.print(f"  {i}. {sugg}")
        console.print()
    
    # Error suggestions
    console.print("[cyan]Error Suggestions:[/cyan]")
    errors = [
        "API key not found in configuration",
        "Connection refused to localhost:6333",
        "Permission denied: /protected/file.txt"
    ]
    
    for error in errors:
        sugg = suggestions.get_error_suggestion(error)
        if sugg:
            console.print(f"  Error: {error[:30]}...")
            console.print(f"  → {sugg}\n")
    
    console.input("Press Enter to continue...")


def demo_status_bar():
    """Demo status bar."""
    console = Console()
    
    console.clear()
    console.print("[bold]Status Bar Demo[/bold]\n")
    
    status_bar = StatusBar(console)
    
    # Simulate different states
    states = [
        {"Database": "Connected", "Files": "0", "Mode": "Interactive"},
        {"Database": "Connected", "Files": "5", "Mode": "Processing..."},
        {"Database": "Connected", "Files": "5", "Mode": "Ready", "Query": "Active"},
    ]
    
    console.print("Status bar updates:\n")
    
    for state in states:
        status_bar.update(**state)
        console.print(f"[dim]Status:[/dim] {status_bar.render()}")
        time.sleep(1)
    
    console.input("\nPress Enter to continue...")


def demo_welcome_screen():
    """Demo welcome screen."""
    console = Console()
    
    console.clear()
    
    # Create mock analytics
    analytics = UsageAnalytics(Path("/tmp/demo_welcome.json"))
    analytics.session_data = {
        "session_id": "previous",
        "actions": [
            {"action": "process_documents"},
            {"action": "process_documents"},
            {"action": "query_database"},
        ]
    }
    analytics.save_session()
    
    # Show welcome screen
    welcome = WelcomeScreen("Demo User")
    welcome.show(analytics)
    
    console.input("\nPress Enter to continue...")


def demo_polished_errors():
    """Demo polished error messages."""
    console = Console()
    
    console.clear()
    console.print("[bold]Polished Error Messages Demo[/bold]\n")
    
    # Show different error types
    error_types = [
        ("file_not_found", "/path/to/missing/file.txt"),
        ("api_key_missing", None),
        ("connection_failed", "localhost:6333"),
        ("permission_denied", "/root/protected.txt"),
    ]
    
    for error_type, details in error_types:
        error_panel = get_polished_error(error_type, details)
        console.print(error_panel)
        console.print()
    
    console.input("Press Enter to continue...")


def demo_feature_highlight():
    """Demo feature highlighting."""
    console = Console()
    
    console.clear()
    console.print("[bold]Feature Highlight Demo[/bold]\n")
    
    # Create mock analytics with some usage
    analytics = UsageAnalytics(Path("/tmp/demo_highlight.json"))
    
    # Simulate sessions without certain features
    for i in range(8):
        analytics.session_data = {
            "session_id": f"session_{i}",
            "actions": [
                {"action": "process_documents"},
                {"action": "query_database"},
            ]
        }
        analytics.save_session()
    
    # Show feature highlight
    highlight = FeatureHighlight(analytics)
    highlight.show_highlight()


def demo_performance_tips():
    """Show performance tips."""
    console = Console()
    
    console.clear()
    console.print(PERFORMANCE_TIPS)
    console.input("\nPress Enter to continue...")


def main():
    """Run polish and optimization demos."""
    console = Console()
    
    demos = [
        ("Performance Monitoring", demo_performance_monitoring),
        ("Caching System", demo_caching),
        ("Batch Processing", demo_batch_processing),
        ("Async Batch Processing", lambda: asyncio.run(demo_async_batch_processing())),
        ("Memory Optimization", demo_memory_optimization),
        ("Usage Analytics", demo_usage_analytics),
        ("Smart Suggestions", demo_smart_suggestions),
        ("Status Bar", demo_status_bar),
        ("Welcome Screen", demo_welcome_screen),
        ("Polished Errors", demo_polished_errors),
        ("Feature Highlights", demo_feature_highlight),
        ("Performance Tips", demo_performance_tips),
    ]
    
    while True:
        console.clear()
        console.print("[bold cyan]Polish & Optimization Demo Suite[/bold cyan]\n")
        
        for i, (name, _) in enumerate(demos, 1):
            console.print(f"{i}. {name}")
        
        console.print("\nPress number to run demo, 'q' to quit")
        
        choice = console.input("\nSelect demo: ")
        
        if choice == 'q':
            # Demo exit confirmation
            exit_confirm = ExitConfirmation()
            if exit_confirm.confirm():
                break
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            _, demo_func = demos[int(choice) - 1]
            demo_func()
        else:
            console.print("[red]Invalid choice![/red]")
            console.input("Press Enter to continue...")
    
    console.print("\n[dim]Goodbye![/dim]")


if __name__ == "__main__":
    main()