"""
Qdrant vector database management and monitoring infrastructure.

This module provides comprehensive management tools for Qdrant,
including collection management, point operations, monitoring,
and optimization capabilities.
"""

from .models import (
    CollectionConfig,
    CollectionInfo,
    CollectionStatus,
    PointData,
    SearchRequest,
    SearchResult,
    BatchOperation,
    OptimizationTask,
    OptimizationStatus,
    QdrantMetrics,
    Distance,
    IndexType,
    PointStatus,
    ClusterNode,
    BackupTask
)

from .manager import (
    QdrantManager,
    get_qdrant_manager,
    reset_qdrant_manager
)

from .qdrant_ui import QdrantManagementUI

__all__ = [
    # Models
    'CollectionConfig',
    'CollectionInfo', 
    'CollectionStatus',
    'PointData',
    'SearchRequest',
    'SearchResult',
    'BatchOperation',
    'OptimizationTask',
    'OptimizationStatus',
    'QdrantMetrics',
    'Distance',
    'IndexType',
    'PointStatus',
    'ClusterNode',
    'BackupTask',
    
    # Manager
    'QdrantManager',
    'get_qdrant_manager',
    'reset_qdrant_manager',
    
    # UI
    'QdrantManagementUI'
]

__version__ = '1.0.0'