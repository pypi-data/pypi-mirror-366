"""Performance optimizations and polish for interactive components."""

import asyncio
import sys
from typing import Dict, Any, Optional, List, Callable
from functools import lru_cache, wraps
from time import time
import gc

from rich.console import Console


class PerformanceMonitor:
    """Monitor and optimize performance of interactive components."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, List[float]] = {}
        self.console = Console()
        self.enabled = False
    
    def measure(self, name: str):
        """Decorator to measure function performance.
        
        Args:
            name: Metric name
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start = time()
                result = func(*args, **kwargs)
                duration = time() - start
                
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(duration)
                
                return result
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not self.enabled:
                    return await func(*args, **kwargs)
                
                start = time()
                result = await func(*args, **kwargs)
                duration = time() - start
                
                if name not in self.metrics:
                    self.metrics[name] = []
                self.metrics[name].append(duration)
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        
        return decorator
    
    def report(self) -> Dict[str, Dict[str, float]]:
        """Generate performance report.
        
        Returns:
            Performance statistics
        """
        report = {}
        
        for name, durations in self.metrics.items():
            if durations:
                report[name] = {
                    "count": len(durations),
                    "total": sum(durations),
                    "average": sum(durations) / len(durations),
                    "min": min(durations),
                    "max": max(durations)
                }
        
        return report
    
    def display_report(self) -> None:
        """Display performance report."""
        from rich.table import Table
        
        report = self.report()
        if not report:
            self.console.print("[yellow]No performance data collected[/yellow]")
            return
        
        table = Table(title="Performance Report", show_header=True)
        table.add_column("Operation", style="cyan")
        table.add_column("Count", style="white")
        table.add_column("Avg (ms)", style="yellow")
        table.add_column("Min (ms)", style="green")
        table.add_column("Max (ms)", style="red")
        table.add_column("Total (ms)", style="magenta")
        
        for name, stats in sorted(report.items()):
            table.add_row(
                name,
                str(stats["count"]),
                f"{stats['average']*1000:.2f}",
                f"{stats['min']*1000:.2f}",
                f"{stats['max']*1000:.2f}",
                f"{stats['total']*1000:.2f}"
            )
        
        self.console.print(table)
    
    def reset(self) -> None:
        """Reset metrics."""
        self.metrics.clear()


# Global performance monitor
perf_monitor = PerformanceMonitor()


class CacheManager:
    """Manage caching for expensive operations."""
    
    def __init__(self, max_size: int = 128):
        """Initialize cache manager.
        
        Args:
            max_size: Maximum cache size
        """
        self.max_size = max_size
        self._caches: Dict[str, Any] = {}
    
    def cached(self, name: str, ttl: Optional[float] = None):
        """Cache decorator with TTL support.
        
        Args:
            name: Cache name
            ttl: Time to live in seconds
        """
        def decorator(func: Callable) -> Callable:
            # Create LRU cache
            cached_func = lru_cache(maxsize=self.max_size)(func)
            self._caches[name] = cached_func
            
            if ttl:
                # Add TTL support
                cache_times: Dict[Any, float] = {}
                
                @wraps(func)
                def wrapper(*args, **kwargs):
                    key = (args, tuple(sorted(kwargs.items())))
                    current_time = time()
                    
                    # Check if cached value expired
                    if key in cache_times:
                        if current_time - cache_times[key] > ttl:
                            # Expired, clear this entry
                            cached_func.cache_clear()
                            cache_times.clear()
                    
                    result = cached_func(*args, **kwargs)
                    cache_times[key] = current_time
                    return result
                
                return wrapper
            
            return cached_func
        
        return decorator
    
    def clear(self, name: Optional[str] = None) -> None:
        """Clear cache.
        
        Args:
            name: Specific cache to clear, or None for all
        """
        if name and name in self._caches:
            self._caches[name].cache_clear()
        else:
            for cache in self._caches.values():
                if hasattr(cache, 'cache_clear'):
                    cache.cache_clear()
    
    def info(self) -> Dict[str, Dict[str, Any]]:
        """Get cache information.
        
        Returns:
            Cache statistics
        """
        info = {}
        
        for name, cache in self._caches.items():
            if hasattr(cache, 'cache_info'):
                cache_info = cache.cache_info()
                info[name] = {
                    "hits": cache_info.hits,
                    "misses": cache_info.misses,
                    "size": cache_info.currsize,
                    "max_size": cache_info.maxsize,
                    "hit_rate": cache_info.hits / (cache_info.hits + cache_info.misses) 
                               if (cache_info.hits + cache_info.misses) > 0 else 0
                }
        
        return info


# Global cache manager
cache_manager = CacheManager()


class LazyLoader:
    """Lazy loading for expensive imports and initializations."""
    
    def __init__(self):
        """Initialize lazy loader."""
        self._loaded: Dict[str, Any] = {}
        self._loaders: Dict[str, Callable] = {}
    
    def register(self, name: str, loader: Callable) -> None:
        """Register a lazy loader.
        
        Args:
            name: Resource name
            loader: Loader function
        """
        self._loaders[name] = loader
    
    def get(self, name: str) -> Any:
        """Get lazy-loaded resource.
        
        Args:
            name: Resource name
            
        Returns:
            Loaded resource
        """
        if name not in self._loaded:
            if name not in self._loaders:
                raise KeyError(f"No loader registered for {name}")
            
            self._loaded[name] = self._loaders[name]()
        
        return self._loaded[name]
    
    def preload(self, names: List[str]) -> None:
        """Preload resources.
        
        Args:
            names: Resource names to preload
        """
        for name in names:
            self.get(name)
    
    def clear(self) -> None:
        """Clear loaded resources."""
        self._loaded.clear()


# Global lazy loader
lazy_loader = LazyLoader()


def optimize_imports():
    """Register lazy imports for heavy modules."""
    # Register lazy loaders for heavy imports
    lazy_loader.register("pandas", lambda: __import__("pandas"))
    lazy_loader.register("numpy", lambda: __import__("numpy"))
    lazy_loader.register("matplotlib", lambda: __import__("matplotlib.pyplot"))
    lazy_loader.register("plotly", lambda: __import__("plotly.graph_objects"))


class MemoryOptimizer:
    """Optimize memory usage."""
    
    @staticmethod
    def optimize_string_memory(strings: List[str]) -> List[str]:
        """Optimize memory for string lists using interning.
        
        Args:
            strings: List of strings
            
        Returns:
            Optimized string list
        """
        # Use string interning for repeated strings
        seen = {}
        optimized = []
        
        for s in strings:
            if s in seen:
                optimized.append(seen[s])
            else:
                interned = sys.intern(s)
                seen[s] = interned
                optimized.append(interned)
        
        return optimized
    
    @staticmethod
    def collect_garbage() -> Dict[str, int]:
        """Force garbage collection and return stats.
        
        Returns:
            Collection statistics
        """
        import gc
        
        before = len(gc.get_objects())
        collected = gc.collect()
        after = len(gc.get_objects())
        
        return {
            "objects_before": before,
            "objects_after": after,
            "collected": collected,
            "freed": before - after
        }
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Get current memory usage.
        
        Returns:
            Memory statistics in MB
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss": memory_info.rss / 1024 / 1024,  # MB
            "vms": memory_info.vms / 1024 / 1024,  # MB
            "percent": process.memory_percent()
        }


class BatchProcessor:
    """Process items in optimized batches."""
    
    def __init__(self, batch_size: int = 100):
        """Initialize batch processor.
        
        Args:
            batch_size: Items per batch
        """
        self.batch_size = batch_size
    
    async def process_async(
        self,
        items: List[Any],
        processor: Callable,
        max_concurrent: int = 5
    ) -> List[Any]:
        """Process items in concurrent batches.
        
        Args:
            items: Items to process
            processor: Async processor function
            max_concurrent: Maximum concurrent batches
            
        Returns:
            Processed results
        """
        results = []
        
        # Split into batches
        batches = [items[i:i + self.batch_size] 
                  for i in range(0, len(items), self.batch_size)]
        
        # Process batches concurrently
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_batch(batch):
            async with semaphore:
                return await processor(batch)
        
        # Process all batches
        batch_results = await asyncio.gather(
            *[process_batch(batch) for batch in batches]
        )
        
        # Flatten results
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results
    
    def process_sync(
        self,
        items: List[Any],
        processor: Callable,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> List[Any]:
        """Process items in batches with progress callback.
        
        Args:
            items: Items to process
            processor: Processor function
            callback: Progress callback (current, total)
            
        Returns:
            Processed results
        """
        results = []
        total = len(items)
        
        for i in range(0, total, self.batch_size):
            batch = items[i:i + self.batch_size]
            batch_results = processor(batch)
            results.extend(batch_results)
            
            if callback:
                callback(min(i + self.batch_size, total), total)
        
        return results


class RenderOptimizer:
    """Optimize rendering performance."""
    
    def __init__(self):
        """Initialize render optimizer."""
        self._render_cache: Dict[str, str] = {}
        self._last_render: Dict[str, float] = {}
        self.min_render_interval = 0.1  # 100ms minimum between renders
    
    def should_render(self, component: str) -> bool:
        """Check if component should render.
        
        Args:
            component: Component name
            
        Returns:
            True if should render
        """
        current_time = time()
        
        if component not in self._last_render:
            self._last_render[component] = current_time
            return True
        
        if current_time - self._last_render[component] >= self.min_render_interval:
            self._last_render[component] = current_time
            return True
        
        return False
    
    def cache_render(self, key: str, content: str) -> None:
        """Cache rendered content.
        
        Args:
            key: Cache key
            content: Rendered content
        """
        self._render_cache[key] = content
    
    def get_cached_render(self, key: str) -> Optional[str]:
        """Get cached render.
        
        Args:
            key: Cache key
            
        Returns:
            Cached content or None
        """
        return self._render_cache.get(key)
    
    def clear_cache(self) -> None:
        """Clear render cache."""
        self._render_cache.clear()


# Global render optimizer
render_optimizer = RenderOptimizer()


def optimize_startup():
    """Optimize application startup."""
    # Lazy load heavy modules
    optimize_imports()
    
    # Pre-compile regex patterns
    import re
    patterns = {
        "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        "url": re.compile(r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'),
        "path": re.compile(r'^(/[^/ ]*)+/?$')
    }
    lazy_loader.register("regex_patterns", lambda: patterns)
    
    # Pre-create commonly used objects
    from rich.style import Style
    common_styles = {
        "success": Style(color="green", bold=True),
        "error": Style(color="red", bold=True),
        "warning": Style(color="yellow", bold=True),
        "info": Style(color="cyan", bold=True)
    }
    lazy_loader.register("common_styles", lambda: common_styles)


# Performance tips
PERFORMANCE_TIPS = """
[bold cyan]Performance Optimization Tips[/bold cyan]

[yellow]1. Enable Caching:[/yellow]
   Use @cache_manager.cached() for expensive operations

[yellow]2. Batch Processing:[/yellow]
   Process items in batches for better performance

[yellow]3. Lazy Loading:[/yellow]
   Use lazy_loader for heavy imports

[yellow]4. Memory Management:[/yellow]
   Call MemoryOptimizer.collect_garbage() periodically

[yellow]5. Render Optimization:[/yellow]
   Use render_optimizer to avoid unnecessary renders

[yellow]6. Monitor Performance:[/yellow]
   Enable perf_monitor to identify bottlenecks
"""