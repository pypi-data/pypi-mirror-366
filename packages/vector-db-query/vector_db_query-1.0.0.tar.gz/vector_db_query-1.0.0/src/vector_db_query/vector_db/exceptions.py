"""Exceptions for vector database operations."""


class VectorDBError(Exception):
    """Base exception for vector database errors."""
    pass


class ConnectionError(VectorDBError):
    """Raised when connection to vector database fails."""
    pass


class CollectionError(VectorDBError):
    """Raised when collection operations fail."""
    pass


class CollectionNotFoundError(CollectionError):
    """Raised when a collection is not found."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        super().__init__(f"Collection not found: {collection_name}")


class CollectionExistsError(CollectionError):
    """Raised when trying to create a collection that already exists."""
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        super().__init__(f"Collection already exists: {collection_name}")


class VectorOperationError(VectorDBError):
    """Raised when vector operations fail."""
    pass


class InsertionError(VectorOperationError):
    """Raised when vector insertion fails."""
    pass


class SearchError(VectorOperationError):
    """Raised when vector search fails."""
    pass


class StorageError(VectorDBError):
    """Raised when storage operations fail."""
    pass


class BackupError(VectorDBError):
    """Raised when backup operations fail."""
    pass


class RestoreError(VectorDBError):
    """Raised when restore operations fail."""
    pass


class DockerError(VectorDBError):
    """Raised when Docker operations fail."""
    pass


class ContainerNotFoundError(DockerError):
    """Raised when Qdrant container is not found."""
    
    def __init__(self, container_name: str = "vector-db-qdrant"):
        self.container_name = container_name
        super().__init__(f"Container not found: {container_name}")


class ContainerNotRunningError(DockerError):
    """Raised when Qdrant container is not running."""
    
    def __init__(self, container_name: str = "vector-db-qdrant"):
        self.container_name = container_name
        super().__init__(f"Container not running: {container_name}")


class HealthCheckError(VectorDBError):
    """Raised when health check fails."""
    pass