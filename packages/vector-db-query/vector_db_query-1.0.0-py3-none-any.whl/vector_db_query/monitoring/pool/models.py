"""
Data models for connection pool monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


class PoolType(Enum):
    """Types of connection pools."""
    DATABASE = "database"
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    REDIS = "redis"
    QDRANT = "qdrant"
    MCP = "mcp"
    CUSTOM = "custom"


class ConnectionState(Enum):
    """Connection states in the pool."""
    IDLE = "idle"           # Available for use
    ACTIVE = "active"       # Currently in use
    RESERVED = "reserved"   # Reserved but not yet active
    STALE = "stale"        # Needs refresh
    CLOSING = "closing"     # Being closed
    CLOSED = "closed"       # Closed
    ERROR = "error"         # In error state


class PoolHealth(Enum):
    """Overall pool health status."""
    HEALTHY = "healthy"         # All good
    WARNING = "warning"         # Some issues but functional
    DEGRADED = "degraded"       # Significant issues
    CRITICAL = "critical"       # Major problems
    FAILED = "failed"          # Pool not functional


@dataclass
class PoolConnection:
    """Individual connection in a pool."""
    connection_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pool_id: str = ""
    state: ConnectionState = ConnectionState.IDLE
    
    # Lifecycle timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    last_checked_at: Optional[datetime] = None
    
    # Usage metrics
    use_count: int = 0
    total_time_active_ms: float = 0.0
    last_activity_duration_ms: float = 0.0
    
    # Connection details
    remote_address: Optional[str] = None
    local_port: Optional[int] = None
    protocol: Optional[str] = None
    
    # Health metrics
    error_count: int = 0
    last_error: Optional[str] = None
    health_score: float = 100.0
    
    # Request tracking
    current_request_id: Optional[str] = None
    current_request_started: Optional[datetime] = None
    
    def is_idle(self) -> bool:
        """Check if connection is idle."""
        return self.state == ConnectionState.IDLE
    
    def is_stale(self, max_idle_seconds: int = 300) -> bool:
        """Check if connection is stale."""
        if self.last_used_at is None:
            return False
        
        idle_time = datetime.now() - self.last_used_at
        return idle_time.total_seconds() > max_idle_seconds
    
    def calculate_efficiency(self) -> float:
        """Calculate connection efficiency (0-100)."""
        if self.use_count == 0:
            return 0.0
        
        # Factor in usage rate and error rate
        usage_score = min(self.use_count / 100, 1.0) * 50
        error_score = max(0, 50 - (self.error_count * 5))
        
        return usage_score + error_score
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'connection_id': self.connection_id,
            'pool_id': self.pool_id,
            'state': self.state.value,
            'created_at': self.created_at.isoformat(),
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'use_count': self.use_count,
            'total_time_active_ms': self.total_time_active_ms,
            'error_count': self.error_count,
            'health_score': self.health_score,
            'efficiency': self.calculate_efficiency(),
            'is_stale': self.is_stale(),
            'remote_address': self.remote_address,
            'protocol': self.protocol
        }


@dataclass
class ConnectionPool:
    """Connection pool configuration and state."""
    pool_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    pool_type: PoolType = PoolType.DATABASE
    
    # Configuration
    min_size: int = 1
    max_size: int = 10
    target_size: int = 5
    max_idle_seconds: int = 300
    max_lifetime_seconds: int = 3600
    
    # Connection settings
    connection_timeout_ms: int = 5000
    request_timeout_ms: int = 30000
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    
    # Health thresholds
    health_check_interval_seconds: int = 30
    unhealthy_threshold: int = 3
    healthy_threshold: int = 2
    
    # Resource limits
    max_requests_per_connection: int = 1000
    max_concurrent_requests: int = 100
    
    # State
    created_at: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    health_status: PoolHealth = PoolHealth.HEALTHY
    
    # Connections
    connections: Dict[str, PoolConnection] = field(default_factory=dict)
    
    # Metrics
    total_connections_created: int = 0
    total_connections_destroyed: int = 0
    total_requests_handled: int = 0
    total_errors: int = 0
    
    def get_connection_counts(self) -> Dict[ConnectionState, int]:
        """Get count of connections by state."""
        counts = {state: 0 for state in ConnectionState}
        for conn in self.connections.values():
            counts[conn.state] += 1
        return counts
    
    def get_active_connections(self) -> List[PoolConnection]:
        """Get all active connections."""
        return [c for c in self.connections.values() if c.state == ConnectionState.ACTIVE]
    
    def get_idle_connections(self) -> List[PoolConnection]:
        """Get all idle connections."""
        return [c for c in self.connections.values() if c.state == ConnectionState.IDLE]
    
    def calculate_utilization(self) -> float:
        """Calculate pool utilization percentage."""
        total = len(self.connections)
        if total == 0:
            return 0.0
        
        active = len(self.get_active_connections())
        return (active / total) * 100
    
    def needs_scaling(self) -> str:
        """Determine if pool needs scaling."""
        utilization = self.calculate_utilization()
        current_size = len(self.connections)
        
        if utilization > 80 and current_size < self.max_size:
            return "scale_up"
        elif utilization < 20 and current_size > self.min_size:
            return "scale_down"
        else:
            return "maintain"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        counts = self.get_connection_counts()
        
        return {
            'pool_id': self.pool_id,
            'name': self.name,
            'type': self.pool_type.value,
            'configuration': {
                'min_size': self.min_size,
                'max_size': self.max_size,
                'target_size': self.target_size,
                'current_size': len(self.connections)
            },
            'health': {
                'status': self.health_status.value,
                'last_check': self.last_health_check.isoformat() if self.last_health_check else None
            },
            'connections': {
                'total': len(self.connections),
                'by_state': {k.value: v for k, v in counts.items()},
                'utilization': self.calculate_utilization()
            },
            'metrics': {
                'total_created': self.total_connections_created,
                'total_destroyed': self.total_connections_destroyed,
                'total_requests': self.total_requests_handled,
                'total_errors': self.total_errors,
                'error_rate': self.total_errors / max(self.total_requests_handled, 1)
            },
            'scaling_recommendation': self.needs_scaling()
        }


@dataclass
class PoolMetrics:
    """Point-in-time metrics for a connection pool."""
    pool_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Connection metrics
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    stale_connections: int = 0
    
    # Performance metrics
    avg_connection_time_ms: float = 0.0
    avg_request_time_ms: float = 0.0
    requests_per_second: float = 0.0
    
    # Resource metrics
    memory_used_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    # Queue metrics
    queue_size: int = 0
    avg_wait_time_ms: float = 0.0
    max_wait_time_ms: float = 0.0
    
    # Error metrics
    error_rate: float = 0.0
    timeout_rate: float = 0.0
    rejection_rate: float = 0.0
    
    def calculate_efficiency_score(self) -> float:
        """Calculate overall efficiency score (0-100)."""
        # Factor in utilization, performance, and errors
        utilization_score = min((self.active_connections / max(self.total_connections, 1)) * 40, 40)
        performance_score = max(0, 40 - (self.avg_request_time_ms / 100))
        error_penalty = self.error_rate * 20
        
        return max(0, utilization_score + performance_score - error_penalty)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pool_id': self.pool_id,
            'timestamp': self.timestamp.isoformat(),
            'connections': {
                'total': self.total_connections,
                'active': self.active_connections,
                'idle': self.idle_connections,
                'stale': self.stale_connections,
                'utilization': (self.active_connections / max(self.total_connections, 1)) * 100
            },
            'performance': {
                'avg_connection_time_ms': self.avg_connection_time_ms,
                'avg_request_time_ms': self.avg_request_time_ms,
                'requests_per_second': self.requests_per_second
            },
            'resources': {
                'memory_mb': self.memory_used_mb,
                'cpu_percent': self.cpu_usage_percent
            },
            'queue': {
                'size': self.queue_size,
                'avg_wait_ms': self.avg_wait_time_ms,
                'max_wait_ms': self.max_wait_time_ms
            },
            'errors': {
                'error_rate': self.error_rate,
                'timeout_rate': self.timeout_rate,
                'rejection_rate': self.rejection_rate
            },
            'efficiency_score': self.calculate_efficiency_score()
        }


@dataclass
class PoolEvent:
    """Event in connection pool lifecycle."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pool_id: str = ""
    connection_id: Optional[str] = None
    event_type: str = ""  # created, destroyed, activated, deactivated, error, scaled
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Event details
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Impact
    severity: str = "info"  # info, warning, error, critical
    affected_connections: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'pool_id': self.pool_id,
            'connection_id': self.connection_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'severity': self.severity,
            'affected_connections': self.affected_connections,
            'metadata': self.metadata
        }


@dataclass
class PoolOptimization:
    """Optimization recommendation for connection pool."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    pool_id: str = ""
    
    # Recommendation details
    title: str = ""
    description: str = ""
    category: str = ""  # sizing, performance, reliability, cost
    priority: str = "medium"  # low, medium, high, critical
    
    # Suggested changes
    suggested_min_size: Optional[int] = None
    suggested_max_size: Optional[int] = None
    suggested_target_size: Optional[int] = None
    suggested_timeout_ms: Optional[int] = None
    
    # Expected impact
    expected_improvement_percent: float = 0.0
    expected_cost_change_percent: float = 0.0
    implementation_effort: str = "medium"  # low, medium, high
    
    # Status
    status: str = "pending"  # pending, approved, implemented, rejected
    created_at: datetime = field(default_factory=datetime.now)
    implemented_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'recommendation_id': self.recommendation_id,
            'pool_id': self.pool_id,
            'details': {
                'title': self.title,
                'description': self.description,
                'category': self.category,
                'priority': self.priority
            },
            'suggestions': {
                'min_size': self.suggested_min_size,
                'max_size': self.suggested_max_size,
                'target_size': self.suggested_target_size,
                'timeout_ms': self.suggested_timeout_ms
            },
            'impact': {
                'improvement_percent': self.expected_improvement_percent,
                'cost_change_percent': self.expected_cost_change_percent,
                'effort': self.implementation_effort
            },
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'implemented_at': self.implemented_at.isoformat() if self.implemented_at else None
        }