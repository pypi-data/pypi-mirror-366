"""Performance testing and optimization commands."""

import click
import asyncio
import subprocess
import sys
from pathlib import Path

from ..utils import console, create_panel, format_success, format_error, format_warning
from ...utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
def performance():
    """Performance testing and optimization commands."""
    pass


@performance.command()
@click.option('--scenarios', '-s', multiple=True,
              type=click.Choice(['throughput', 'concurrency', 'memory', 'deduplication', 'nlp', 'stress']),
              help='Specific scenarios to run (default: all)')
@click.option('--output', '-o', default='benchmark_results', help='Output directory for results')
@click.option('--quick', is_flag=True, help='Run quick benchmarks only')
def benchmark(scenarios, output, quick):
    """Run performance benchmarks."""
    console.print(create_panel(
        "[bold blue]🚀 Performance Benchmark[/bold blue]\n\n"
        "Running comprehensive performance tests...",
        title="Benchmark"
    ))
    
    # Build command
    cmd = [sys.executable, 'scripts/performance_benchmark.py', '--output', output]
    
    if quick:
        cmd.append('--quick')
    
    if scenarios:
        cmd.extend(['--scenarios'] + list(scenarios))
    
    try:
        # Run benchmark script
        result = subprocess.run(cmd, cwd=Path.cwd())
        
        if result.returncode == 0:
            console.print(format_success("✅ Benchmark completed successfully!"))
            console.print(f"\nResults saved to: {output}/")
        else:
            console.print(format_error("❌ Benchmark failed"))
            sys.exit(1)
            
    except FileNotFoundError:
        console.print(format_error("Benchmark script not found. Make sure you're in the project root."))
        sys.exit(1)
    except Exception as e:
        console.print(format_error(f"Error running benchmark: {e}"))
        sys.exit(1)


@performance.command()
@click.option('--analyze', '-a', is_flag=True, help='Analyze current configuration')
@click.option('--optimize', '-o', is_flag=True, help='Generate and apply optimizations')
@click.option('--profile', '-p',
              type=click.Choice(['conservative', 'balanced', 'aggressive']),
              default='balanced',
              help='Performance profile to use')
@click.option('--dry-run', is_flag=True, help='Show changes without applying')
def optimize(analyze, optimize_flag, profile, dry_run):
    """Optimize performance configuration."""
    console.print(create_panel(
        "[bold blue]⚡ Performance Optimization[/bold blue]\n\n"
        "Analyzing and optimizing configuration...",
        title="Optimization"
    ))
    
    # Build command
    cmd = [sys.executable, 'scripts/optimize_data_sources.py']
    
    if analyze:
        cmd.append('--analyze')
    
    if optimize_flag:
        cmd.append('--optimize')
    
    cmd.extend(['--profile', profile])
    
    if dry_run:
        cmd.append('--dry-run')
    
    if not analyze and not optimize_flag:
        # Default to analyze
        cmd.append('--analyze')
    
    try:
        # Run optimization script
        result = subprocess.run(cmd, cwd=Path.cwd())
        
        if result.returncode == 0:
            console.print(format_success("\n✅ Optimization analysis complete!"))
        else:
            console.print(format_error("❌ Optimization failed"))
            sys.exit(1)
            
    except FileNotFoundError:
        console.print(format_error("Optimization script not found. Make sure you're in the project root."))
        sys.exit(1)
    except Exception as e:
        console.print(format_error(f"Error running optimization: {e}"))
        sys.exit(1)


@performance.command()
@click.option('--items', '-n', type=int, default=500, help='Number of items to test')
@click.option('--distribution', '-d', type=(str, float), multiple=True,
              help='Source distribution (e.g., gmail 0.5 fireflies 0.3)')
async def stress(items, distribution):
    """Run stress test with specified load."""
    console.print(create_panel(
        f"[bold blue]💪 Stress Test[/bold blue]\n\n"
        f"Testing with {items} items...",
        title="Stress Test"
    ))
    
    # Parse distribution
    dist_dict = {}
    if distribution:
        for source, ratio in distribution:
            dist_dict[source] = ratio
    else:
        # Default distribution
        dist_dict = {
            'gmail': 0.5,
            'fireflies': 0.3,
            'google_drive': 0.2
        }
    
    # Ensure ratios sum to 1.0
    total = sum(dist_dict.values())
    if abs(total - 1.0) > 0.01:
        console.print(format_warning(f"Distribution ratios sum to {total:.2f}, normalizing to 1.0"))
        for key in dist_dict:
            dist_dict[key] /= total
    
    console.print("\n[bold]Test Configuration:[/bold]")
    console.print(f"Total items: {items}")
    console.print("Distribution:")
    for source, ratio in dist_dict.items():
        console.print(f"  - {source}: {ratio:.0%} ({int(items * ratio)} items)")
    
    # Import and run stress test
    try:
        from tests.test_performance_data_sources import TestDataSourcePerformance, PerformanceMetrics
        
        test_suite = TestDataSourcePerformance()
        
        # Run stress test
        console.print("\n[cyan]Running stress test...[/cyan]")
        result = await test_suite.test_stress_test_500_daily()
        
        # Display results
        console.print(format_success("\n✅ Stress test completed!"))
        
        console.print("\n[bold]Results:[/bold]")
        console.print(f"Items processed: {result['total_processed']}/{result['total_items']}")
        console.print(f"Duration: {result['duration_seconds']:.2f} seconds")
        console.print(f"Throughput: {result['throughput_items_per_second']:.2f} items/second")
        console.print(f"Daily capacity: {result['estimated_daily_capacity']:,.0f} items/day")
        console.print(f"Success rate: {result['success_rate']:.2%}")
        
        if result['estimated_daily_capacity'] >= items:
            console.print(format_success(f"\n✅ System can handle {items}+ items daily!"))
        else:
            console.print(format_warning(f"\n⚠️ System capacity ({result['estimated_daily_capacity']:,.0f}) below target ({items})"))
        
    except ImportError:
        console.print(format_error("Performance test module not found. Make sure tests are installed."))
        sys.exit(1)
    except Exception as e:
        console.print(format_error(f"Stress test failed: {e}"))
        logger.error("Stress test error", exc_info=True)
        sys.exit(1)


@performance.command()
def report():
    """Generate performance report from latest benchmark."""
    console.print(create_panel(
        "[bold blue]📊 Performance Report[/bold blue]\n\n"
        "Generating report from latest benchmark results...",
        title="Report"
    ))
    
    # Find latest benchmark results
    results_dir = Path("benchmark_results")
    if not results_dir.exists():
        console.print(format_error("No benchmark results found. Run 'vdq performance benchmark' first."))
        sys.exit(1)
    
    # Find latest JSON file
    json_files = list(results_dir.glob("benchmark_results_*.json"))
    if not json_files:
        console.print(format_error("No benchmark result files found."))
        sys.exit(1)
    
    latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
    
    # Find corresponding HTML report
    timestamp = latest_file.stem.split('_', 2)[2]
    html_file = results_dir / f"performance_report_{timestamp}.html"
    
    if html_file.exists():
        console.print(format_success(f"✅ Found report: {html_file}"))
        
        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f"file://{html_file.absolute()}")
            console.print("\n[green]Report opened in browser[/green]")
        except:
            console.print("\n[yellow]Open the report manually:[/yellow]")
            console.print(f"  {html_file.absolute()}")
    else:
        console.print(format_warning("HTML report not found. Displaying raw results:"))
        
        # Display JSON results
        import json
        with open(latest_file) as f:
            results = json.load(f)
        
        for test_result in results:
            console.print(f"\n[bold]{test_result['scenario'].title()}:[/bold]")
            console.print(f"Timestamp: {test_result['timestamp']}")
            if isinstance(test_result.get('result'), dict):
                for key, value in test_result['result'].items():
                    console.print(f"  {key}: {value}")


# Add a convenient alias
@click.command()
@click.pass_context
def perf(ctx):
    """Alias for performance command."""
    ctx.invoke(performance)


if __name__ == "__main__":
    performance()