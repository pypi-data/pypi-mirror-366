"""Data models for vector database operations."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class VectorPoint:
    """Represents a vector point in the database."""
    
    id: str
    vector: List[float]
    payload: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Qdrant."""
        return {
            "id": self.id,
            "vector": self.vector,
            "payload": self.payload
        }
        
    @classmethod
    def from_embedding(cls, embedding, metadata: Dict[str, Any]) -> "VectorPoint":
        """Create from an Embedding object."""
        return cls(
            id=embedding.chunk_id,
            vector=embedding.to_list(),
            payload=metadata
        )


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    
    id: str
    score: float
    payload: Dict[str, Any]
    vector: Optional[np.ndarray] = None
    
    @property
    def chunk_id(self) -> str:
        """Get chunk ID from payload."""
        return self.payload.get("chunk_id", self.id)
        
    @property
    def document_id(self) -> str:
        """Get document ID from payload."""
        return self.payload.get("document_id", "")
        
    @property
    def file_path(self) -> str:
        """Get file path from payload."""
        return self.payload.get("file_path", "")
        
    @property
    def chunk_text(self) -> str:
        """Get chunk text preview from payload."""
        return self.payload.get("chunk_text", "")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "score": self.score,
            "payload": self.payload,
            "vector": self.vector.tolist() if self.vector is not None else None
        }


@dataclass
class CollectionInfo:
    """Information about a collection."""
    
    name: str
    vector_size: int
    vectors_count: int
    distance_metric: str
    status: str
    config: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_ready(self) -> bool:
        """Check if collection is ready for operations."""
        return self.status.lower() in ["green", "ready", "active"]


@dataclass
class CollectionConfig:
    """Configuration for creating a collection."""
    
    name: str = "documents"
    vector_size: int = 768
    distance: str = "Cosine"
    on_disk_payload: bool = True
    hnsw_config: Dict[str, Any] = field(default_factory=lambda: {
        "m": 16,
        "ef_construct": 128,
        "full_scan_threshold": 10000
    })
    
    def to_qdrant_config(self) -> Dict[str, Any]:
        """Convert to Qdrant collection config."""
        return {
            "vectors": {
                "size": self.vector_size,
                "distance": self.distance
            },
            "on_disk_payload": self.on_disk_payload,
            "hnsw_config": self.hnsw_config
        }


@dataclass
class HealthStatus:
    """Health status of the vector database."""
    
    is_healthy: bool
    version: str = ""
    collections_count: int = 0
    vectors_count: int = 0
    disk_usage_mb: float = 0.0
    memory_usage_mb: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_healthy": self.is_healthy,
            "version": self.version,
            "collections_count": self.collections_count,
            "vectors_count": self.vectors_count,
            "disk_usage_mb": self.disk_usage_mb,
            "memory_usage_mb": self.memory_usage_mb,
            "error": self.error
        }


@dataclass
class StorageStats:
    """Storage statistics for the vector database."""
    
    total_vectors: int
    total_collections: int
    disk_usage_mb: float
    memory_usage_mb: float
    collections: Dict[str, int] = field(default_factory=dict)  # name -> count
    
    def get_summary(self) -> str:
        """Get summary string."""
        return (
            f"Collections: {self.total_collections} | "
            f"Vectors: {self.total_vectors} | "
            f"Disk: {self.disk_usage_mb:.1f}MB | "
            f"Memory: {self.memory_usage_mb:.1f}MB"
        )


@dataclass
class StorageResult:
    """Result of a storage operation."""
    
    success: bool
    stored_count: int
    failed_count: int
    collection_name: str
    duration: float
    errors: List[str] = field(default_factory=list)
    
    @property
    def total_count(self) -> int:
        """Get total count attempted."""
        return self.stored_count + self.failed_count
        
    def get_summary(self) -> str:
        """Get summary string."""
        return (
            f"Stored {self.stored_count}/{self.total_count} vectors "
            f"in {self.duration:.2f}s"
        )


@dataclass
class BackupInfo:
    """Information about a backup."""
    
    backup_id: str
    collection_name: str
    created_at: datetime
    size_mb: float
    vectors_count: int
    path: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "backup_id": self.backup_id,
            "collection_name": self.collection_name,
            "created_at": self.created_at.isoformat(),
            "size_mb": self.size_mb,
            "vectors_count": self.vectors_count,
            "path": self.path
        }