"""
Connection monitoring infrastructure for tracking system connections.

This module provides comprehensive monitoring for all system connections
including Qdrant, MCP Server, database connections, and external services.
"""

from .models import (
    ConnectionType,
    ConnectionStatus,
    ConnectionHealth,
    Connection,
    ConnectionMetrics,
    ConnectionEvent,
    ConnectionCheck
)

from .monitor import (
    ConnectionMonitor,
    get_connection_monitor,
    reset_connection_monitor
)

from .checkers import (
    ConnectionChecker,
    QdrantChecker,
    MCPChecker,
    DatabaseChecker,
    ServiceChecker,
    HTTPChecker
)

__all__ = [
    # Models
    'ConnectionType',
    'ConnectionStatus',
    'ConnectionHealth',
    'Connection',
    'ConnectionMetrics',
    'ConnectionEvent',
    'ConnectionCheck',
    
    # Monitor
    'ConnectionMonitor',
    'get_connection_monitor',
    'reset_connection_monitor',
    
    # Checkers
    'ConnectionChecker',
    'QdrantChecker',
    'MCPChecker',
    'DatabaseChecker',
    'ServiceChecker',
    'HTTPChecker'
]

__version__ = '1.0.0'