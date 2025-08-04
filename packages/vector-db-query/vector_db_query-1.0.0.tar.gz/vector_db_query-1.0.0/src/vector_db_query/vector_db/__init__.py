"""Vector database module for Vector DB Query System."""

from vector_db_query.vector_db.service import VectorDBService
from vector_db_query.vector_db.client import QdrantClient
from vector_db_query.vector_db.docker_manager import QdrantDockerManager
from vector_db_query.vector_db.collection import CollectionManager
from vector_db_query.vector_db.operations import VectorOperations
from vector_db_query.vector_db.storage import StorageManager
from vector_db_query.vector_db.models import (
    VectorPoint,
    SearchResult,
    CollectionInfo,
    CollectionConfig,
    HealthStatus,
    StorageStats,
    StorageResult,
    BackupInfo
)
from vector_db_query.vector_db.exceptions import (
    VectorDBError,
    ConnectionError,
    CollectionError,
    CollectionNotFoundError,
    CollectionExistsError,
    VectorOperationError,
    InsertionError,
    SearchError,
    StorageError,
    BackupError,
    RestoreError,
    DockerError,
    ContainerNotFoundError,
    ContainerNotRunningError,
    HealthCheckError
)

__all__ = [
    # Main service
    "VectorDBService",
    
    # Core components
    "QdrantClient",
    "QdrantDockerManager",
    "CollectionManager",
    "VectorOperations",
    "StorageManager",
    
    # Models
    "VectorPoint",
    "SearchResult",
    "CollectionInfo",
    "CollectionConfig",
    "HealthStatus",
    "StorageStats",
    "StorageResult",
    "BackupInfo",
    
    # Exceptions
    "VectorDBError",
    "ConnectionError",
    "CollectionError",
    "CollectionNotFoundError",
    "CollectionExistsError",
    "VectorOperationError",
    "InsertionError",
    "SearchError",
    "StorageError",
    "BackupError",
    "RestoreError",
    "DockerError",
    "ContainerNotFoundError",
    "ContainerNotRunningError",
    "HealthCheckError",
]