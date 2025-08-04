"""
Data models for MCP Server metrics and monitoring.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid


class MCPRequestType(Enum):
    """Types of MCP requests."""
    QUERY = "query"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    AGGREGATE = "aggregate"
    ADMIN = "admin"
    HEALTH = "health"
    INFO = "info"
    CUSTOM = "custom"


class MCPResponseStatus(Enum):
    """MCP response status codes."""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not_found"
    PARTIAL = "partial"


@dataclass
class MCPResourceUsage:
    """Resource usage metrics for MCP Server."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # CPU metrics
    cpu_percent: float = 0.0
    cpu_cores: int = 0
    cpu_threads: int = 0
    
    # Memory metrics
    memory_used_mb: float = 0.0
    memory_total_mb: float = 0.0
    memory_percent: float = 0.0
    heap_used_mb: float = 0.0
    heap_max_mb: float = 0.0
    
    # Network metrics
    network_in_mbps: float = 0.0
    network_out_mbps: float = 0.0
    active_connections: int = 0
    total_connections: int = 0
    
    # Disk metrics
    disk_read_mbps: float = 0.0
    disk_write_mbps: float = 0.0
    disk_usage_gb: float = 0.0
    
    # Thread pool metrics
    thread_pool_size: int = 0
    thread_pool_active: int = 0
    thread_pool_queued: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu': {
                'percent': self.cpu_percent,
                'cores': self.cpu_cores,
                'threads': self.cpu_threads
            },
            'memory': {
                'used_mb': self.memory_used_mb,
                'total_mb': self.memory_total_mb,
                'percent': self.memory_percent,
                'heap_used_mb': self.heap_used_mb,
                'heap_max_mb': self.heap_max_mb
            },
            'network': {
                'in_mbps': self.network_in_mbps,
                'out_mbps': self.network_out_mbps,
                'active_connections': self.active_connections,
                'total_connections': self.total_connections
            },
            'disk': {
                'read_mbps': self.disk_read_mbps,
                'write_mbps': self.disk_write_mbps,
                'usage_gb': self.disk_usage_gb
            },
            'thread_pool': {
                'size': self.thread_pool_size,
                'active': self.thread_pool_active,
                'queued': self.thread_pool_queued
            }
        }


@dataclass
class MCPMethodStats:
    """Statistics for a specific MCP method."""
    method_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    
    # Timing metrics (in milliseconds)
    avg_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    
    # Rate metrics
    calls_per_minute: float = 0.0
    error_rate: float = 0.0
    
    # Data metrics
    avg_request_size_bytes: float = 0.0
    avg_response_size_bytes: float = 0.0
    total_data_processed_mb: float = 0.0
    
    # Recent errors
    recent_errors: List[str] = field(default_factory=list)
    last_error_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method_name': self.method_name,
            'total_calls': self.total_calls,
            'successful_calls': self.successful_calls,
            'failed_calls': self.failed_calls,
            'timing': {
                'avg_ms': self.avg_response_time,
                'min_ms': self.min_response_time if self.min_response_time != float('inf') else None,
                'max_ms': self.max_response_time,
                'p50_ms': self.p50_response_time,
                'p95_ms': self.p95_response_time,
                'p99_ms': self.p99_response_time
            },
            'rates': {
                'calls_per_minute': self.calls_per_minute,
                'error_rate': self.error_rate
            },
            'data': {
                'avg_request_bytes': self.avg_request_size_bytes,
                'avg_response_bytes': self.avg_response_size_bytes,
                'total_mb': self.total_data_processed_mb
            },
            'errors': {
                'recent': self.recent_errors[-5:],  # Last 5 errors
                'last_error_time': self.last_error_time.isoformat() if self.last_error_time else None
            }
        }


@dataclass
class MCPRequest:
    """Represents an MCP request."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    method: str = ""
    request_type: MCPRequestType = MCPRequestType.CUSTOM
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Request details
    params: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    client_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Size metrics
    request_size_bytes: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'method': self.method,
            'request_type': self.request_type.value,
            'timestamp': self.timestamp.isoformat(),
            'client_id': self.client_id,
            'session_id': self.session_id,
            'request_size_bytes': self.request_size_bytes,
            'params': self.params,
            'headers': self.headers
        }


@dataclass
class MCPResponse:
    """Represents an MCP response."""
    request_id: str
    status: MCPResponseStatus = MCPResponseStatus.SUCCESS
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Response details
    response_time_ms: float = 0.0
    response_size_bytes: int = 0
    
    # Result data
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    
    # Processing metrics
    db_query_time_ms: Optional[float] = None
    cache_hit: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'request_id': self.request_id,
            'status': self.status.value,
            'timestamp': self.timestamp.isoformat(),
            'response_time_ms': self.response_time_ms,
            'response_size_bytes': self.response_size_bytes,
            'error': self.error,
            'error_code': self.error_code,
            'processing': {
                'db_query_time_ms': self.db_query_time_ms,
                'cache_hit': self.cache_hit
            }
        }


@dataclass
class MCPSession:
    """Represents an MCP client session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Session metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_data_transferred_mb: float = 0.0
    
    # Connection info
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    protocol_version: Optional[str] = None
    
    # State
    is_active: bool = True
    ended_at: Optional[datetime] = None
    
    def duration_seconds(self) -> float:
        """Get session duration in seconds."""
        end_time = self.ended_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'started_at': self.started_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'duration_seconds': self.duration_seconds(),
            'metrics': {
                'total_requests': self.total_requests,
                'successful_requests': self.successful_requests,
                'failed_requests': self.failed_requests,
                'total_data_mb': self.total_data_transferred_mb
            },
            'connection': {
                'client_ip': self.client_ip,
                'user_agent': self.user_agent,
                'protocol_version': self.protocol_version
            },
            'is_active': self.is_active
        }


@dataclass
class MCPError:
    """Represents an MCP error event."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    error_type: str = ""
    error_message: str = ""
    
    # Context
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    method: Optional[str] = None
    
    # Error details
    stack_trace: Optional[str] = None
    error_code: Optional[str] = None
    severity: str = "error"  # info, warning, error, critical
    
    # Impact
    affected_sessions: List[str] = field(default_factory=list)
    recovery_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'error_type': self.error_type,
            'error_message': self.error_message,
            'context': {
                'request_id': self.request_id,
                'session_id': self.session_id,
                'method': self.method
            },
            'details': {
                'stack_trace': self.stack_trace,
                'error_code': self.error_code,
                'severity': self.severity
            },
            'impact': {
                'affected_sessions': self.affected_sessions,
                'recovery_action': self.recovery_action
            }
        }


@dataclass
class MCPMetrics:
    """Comprehensive MCP Server metrics."""
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Server info
    server_version: Optional[str] = None
    uptime_seconds: float = 0.0
    
    # Current state
    active_sessions: int = 0
    total_sessions: int = 0
    requests_in_flight: int = 0
    
    # Performance metrics
    requests_per_second: float = 0.0
    avg_response_time_ms: float = 0.0
    error_rate: float = 0.0
    
    # Resource usage
    resource_usage: MCPResourceUsage = field(default_factory=MCPResourceUsage)
    
    # Method statistics
    method_stats: Dict[str, MCPMethodStats] = field(default_factory=dict)
    
    # Recent activity
    recent_requests: List[MCPRequest] = field(default_factory=list)
    recent_errors: List[MCPError] = field(default_factory=list)
    
    # Totals
    total_requests: int = 0
    total_errors: int = 0
    total_data_processed_gb: float = 0.0
    
    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_size_mb: float = 0.0
    cache_evictions: int = 0
    
    # Database metrics
    db_connection_pool_size: int = 0
    db_active_connections: int = 0
    db_query_queue_size: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'server': {
                'version': self.server_version,
                'uptime_seconds': self.uptime_seconds,
                'uptime_hours': self.uptime_seconds / 3600
            },
            'current_state': {
                'active_sessions': self.active_sessions,
                'total_sessions': self.total_sessions,
                'requests_in_flight': self.requests_in_flight
            },
            'performance': {
                'requests_per_second': self.requests_per_second,
                'avg_response_time_ms': self.avg_response_time_ms,
                'error_rate': self.error_rate
            },
            'resource_usage': self.resource_usage.to_dict(),
            'method_stats': {
                name: stats.to_dict() 
                for name, stats in self.method_stats.items()
            },
            'totals': {
                'total_requests': self.total_requests,
                'total_errors': self.total_errors,
                'total_data_gb': self.total_data_processed_gb
            },
            'cache': {
                'hit_rate': self.cache_hit_rate,
                'size_mb': self.cache_size_mb,
                'evictions': self.cache_evictions
            },
            'database': {
                'pool_size': self.db_connection_pool_size,
                'active_connections': self.db_active_connections,
                'query_queue_size': self.db_query_queue_size
            }
        }