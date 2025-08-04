"""
Data models for Qdrant management and monitoring.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


class CollectionStatus(Enum):
    """Qdrant collection status."""
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    INITIALIZING = "initializing"


class PointStatus(Enum):
    """Status of points in collection."""
    INDEXED = "indexed"
    PENDING = "pending"
    FAILED = "failed"


class IndexType(Enum):
    """Qdrant index types."""
    FLAT = "flat"
    HNSW = "hnsw"
    IVF_FLAT = "ivf_flat"


class Distance(Enum):
    """Distance metrics for vector similarity."""
    COSINE = "cosine"
    EUCLID = "euclid"
    DOT = "dot"


class OptimizationStatus(Enum):
    """Collection optimization status."""
    IDLE = "idle"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CollectionConfig:
    """Configuration for a Qdrant collection."""
    name: str
    vector_size: int
    distance: Distance = Distance.COSINE
    
    # Index configuration
    index_type: IndexType = IndexType.HNSW
    hnsw_config: Dict[str, Any] = field(default_factory=lambda: {
        "m": 16,
        "ef_construct": 200,
        "full_scan_threshold": 10000
    })
    
    # Performance settings
    wal_config: Dict[str, Any] = field(default_factory=lambda: {
        "wal_capacity_mb": 32,
        "wal_segments_ahead": 0
    })
    optimizers_config: Dict[str, Any] = field(default_factory=lambda: {
        "deleted_threshold": 0.2,
        "vacuum_min_vector_number": 1000,
        "default_segment_number": 0,
        "max_segment_size": None,
        "memmap_threshold": None,
        "indexing_threshold": 20000,
        "flush_interval_sec": 5,
        "max_optimization_threads": 1
    })
    
    # Replication settings
    replication_factor: int = 1
    write_consistency_factor: int = 1
    
    # Optional payload schema
    payload_schema: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'vector_size': self.vector_size,
            'distance': self.distance.value,
            'index_type': self.index_type.value,
            'hnsw_config': self.hnsw_config,
            'wal_config': self.wal_config,
            'optimizers_config': self.optimizers_config,
            'replication_factor': self.replication_factor,
            'write_consistency_factor': self.write_consistency_factor,
            'payload_schema': self.payload_schema
        }


@dataclass
class CollectionInfo:
    """Information about a Qdrant collection."""
    name: str
    status: CollectionStatus
    vectors_count: int
    points_count: int
    segments_count: int
    config: CollectionConfig
    
    # Size metrics
    size_bytes: int = 0
    indexed_vectors_count: int = 0
    
    # Performance metrics
    indexing_time_ms: float = 0.0
    search_latency_ms: float = 0.0
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    optimized_at: Optional[datetime] = None
    
    # Health indicators
    is_optimized: bool = True
    has_errors: bool = False
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'status': self.status.value,
            'vectors_count': self.vectors_count,
            'points_count': self.points_count,
            'segments_count': self.segments_count,
            'config': self.config.to_dict(),
            'size_bytes': self.size_bytes,
            'indexed_vectors_count': self.indexed_vectors_count,
            'performance': {
                'indexing_time_ms': self.indexing_time_ms,
                'search_latency_ms': self.search_latency_ms
            },
            'timestamps': {
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'updated_at': self.updated_at.isoformat() if self.updated_at else None,
                'optimized_at': self.optimized_at.isoformat() if self.optimized_at else None
            },
            'health': {
                'is_optimized': self.is_optimized,
                'has_errors': self.has_errors,
                'error_message': self.error_message
            }
        }


@dataclass
class PointData:
    """Data for a single point in Qdrant."""
    id: Union[str, int]
    vector: List[float]
    payload: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'vector': self.vector,
            'payload': self.payload
        }


@dataclass
class SearchRequest:
    """Search request configuration."""
    collection_name: str
    vector: List[float]
    limit: int = 10
    offset: int = 0
    
    # Filtering
    filter: Optional[Dict[str, Any]] = None
    
    # Search parameters
    with_payload: bool = True
    with_vector: bool = False
    score_threshold: Optional[float] = None
    
    # Performance
    params: Optional[Dict[str, Any]] = None  # HNSW search params
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'collection_name': self.collection_name,
            'vector': self.vector,
            'limit': self.limit,
            'offset': self.offset,
            'filter': self.filter,
            'with_payload': self.with_payload,
            'with_vector': self.with_vector,
            'score_threshold': self.score_threshold,
            'params': self.params
        }


@dataclass
class SearchResult:
    """Search result from Qdrant."""
    id: Union[str, int]
    score: float
    payload: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'score': self.score,
            'payload': self.payload,
            'vector': self.vector
        }


@dataclass
class BatchOperation:
    """Batch operation for points."""
    operation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    operation_type: str = ""  # insert, update, delete
    collection_name: str = ""
    points: List[PointData] = field(default_factory=list)
    
    # For delete operations
    point_ids: List[Union[str, int]] = field(default_factory=list)
    filter: Optional[Dict[str, Any]] = None
    
    # Status tracking
    status: str = "pending"  # pending, processing, completed, failed
    processed_count: int = 0
    error_count: int = 0
    errors: List[str] = field(default_factory=list)
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def duration_ms(self) -> Optional[float]:
        """Get operation duration in milliseconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'collection_name': self.collection_name,
            'points_count': len(self.points),
            'status': self.status,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'errors': self.errors,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_ms': self.duration_ms()
        }


@dataclass
class OptimizationTask:
    """Collection optimization task."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    collection_name: str = ""
    optimization_type: str = "indexing"  # indexing, vacuum, segments_merge
    
    # Status
    status: OptimizationStatus = OptimizationStatus.IDLE
    progress: float = 0.0  # 0-100
    
    # Results
    segments_before: int = 0
    segments_after: int = 0
    size_before_bytes: int = 0
    size_after_bytes: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Errors
    error_message: Optional[str] = None
    
    def space_saved_bytes(self) -> int:
        """Calculate space saved."""
        return max(0, self.size_before_bytes - self.size_after_bytes)
    
    def duration_seconds(self) -> Optional[float]:
        """Get duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'collection_name': self.collection_name,
            'optimization_type': self.optimization_type,
            'status': self.status.value,
            'progress': self.progress,
            'results': {
                'segments_before': self.segments_before,
                'segments_after': self.segments_after,
                'size_before_bytes': self.size_before_bytes,
                'size_after_bytes': self.size_after_bytes,
                'space_saved_bytes': self.space_saved_bytes()
            },
            'timing': {
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
                'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
                'duration_seconds': self.duration_seconds()
            },
            'error_message': self.error_message
        }


@dataclass
class ClusterNode:
    """Qdrant cluster node information."""
    node_id: str
    uri: str
    status: str = "online"  # online, offline, syncing
    
    # Node metrics
    collections_count: int = 0
    total_vectors: int = 0
    total_size_bytes: int = 0
    
    # Performance
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_gb: float = 0.0
    
    # Network
    requests_per_second: float = 0.0
    latency_ms: float = 0.0
    
    # Timestamps
    last_seen: datetime = field(default_factory=datetime.now)
    joined_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'uri': self.uri,
            'status': self.status,
            'metrics': {
                'collections_count': self.collections_count,
                'total_vectors': self.total_vectors,
                'total_size_bytes': self.total_size_bytes
            },
            'performance': {
                'cpu_usage': self.cpu_usage,
                'memory_usage_mb': self.memory_usage_mb,
                'disk_usage_gb': self.disk_usage_gb,
                'requests_per_second': self.requests_per_second,
                'latency_ms': self.latency_ms
            },
            'timestamps': {
                'last_seen': self.last_seen.isoformat(),
                'joined_at': self.joined_at.isoformat() if self.joined_at else None
            }
        }


@dataclass
class QdrantMetrics:
    """Overall Qdrant instance metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Collections
    total_collections: int = 0
    total_vectors: int = 0
    total_points: int = 0
    
    # Storage
    total_size_bytes: int = 0
    index_size_bytes: int = 0
    payload_size_bytes: int = 0
    
    # Performance
    avg_search_latency_ms: float = 0.0
    avg_insert_latency_ms: float = 0.0
    requests_per_second: float = 0.0
    
    # Resources
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_gb: float = 0.0
    
    # Cluster info (if applicable)
    cluster_nodes: List[ClusterNode] = field(default_factory=list)
    is_distributed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'collections': {
                'total': self.total_collections,
                'vectors': self.total_vectors,
                'points': self.total_points
            },
            'storage': {
                'total_bytes': self.total_size_bytes,
                'index_bytes': self.index_size_bytes,
                'payload_bytes': self.payload_size_bytes
            },
            'performance': {
                'avg_search_latency_ms': self.avg_search_latency_ms,
                'avg_insert_latency_ms': self.avg_insert_latency_ms,
                'requests_per_second': self.requests_per_second
            },
            'resources': {
                'cpu_percent': self.cpu_usage_percent,
                'memory_mb': self.memory_usage_mb,
                'disk_gb': self.disk_usage_gb
            },
            'cluster': {
                'is_distributed': self.is_distributed,
                'nodes': [node.to_dict() for node in self.cluster_nodes]
            }
        }


@dataclass 
class BackupTask:
    """Qdrant backup task."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    backup_type: str = "full"  # full, incremental, collection
    
    # Target
    collections: List[str] = field(default_factory=list)
    destination_path: str = ""
    
    # Status
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    bytes_processed: int = 0
    total_bytes: int = 0
    
    # Timing
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    backup_size_bytes: int = 0
    collections_backed_up: int = 0
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'backup_type': self.backup_type,
            'collections': self.collections,
            'destination_path': self.destination_path,
            'status': self.status,
            'progress': self.progress,
            'bytes_processed': self.bytes_processed,
            'total_bytes': self.total_bytes,
            'timing': {
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None
            },
            'results': {
                'backup_size_bytes': self.backup_size_bytes,
                'collections_backed_up': self.collections_backed_up,
                'error_message': self.error_message
            }
        }