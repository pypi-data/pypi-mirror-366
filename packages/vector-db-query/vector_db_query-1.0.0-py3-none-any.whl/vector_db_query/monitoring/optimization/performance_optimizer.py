"""
Comprehensive performance optimizer for the monitoring system.
"""

import os
import time
import threading
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Tuple
from threading import RLock, Thread
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


class OptimizationLevel(Enum):
    """Optimization aggressiveness levels."""
    MINIMAL = "minimal"          # Basic optimizations only
    BALANCED = "balanced"        # Balance performance and resources
    AGGRESSIVE = "aggressive"    # Maximum performance optimizations
    ADAPTIVE = "adaptive"        # Dynamically adjust based on load


class ResourceType(Enum):
    """System resource types."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


@dataclass
class PerformanceMetrics:
    """System performance metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0
    network_sent_mb: float = 0.0
    network_recv_mb: float = 0.0
    active_threads: int = 0
    response_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'memory_mb': self.memory_mb,
            'disk_io_read_mb': self.disk_io_read_mb,
            'disk_io_write_mb': self.disk_io_write_mb,
            'network_sent_mb': self.network_sent_mb,
            'network_recv_mb': self.network_recv_mb,
            'active_threads': self.active_threads,
            'response_time_ms': self.response_time_ms
        }


@dataclass
class OptimizationRule:
    """Rule for triggering optimizations."""
    name: str
    resource_type: ResourceType
    threshold: float
    duration_seconds: int
    action: Callable[[], None]
    cooldown_seconds: int = 300
    last_triggered: Optional[datetime] = None
    enabled: bool = True
    
    def should_trigger(self, current_value: float, duration_met: bool) -> bool:
        """Check if rule should trigger."""
        if not self.enabled:
            return False
        
        # Check cooldown
        if self.last_triggered:
            cooldown_elapsed = (datetime.now() - self.last_triggered).total_seconds()
            if cooldown_elapsed < self.cooldown_seconds:
                return False
        
        # Check threshold and duration
        return current_value > self.threshold and duration_met
    
    def trigger(self) -> None:
        """Execute the optimization action."""
        self.action()
        self.last_triggered = datetime.now()


class PerformanceOptimizer:
    """
    Comprehensive performance optimization system.
    """
    
    def __init__(self,
                 optimization_level: OptimizationLevel = OptimizationLevel.BALANCED,
                 monitor_interval_seconds: int = 5,
                 history_size: int = 100):
        """Initialize performance optimizer."""
        self._lock = RLock()
        self.optimization_level = optimization_level
        self.monitor_interval = monitor_interval_seconds
        self.history_size = history_size
        
        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread: Optional[Thread] = None
        
        # Performance history
        self.metrics_history: deque[PerformanceMetrics] = deque(maxlen=history_size)
        
        # Thread pools
        self.thread_pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix="PerfOpt")
        self.process_pool: Optional[ProcessPoolExecutor] = None
        
        # Optimization rules
        self.optimization_rules: List[OptimizationRule] = []
        self._setup_default_rules()
        
        # Resource baselines
        self.resource_baselines: Dict[ResourceType, float] = {}
        self._establish_baselines()
        
        # Optimization callbacks
        self.optimization_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []
        
        # Async event loop for async optimizations
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def _setup_default_rules(self) -> None:
        """Set up default optimization rules."""
        # High CPU usage rule
        self.add_rule(OptimizationRule(
            name="high_cpu_usage",
            resource_type=ResourceType.CPU,
            threshold=80.0,
            duration_seconds=30,
            action=self._optimize_cpu_usage,
            cooldown_seconds=300
        ))
        
        # High memory usage rule
        self.add_rule(OptimizationRule(
            name="high_memory_usage",
            resource_type=ResourceType.MEMORY,
            threshold=85.0,
            duration_seconds=20,
            action=self._optimize_memory_usage,
            cooldown_seconds=300
        ))
        
        # High disk I/O rule
        self.add_rule(OptimizationRule(
            name="high_disk_io",
            resource_type=ResourceType.DISK,
            threshold=100.0,  # MB/s
            duration_seconds=60,
            action=self._optimize_disk_io,
            cooldown_seconds=600
        ))
    
    def _establish_baselines(self) -> None:
        """Establish resource usage baselines."""
        try:
            # Get current system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # Get disk I/O if available
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
            
            # Get network I/O if available
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
            net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0
            
            # Store baselines
            self.resource_baselines = {
                ResourceType.CPU: cpu_percent,
                ResourceType.MEMORY: memory_percent,
                ResourceType.DISK: (disk_read_mb + disk_write_mb) / 2,
                ResourceType.NETWORK: (net_sent_mb + net_recv_mb) / 2
            }
        except Exception as e:
            self.logger.error(f"Failed to establish baselines: {e}")
    
    def start_monitoring(self) -> None:
        """Start performance monitoring."""
        with self._lock:
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
                self.monitor_thread.start()
                self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop performance monitoring."""
        with self._lock:
            if self.monitoring_active:
                self.monitoring_active = False
                if self.monitor_thread:
                    self.monitor_thread.join(timeout=5)
                self.logger.info("Performance monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        disk_io_prev = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
        net_io_prev = psutil.net_io_counters() if hasattr(psutil, 'net_io_counters') else None
        
        while self.monitoring_active:
            try:
                # Collect current metrics
                metrics = self._collect_metrics(disk_io_prev, net_io_prev)
                
                # Store in history
                with self._lock:
                    self.metrics_history.append(metrics)
                
                # Check optimization rules
                self._check_optimization_rules(metrics)
                
                # Update previous I/O counters
                disk_io_prev = psutil.disk_io_counters() if hasattr(psutil, 'disk_io_counters') else None
                net_io_prev = psutil.net_io_counters() if hasattr(psutil, 'net_io_counters') else None
                
                # Sleep for monitoring interval
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitor_interval)
    
    def _collect_metrics(self, disk_io_prev, net_io_prev) -> PerformanceMetrics:
        """Collect current system metrics."""
        metrics = PerformanceMetrics()
        
        try:
            # CPU usage
            metrics.cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            metrics.memory_percent = memory.percent
            metrics.memory_mb = memory.used / (1024 * 1024)
            
            # Disk I/O (calculate rate)
            if disk_io_prev and hasattr(psutil, 'disk_io_counters'):
                disk_io_curr = psutil.disk_io_counters()
                if disk_io_curr:
                    read_diff = (disk_io_curr.read_bytes - disk_io_prev.read_bytes) / (1024 * 1024)
                    write_diff = (disk_io_curr.write_bytes - disk_io_prev.write_bytes) / (1024 * 1024)
                    metrics.disk_io_read_mb = read_diff / self.monitor_interval
                    metrics.disk_io_write_mb = write_diff / self.monitor_interval
            
            # Network I/O (calculate rate)
            if net_io_prev and hasattr(psutil, 'net_io_counters'):
                net_io_curr = psutil.net_io_counters()
                if net_io_curr:
                    sent_diff = (net_io_curr.bytes_sent - net_io_prev.bytes_sent) / (1024 * 1024)
                    recv_diff = (net_io_curr.bytes_recv - net_io_prev.bytes_recv) / (1024 * 1024)
                    metrics.network_sent_mb = sent_diff / self.monitor_interval
                    metrics.network_recv_mb = recv_diff / self.monitor_interval
            
            # Active threads
            metrics.active_threads = threading.active_count()
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
        
        return metrics
    
    def _check_optimization_rules(self, current_metrics: PerformanceMetrics) -> None:
        """Check and trigger optimization rules."""
        with self._lock:
            for rule in self.optimization_rules:
                # Get current value for the resource type
                current_value = self._get_resource_value(current_metrics, rule.resource_type)
                
                # Check if threshold has been exceeded for required duration
                duration_met = self._check_duration_threshold(
                    rule.resource_type,
                    rule.threshold,
                    rule.duration_seconds
                )
                
                # Trigger rule if conditions are met
                if rule.should_trigger(current_value, duration_met):
                    self.logger.info(f"Triggering optimization rule: {rule.name}")
                    
                    # Execute in thread pool to avoid blocking
                    self.thread_pool.submit(self._execute_rule, rule)
    
    def _get_resource_value(self, metrics: PerformanceMetrics, resource_type: ResourceType) -> float:
        """Get current value for a resource type."""
        if resource_type == ResourceType.CPU:
            return metrics.cpu_percent
        elif resource_type == ResourceType.MEMORY:
            return metrics.memory_percent
        elif resource_type == ResourceType.DISK:
            return metrics.disk_io_read_mb + metrics.disk_io_write_mb
        elif resource_type == ResourceType.NETWORK:
            return metrics.network_sent_mb + metrics.network_recv_mb
        return 0.0
    
    def _check_duration_threshold(self, resource_type: ResourceType, threshold: float, duration_seconds: int) -> bool:
        """Check if resource has exceeded threshold for required duration."""
        if len(self.metrics_history) < duration_seconds / self.monitor_interval:
            return False
        
        # Check recent metrics
        samples_needed = int(duration_seconds / self.monitor_interval)
        recent_metrics = list(self.metrics_history)[-samples_needed:]
        
        # Check if all samples exceed threshold
        for metrics in recent_metrics:
            value = self._get_resource_value(metrics, resource_type)
            if value <= threshold:
                return False
        
        return True
    
    def _execute_rule(self, rule: OptimizationRule) -> None:
        """Execute optimization rule with error handling."""
        try:
            rule.trigger()
            
            # Notify callbacks
            self._notify_optimization(rule.name, {
                'resource_type': rule.resource_type.value,
                'threshold': rule.threshold,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self.logger.error(f"Error executing rule {rule.name}: {e}")
    
    def _optimize_cpu_usage(self) -> None:
        """Optimize high CPU usage."""
        self.logger.info("Optimizing CPU usage")
        
        if self.optimization_level == OptimizationLevel.MINIMAL:
            # Basic optimization - reduce thread priority
            try:
                psutil.Process().nice(10)
            except:
                pass
                
        elif self.optimization_level in [OptimizationLevel.BALANCED, OptimizationLevel.ADAPTIVE]:
            # Balanced optimization
            # Reduce thread pool sizes
            if hasattr(self.thread_pool, '_max_workers'):
                self.thread_pool._max_workers = max(2, self.thread_pool._max_workers - 2)
            
            # Trigger garbage collection
            gc.collect()
            
        elif self.optimization_level == OptimizationLevel.AGGRESSIVE:
            # Aggressive optimization
            # Force garbage collection
            gc.collect(2)
            
            # Reduce process priority
            try:
                psutil.Process().nice(19)
            except:
                pass
            
            # Limit CPU affinity if possible
            try:
                p = psutil.Process()
                cpu_count = psutil.cpu_count()
                if cpu_count > 2:
                    # Use only half the CPUs
                    p.cpu_affinity(list(range(cpu_count // 2)))
            except:
                pass
    
    def _optimize_memory_usage(self) -> None:
        """Optimize high memory usage."""
        self.logger.info("Optimizing memory usage")
        
        # Force garbage collection
        gc.collect()
        
        if self.optimization_level != OptimizationLevel.MINIMAL:
            # Clear caches (if cache manager is available)
            try:
                from .cache_manager import get_cache_manager
                cache_manager = get_cache_manager()
                
                # Clear old entries based on optimization level
                if self.optimization_level == OptimizationLevel.AGGRESSIVE:
                    cache_manager.clear()
                else:
                    cache_manager.cleanup_expired()
                    
            except ImportError:
                pass
            
            # Trim memory if possible
            if hasattr(gc, 'freeze'):
                gc.freeze()
                gc.collect()
                gc.unfreeze()
    
    def _optimize_disk_io(self) -> None:
        """Optimize high disk I/O."""
        self.logger.info("Optimizing disk I/O")
        
        # Implement I/O throttling
        if self.optimization_level != OptimizationLevel.MINIMAL:
            # This would need to be integrated with actual I/O operations
            # For now, we'll just log the optimization
            pass
    
    def add_rule(self, rule: OptimizationRule) -> None:
        """Add optimization rule."""
        with self._lock:
            self.optimization_rules.append(rule)
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove optimization rule by name."""
        with self._lock:
            for i, rule in enumerate(self.optimization_rules):
                if rule.name == rule_name:
                    del self.optimization_rules[i]
                    return True
            return False
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics."""
        with self._lock:
            if not self.metrics_history:
                return {}
            
            recent_metrics = list(self.metrics_history)
            
            # Calculate averages
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk_io = sum(m.disk_io_read_mb + m.disk_io_write_mb for m in recent_metrics) / len(recent_metrics)
            avg_network = sum(m.network_sent_mb + m.network_recv_mb for m in recent_metrics) / len(recent_metrics)
            
            # Get current metrics
            current = recent_metrics[-1] if recent_metrics else PerformanceMetrics()
            
            return {
                'current': current.to_dict(),
                'averages': {
                    'cpu_percent': round(avg_cpu, 2),
                    'memory_percent': round(avg_memory, 2),
                    'disk_io_mb_per_sec': round(avg_disk_io, 2),
                    'network_mb_per_sec': round(avg_network, 2)
                },
                'optimization_level': self.optimization_level.value,
                'active_rules': len([r for r in self.optimization_rules if r.enabled]),
                'metrics_count': len(recent_metrics)
            }
    
    def add_optimization_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add callback for optimization events."""
        with self._lock:
            self.optimization_callbacks.append(callback)
    
    def _notify_optimization(self, rule_name: str, details: Dict[str, Any]) -> None:
        """Notify callbacks of optimization event."""
        for callback in self.optimization_callbacks:
            try:
                callback(rule_name, details)
            except Exception as e:
                self.logger.error(f"Error in optimization callback: {e}")
    
    def set_optimization_level(self, level: OptimizationLevel) -> None:
        """Change optimization level."""
        with self._lock:
            self.optimization_level = level
            self.logger.info(f"Optimization level changed to: {level.value}")
            
            # Adjust rules based on level
            if level == OptimizationLevel.MINIMAL:
                # Increase thresholds for minimal optimization
                for rule in self.optimization_rules:
                    if rule.name == "high_cpu_usage":
                        rule.threshold = 95.0
                    elif rule.name == "high_memory_usage":
                        rule.threshold = 95.0
            elif level == OptimizationLevel.AGGRESSIVE:
                # Decrease thresholds for aggressive optimization
                for rule in self.optimization_rules:
                    if rule.name == "high_cpu_usage":
                        rule.threshold = 70.0
                    elif rule.name == "high_memory_usage":
                        rule.threshold = 75.0
    
    def shutdown(self) -> None:
        """Shutdown the optimizer."""
        self.stop_monitoring()
        
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        if self.process_pool:
            self.process_pool.shutdown(wait=True)
        
        # Clear resources
        self.metrics_history.clear()
        self.optimization_rules.clear()


# Global optimizer instance
_performance_optimizer = None
_optimizer_lock = RLock()


def get_performance_optimizer(**kwargs) -> PerformanceOptimizer:
    """
    Get the global performance optimizer instance (singleton).
    
    Returns:
        Global performance optimizer instance
    """
    global _performance_optimizer
    with _optimizer_lock:
        if _performance_optimizer is None:
            _performance_optimizer = PerformanceOptimizer(**kwargs)
        return _performance_optimizer


def reset_performance_optimizer() -> None:
    """Reset the global performance optimizer (mainly for testing)."""
    global _performance_optimizer
    with _optimizer_lock:
        if _performance_optimizer:
            _performance_optimizer.shutdown()
        _performance_optimizer = None