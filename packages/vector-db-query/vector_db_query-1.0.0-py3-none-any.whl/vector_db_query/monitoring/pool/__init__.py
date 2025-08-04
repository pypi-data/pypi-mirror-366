"""
Connection pool monitoring and visualization module.

This module provides comprehensive tools for monitoring, analyzing,
and visualizing connection pools across the system.
"""

from .models import (
    PoolType, ConnectionState, PoolHealth,
    PoolConnection, ConnectionPool, PoolMetrics,
    PoolEvent, PoolOptimization
)
from .pool_manager import PoolManager, get_pool_manager, reset_pool_manager
from .pool_ui import ConnectionPoolUI

__all__ = [
    # Enums
    'PoolType', 'ConnectionState', 'PoolHealth',
    # Models
    'PoolConnection', 'ConnectionPool', 'PoolMetrics',
    'PoolEvent', 'PoolOptimization',
    # Services
    'PoolManager', 'get_pool_manager', 'reset_pool_manager',
    # UI
    'ConnectionPoolUI'
]

__version__ = '1.0.0'