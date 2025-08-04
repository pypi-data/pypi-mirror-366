"""
Performance optimization module for the monitoring system.

This module provides performance enhancements, caching, and optimization
strategies for the enterprise-grade monitoring dashboard.
"""

from .cache_manager import CacheManager, get_cache_manager
from .performance_optimizer import PerformanceOptimizer, get_performance_optimizer
from .batch_processor import BatchProcessor, get_batch_processor
from .connection_pooling import ConnectionPoolManager, get_connection_pool_manager
from .lazy_loader import LazyLoader, get_lazy_loader
from .query_optimizer import QueryOptimizer, get_query_optimizer

__all__ = [
    'CacheManager', 'get_cache_manager',
    'PerformanceOptimizer', 'get_performance_optimizer',
    'BatchProcessor', 'get_batch_processor',
    'ConnectionPoolManager', 'get_connection_pool_manager',
    'LazyLoader', 'get_lazy_loader',
    'QueryOptimizer', 'get_query_optimizer'
]

__version__ = '1.0.0'